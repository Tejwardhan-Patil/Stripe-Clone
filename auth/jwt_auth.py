import jwt
import datetime
from flask import request, jsonify
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from backend.src.models.user_model import UserModel 
from backend.src.config.env_config import SECRET_KEY  

# JWT Token Utility Functions
def generate_token(user_id, expires_in=3600):
    """
    Generates a JWT token with user_id and an expiration time.
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def decode_token(token):
    """
    Decodes a JWT token and returns the payload if valid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Invalid token

# Authentication Decorator
def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]  # 'Bearer <token>'
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            payload = decode_token(token)
            if payload is None:
                return jsonify({'message': 'Token is invalid!'}), 401
            current_user = UserModel.query.get(payload['user_id'])  # Fetch user from database
        except Exception as e:
            return jsonify({'message': 'Token is invalid or expired!', 'error': str(e)}), 401

        return f(current_user, *args, **kwargs)
    
    return decorated_function

# JWT Authentication Class
class JWTAuth:
    @staticmethod
    def login(username, password):
        """
        Authenticates user and returns JWT token.
        """
        user = UserModel.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password, password):
            return jsonify({'message': 'Invalid credentials!'}), 401

        token = generate_token(user.id)
        return jsonify({
            'token': token,
            'user_id': user.id,
            'expires_in': 3600
        }), 200

    @staticmethod
    def refresh_token(old_token):
        """
        Refreshes the JWT token.
        """
        payload = decode_token(old_token)
        if not payload:
            return jsonify({'message': 'Invalid or expired token!'}), 401
        
        new_token = generate_token(payload['user_id'])
        return jsonify({
            'token': new_token,
            'expires_in': 3600
        }), 200

    @staticmethod
    def register(username, password, email):
        """
        Registers a new user and returns a JWT token.
        """
        hashed_password = generate_password_hash(password, method='sha256')
        
        # Check if user already exists
        existing_user = UserModel.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'message': 'Username already exists!'}), 400

        new_user = UserModel(username=username, password=hashed_password, email=email)
        new_user.save_to_db()
        
        token = generate_token(new_user.id)
        return jsonify({
            'message': 'User registered successfully!',
            'token': token,
            'user_id': new_user.id,
            'expires_in': 3600
        }), 201

    @staticmethod
    def verify_token(token):
        """
        Verifies the validity of a token.
        """
        payload = decode_token(token)
        if payload:
            return jsonify({'message': 'Token is valid!', 'user_id': payload['user_id']}), 200
        return jsonify({'message': 'Token is invalid or expired!'}), 401


# Routes for Authentication
from flask import Blueprint

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not 'username' in data or not 'password' in data:
        return jsonify({'message': 'Missing credentials!'}), 400

    return JWTAuth.login(data['username'], data['password'])


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not 'username' in data or not 'password' in data or not 'email' in data:
        return jsonify({'message': 'Missing registration details!'}), 400

    return JWTAuth.register(data['username'], data['password'], data['email'])


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    data = request.get_json()
    if not data or not 'token' in data:
        return jsonify({'message': 'Missing token!'}), 400

    return JWTAuth.refresh_token(data['token'])


@auth_bp.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    if not data or not 'token' in data:
        return jsonify({'message': 'Missing token!'}), 400

    return JWTAuth.verify_token(data['token'])


# Helper Function for Unauthorized Access Handling
def unauthorized_response():
    """
    Returns a standard response for unauthorized access.
    """
    return jsonify({'message': 'Unauthorized access!'}), 403

# Usage of JWT-Required Decorator in a Route
@auth_bp.route('/protected', methods=['GET'])
@jwt_required
def protected_route(current_user):
    """
    This is a protected route that requires a valid JWT token.
    """
    return jsonify({'message': 'This is a protected route.', 'user': current_user.username}), 200