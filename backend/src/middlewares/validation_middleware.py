from functools import wraps
from flask import request, jsonify
import re
from backend.src.utils.jwt_util import decode_token
from backend.src.models.user_model import User
from backend.src.models.payment_model import Payment
from datetime import datetime

# Validation Error Class
class ValidationError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

# Utility Functions for Validation
def is_valid_email(email: str) -> bool:
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email) is not None

def is_valid_currency(currency: str) -> bool:
    supported_currencies = ['USD', 'EUR', 'GBP', 'JPY']
    return currency.upper() in supported_currencies

def is_positive_amount(amount: float) -> bool:
    return amount > 0

def validate_token():
    token = request.headers.get('Authorization')
    if not token:
        raise ValidationError("Authorization token is missing")
    try:
        token = token.split()[1]  # Bearer <token>
        user_data = decode_token(token)
        user = User.find_by_id(user_data['user_id'])
        if not user:
            raise ValidationError("User not found")
        return user
    except Exception as e:
        raise ValidationError(f"Invalid token: {str(e)}")

# Decorator for validating JSON body
def validate_json_body(required_fields: dict):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({"error": "Request must be in JSON format"}), 400

            data = request.get_json()
            for field, field_type in required_fields.items():
                if field not in data:
                    return jsonify({"error": f"'{field}' is required"}), 400
                if not isinstance(data[field], field_type):
                    return jsonify({"error": f"'{field}' must be of type {field_type.__name__}"}), 400
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Decorator for payment validation
def validate_payment_data(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        try:
            if not is_positive_amount(data.get('amount', 0)):
                raise ValidationError("Amount must be greater than zero")
            if not is_valid_currency(data.get('currency', '')):
                raise ValidationError("Invalid currency")
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400
        return f(*args, **kwargs)
    return decorated_function

# Middleware for validating user authentication token
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            user = validate_token()
            request.user = user
        except ValidationError as e:
            return jsonify({"error": str(e)}), 401
        return f(*args, **kwargs)
    return decorated_function

# Middleware for validating email format
def email_format_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        email = data.get('email')
        if not is_valid_email(email):
            return jsonify({"error": "Invalid email format"}), 400
        return f(*args, **kwargs)
    return decorated_function

# Validate that payment method exists in the database
def payment_method_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        payment_method_id = data.get('payment_method_id')
        payment_method = Payment.find_by_id(payment_method_id)
        if not payment_method:
            return jsonify({"error": "Payment method not found"}), 404
        request.payment_method = payment_method
        return f(*args, **kwargs)
    return decorated_function

# Usage with a Flask route
from flask import Flask

app = Flask(__name__)

@app.route('/payments', methods=['POST'])
@token_required
@validate_json_body({
    'amount': (float, int),
    'currency': str,
    'payment_method_id': str
})
@validate_payment_data
@payment_method_required
def create_payment():
    try:
        user = request.user
        payment_method = request.payment_method
        data = request.get_json()
        amount = data['amount']
        currency = data['currency']
        payment = Payment(user_id=user.id, amount=amount, currency=currency, payment_method_id=payment_method.id)
        payment.created_at = datetime.utcnow()
        payment.save()

        # Log payment details in payment history
        return jsonify({"message": "Payment created successfully", "payment_id": payment.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Validations for user registration
@app.route('/register', methods=['POST'])
@validate_json_body({
    'email': str,
    'password': str
})
@email_format_required
def register_user():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']
        new_user = User(email=email, password=password)
        new_user.created_at = datetime.utcnow()
        new_user.save()

        return jsonify({"message": "User registered successfully", "user_id": new_user.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Password validation middleware
def validate_password_strength(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        password = data.get('password')
        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters long"}), 400
        if not re.search(r'[A-Z]', password):
            return jsonify({"error": "Password must contain at least one uppercase letter"}), 400
        if not re.search(r'[0-9]', password):
            return jsonify({"error": "Password must contain at least one digit"}), 400
        return f(*args, **kwargs)
    return decorated_function

@app.route('/change-password', methods=['POST'])
@token_required
@validate_json_body({
    'password': str
})
@validate_password_strength
def change_password():
    try:
        user = request.user
        data = request.get_json()
        new_password = data['password']
        user.password = new_password
        user.save()

        return jsonify({"message": "Password changed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Middleware to check if user exists by email
def user_exists_by_email(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        email = data.get('email')
        user = User.find_by_email(email)
        if user:
            return jsonify({"error": "Email is already in use"}), 409
        return f(*args, **kwargs)
    return decorated_function

@app.route('/reset-password', methods=['POST'])
@validate_json_body({
    'email': str,
    'new_password': str
})
@validate_password_strength
def reset_password():
    try:
        data = request.get_json()
        email = data['email']
        user = User.find_by_email(email)
        if not user:
            return jsonify({"error": "User not found"}), 404
        user.password = data['new_password']
        user.save()

        return jsonify({"message": "Password reset successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500