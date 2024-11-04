import subprocess
from flask import Blueprint, request, jsonify
from backend.src.models.user_model import User
from backend.src.utils.jwt_util import decode_jwt_token
from backend.src.middlewares.auth_middleware import authenticate_request
from backend.src.middlewares.validation_middleware import validate_subscription_data

subscription_controller = Blueprint('subscription_controller', __name__)

def run_java_subscription_service(method, *args):
    """Executes the Java-based SubscriptionService using subprocess."""
    cmd = ['java', '-cp', 'backend/src/services', 'SubscriptionService', method] + list(args)
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        raise Exception(result.stderr)
    
    return result.stdout.strip()

@subscription_controller.route('/subscriptions', methods=['POST'])
@authenticate_request
@validate_subscription_data
def create_subscription():
    try:
        token = request.headers.get('Authorization')
        user_data = decode_jwt_token(token)
        user = User.query.filter_by(id=user_data['user_id']).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404

        subscription_data = request.json
        subscription_json = run_java_subscription_service('create', str(user.id), str(subscription_data))
        
        return jsonify({'subscription': subscription_json}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscription_controller.route('/subscriptions/<int:subscription_id>', methods=['GET'])
@authenticate_request
def get_subscription(subscription_id):
    try:
        subscription_json = run_java_subscription_service('get', str(subscription_id))
        
        if not subscription_json:
            return jsonify({'error': 'Subscription not found'}), 404

        return jsonify({'subscription': subscription_json}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscription_controller.route('/subscriptions/user/<int:user_id>', methods=['GET'])
@authenticate_request
def get_user_subscriptions(user_id):
    try:
        subscriptions_json = run_java_subscription_service('getUserSubscriptions', str(user_id))
        
        if not subscriptions_json:
            return jsonify({'error': 'No subscriptions found for this user'}), 404

        return jsonify({'subscriptions': subscriptions_json}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscription_controller.route('/subscriptions/<int:subscription_id>', methods=['PUT'])
@authenticate_request
@validate_subscription_data
def update_subscription(subscription_id):
    try:
        subscription_data = request.json
        subscription_json = run_java_subscription_service('update', str(subscription_id), str(subscription_data))

        return jsonify({'subscription': subscription_json}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscription_controller.route('/subscriptions/<int:subscription_id>', methods=['DELETE'])
@authenticate_request
def delete_subscription(subscription_id):
    try:
        run_java_subscription_service('delete', str(subscription_id))
        return jsonify({'message': 'Subscription deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscription_controller.route('/subscriptions/cancel', methods=['POST'])
@authenticate_request
def cancel_subscription():
    try:
        token = request.headers.get('Authorization')
        user_data = decode_jwt_token(token)
        user = User.query.filter_by(id=user_data['user_id']).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404

        subscription_id = request.json.get('subscription_id')
        run_java_subscription_service('cancel', str(user.id), str(subscription_id))

        return jsonify({'message': 'Subscription canceled successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscription_controller.route('/subscriptions/resume', methods=['POST'])
@authenticate_request
def resume_subscription():
    try:
        token = request.headers.get('Authorization')
        user_data = decode_jwt_token(token)
        user = User.query.filter_by(id=user_data['user_id']).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404

        subscription_id = request.json.get('subscription_id')
        run_java_subscription_service('resume', str(user.id), str(subscription_id))

        return jsonify({'message': 'Subscription resumed successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscription_controller.route('/subscriptions/<int:subscription_id>/status', methods=['GET'])
@authenticate_request
def check_subscription_status(subscription_id):
    try:
        status = run_java_subscription_service('checkStatus', str(subscription_id))
        return jsonify({'subscription_status': status}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscription_controller.route('/subscriptions/billing', methods=['POST'])
@authenticate_request
def update_billing_info():
    try:
        token = request.headers.get('Authorization')
        user_data = decode_jwt_token(token)
        user = User.query.filter_by(id=user_data['user_id']).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        billing_info = request.json.get('billing_info')
        if not billing_info:
            return jsonify({'error': 'Billing info not provided'}), 400

        run_java_subscription_service('updateBilling', str(user.id), str(billing_info))

        return jsonify({'message': 'Billing info updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500