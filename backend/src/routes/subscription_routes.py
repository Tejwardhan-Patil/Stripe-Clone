import subprocess
from flask import Blueprint, request, jsonify
from backend.src.middlewares.auth_middleware import token_required
from backend.src.middlewares.validation_middleware import validate_json
from backend.src.utils.jwt_util import decode_token
from backend.src.models.user_model import User
from backend.src.config.database_config import db

subscription_routes = Blueprint('subscription_routes', __name__)

def execute_subscription_service(command, *args):
    """
    Execute the Java-based SubscriptionService through subprocess.
    command: The service command to execute (create, cancel, renew, etc).
    args: Additional arguments required for the service.
    """
    java_cmd = ['java', '-cp', 'backend/src/services/SubscriptionService.jar', 'SubscriptionService', command] + list(args)
    result = subprocess.run(java_cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(result.stderr)
    
    return result.stdout


@subscription_routes.route('/subscriptions', methods=['POST'])
@token_required
@validate_json(['plan_id', 'start_date', 'payment_method'])
def create_subscription():
    """
    Create a new subscription for an authenticated user
    """
    data = request.get_json()
    user_id = decode_token(request.headers['Authorization'])['user_id']
    
    plan_id = data['plan_id']
    start_date = data['start_date']
    payment_method = data['payment_method']
    
    try:
        output = execute_subscription_service('create', str(user_id), plan_id, start_date, payment_method)
        return jsonify({'message': 'Subscription created successfully', 'output': output}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@subscription_routes.route('/subscriptions', methods=['GET'])
@token_required
def get_user_subscriptions():
    """
    Get all subscriptions for the authenticated user
    """
    user_id = decode_token(request.headers['Authorization'])['user_id']
    
    try:
        output = execute_subscription_service('list', str(user_id))
        return jsonify({'subscriptions': output}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@subscription_routes.route('/subscriptions/<int:subscription_id>', methods=['GET'])
@token_required
def get_subscription_by_id(subscription_id):
    """
    Get details of a specific subscription by subscription_id
    """
    user_id = decode_token(request.headers['Authorization'])['user_id']
    
    try:
        output = execute_subscription_service('get', str(user_id), str(subscription_id))
        return jsonify({'subscription': output}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@subscription_routes.route('/subscriptions/<int:subscription_id>', methods=['PUT'])
@token_required
@validate_json(['plan_id', 'payment_method'])
def update_subscription(subscription_id):
    """
    Update an existing subscription for an authenticated user
    """
    user_id = decode_token(request.headers['Authorization'])['user_id']
    data = request.get_json()
    
    plan_id = data['plan_id']
    payment_method = data['payment_method']
    
    try:
        output = execute_subscription_service('update', str(user_id), str(subscription_id), plan_id, payment_method)
        return jsonify({'message': 'Subscription updated successfully', 'output': output}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@subscription_routes.route('/subscriptions/<int:subscription_id>', methods=['DELETE'])
@token_required
def cancel_subscription(subscription_id):
    """
    Cancel a specific subscription by subscription_id
    """
    user_id = decode_token(request.headers['Authorization'])['user_id']
    
    try:
        output = execute_subscription_service('cancel', str(user_id), str(subscription_id))
        return jsonify({'message': 'Subscription cancelled successfully', 'output': output}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@subscription_routes.route('/subscriptions/renew', methods=['POST'])
@token_required
@validate_json(['subscription_id', 'renewal_date'])
def renew_subscription():
    """
    Renew a subscription for an authenticated user
    """
    data = request.get_json()
    user_id = decode_token(request.headers['Authorization'])['user_id']
    subscription_id = data['subscription_id']
    renewal_date = data['renewal_date']
    
    try:
        output = execute_subscription_service('renew', str(user_id), str(subscription_id), renewal_date)
        return jsonify({'message': 'Subscription renewed successfully', 'output': output}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@subscription_routes.route('/subscriptions/status/<int:subscription_id>', methods=['GET'])
@token_required
def check_subscription_status(subscription_id):
    """
    Check the current status of a subscription (active, canceled, etc.)
    """
    user_id = decode_token(request.headers['Authorization'])['user_id']
    
    try:
        output = execute_subscription_service('status', str(user_id), str(subscription_id))
        return jsonify({'status': output}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@subscription_routes.route('/subscriptions/upcoming_invoice/<int:subscription_id>', methods=['GET'])
@token_required
def get_upcoming_invoice(subscription_id):
    """
    Get the upcoming invoice for a subscription
    """
    user_id = decode_token(request.headers['Authorization'])['user_id']
    
    try:
        output = execute_subscription_service('invoice', str(user_id), str(subscription_id))
        return jsonify({'upcoming_invoice': output}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500