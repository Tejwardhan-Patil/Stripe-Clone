from flask import Flask, jsonify, request
from backend.src.middlewares.auth_middleware import auth_middleware
from backend.src.middlewares.validation_middleware import validation_middleware
from backend.src.routes.payment_routes import payment_routes
from backend.src.routes.subscription_routes import subscription_routes
from backend.src.config.database_config import setup_database
from backend.src.config.env_config import load_env_variables
from backend.src.utils.jwt_util import create_jwt_token, decode_jwt_token
from backend.src.utils.email_util import send_email_notification
import logging
from logging.config import dictConfig
import os

app = Flask(__name__)

# Load environment variables
load_env_variables()

# Database setup
setup_database()

# Configure logging
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Stripe Clone API"}), 200

# Register routes for payments
app.register_blueprint(payment_routes, url_prefix='/api/payments')

# Register routes for subscriptions
app.register_blueprint(subscription_routes, url_prefix='/api/subscriptions')

# Middleware for Authentication
@app.before_request
def apply_auth_middleware():
    auth_middleware()

# Middleware for Request Validation
@app.before_request
def apply_validation_middleware():
    validation_middleware()

# Error handling
@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({"error": "Bad request", "message": str(error)}), 400

@app.errorhandler(401)
def unauthorized_error(error):
    return jsonify({"error": "Unauthorized", "message": str(error)}), 401

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found", "message": str(error)}), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred."}), 500

# Endpoint to handle token generation
@app.route('/auth/token', methods=['POST'])
def generate_token():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    token = create_jwt_token({"user_id": user_id})
    return jsonify({"token": token}), 200

# Endpoint to decode a token
@app.route('/auth/verify-token', methods=['POST'])
def verify_token():
    token = request.json.get('token')
    if not token:
        return jsonify({"error": "Token is required"}), 400

    decoded_token = decode_jwt_token(token)
    if decoded_token:
        return jsonify({"message": "Token is valid", "data": decoded_token}), 200
    else:
        return jsonify({"error": "Invalid token"}), 401

# Email notification
@app.route('/notifications/email', methods=['POST'])
def send_email():
    recipient_email = request.json.get('email')
    subject = request.json.get('subject')
    message = request.json.get('message')

    if not recipient_email or not subject or not message:
        return jsonify({"error": "Email, subject, and message are required"}), 400

    send_email_notification(recipient_email, subject, message)
    return jsonify({"message": "Email sent successfully"}), 200

# Payment processing webhook endpoint
@app.route('/webhooks/payment', methods=['POST'])
def payment_webhook():
    payload = request.json
    # Process the incoming webhook data
    logging.info(f"Received webhook: {payload}")
    return jsonify({"message": "Webhook received successfully"}), 200

# Subscription management endpoint
@app.route('/subscriptions/manage', methods=['POST'])
def manage_subscription():
    user_id = request.json.get('user_id')
    action = request.json.get('action')

    if not user_id or not action:
        return jsonify({"error": "User ID and action are required"}), 400

    # Logic for managing subscriptions (cancel, renew)
    if action == 'cancel':
        # Code to cancel the subscription
        logging.info(f"Subscription cancelled for user {user_id}")
        return jsonify({"message": "Subscription cancelled"}), 200
    elif action == 'renew':
        # Code to renew the subscription
        logging.info(f"Subscription renewed for user {user_id}")
        return jsonify({"message": "Subscription renewed"}), 200
    else:
        return jsonify({"error": "Invalid action"}), 400

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    # Start the Flask application
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))