from flask import Blueprint, request, jsonify
from backend.src.controllers.payment_controller import PaymentController
from backend.src.middlewares.auth_middleware import token_required
from backend.src.middlewares.validation_middleware import validate_request
from backend.src.models.payment_model import PaymentModel
from backend.src.utils.jwt_util import decode_token
from backend.src.config.database_config import db_session

payment_routes = Blueprint('payment_routes', __name__)
payment_controller = PaymentController()

# Route for processing payments
@payment_routes.route('/api/v1/payment', methods=['POST'])
@token_required
@validate_request
def process_payment(current_user):
    try:
        data = request.get_json()
        payment_method = data.get('payment_method')
        amount = data.get('amount')

        if not payment_method or not amount:
            return jsonify({'error': 'Missing payment method or amount'}), 400

        # Process the payment using the payment controller
        payment = payment_controller.process_payment(current_user, payment_method, amount)

        return jsonify({
            'status': 'success',
            'message': 'Payment processed successfully',
            'payment_id': payment.payment_id,
            'amount': payment.amount,
            'status': payment.status
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route for fetching payment history
@payment_routes.route('/api/v1/payment/history', methods=['GET'])
@token_required
def payment_history(current_user):
    try:
        # Fetch the user's payment history from the database
        payments = PaymentModel.query.filter_by(user_id=current_user.id).all()
        if not payments:
            return jsonify({'message': 'No payment history found'}), 404

        payment_list = []
        for payment in payments:
            payment_list.append({
                'payment_id': payment.payment_id,
                'amount': payment.amount,
                'status': payment.status,
                'created_at': payment.created_at
            })

        return jsonify({'status': 'success', 'payments': payment_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route for initiating a refund
@payment_routes.route('/api/v1/payment/refund', methods=['POST'])
@token_required
@validate_request
def initiate_refund(current_user):
    try:
        data = request.get_json()
        payment_id = data.get('payment_id')

        if not payment_id:
            return jsonify({'error': 'Payment ID is required'}), 400

        # Check if the payment exists
        payment = PaymentModel.query.filter_by(payment_id=payment_id, user_id=current_user.id).first()

        if not payment:
            return jsonify({'error': 'Payment not found'}), 404

        # Process the refund using the payment controller
        refund = payment_controller.process_refund(payment)

        return jsonify({
            'status': 'success',
            'message': 'Refund initiated successfully',
            'refund_id': refund.refund_id,
            'payment_id': refund.payment_id,
            'refund_status': refund.status
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route for verifying a payment using Stripe Webhooks
@payment_routes.route('/api/v1/payment/webhook', methods=['POST'])
def stripe_webhook():
    try:
        data = request.get_json()
        event_type = data.get('type')

        if not event_type:
            return jsonify({'error': 'Invalid webhook data'}), 400

        # Process the event based on its type
        if event_type == 'payment_intent.succeeded':
            payment_intent = data['data']['object']
            payment_controller.handle_successful_payment(payment_intent)

        elif event_type == 'payment_intent.payment_failed':
            payment_intent = data['data']['object']
            payment_controller.handle_failed_payment(payment_intent)

        return jsonify({'status': 'success', 'message': 'Webhook received'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route for updating payment details (Admin access only)
@payment_routes.route('/api/v1/payment/update', methods=['PUT'])
@token_required
def update_payment(current_user):
    try:
        if not current_user.is_admin:
            return jsonify({'error': 'Unauthorized access'}), 403

        data = request.get_json()
        payment_id = data.get('payment_id')
        status = data.get('status')

        if not payment_id or not status:
            return jsonify({'error': 'Missing payment ID or status'}), 400

        # Find the payment and update its status
        payment = PaymentModel.query.filter_by(payment_id=payment_id).first()

        if not payment:
            return jsonify({'error': 'Payment not found'}), 404

        payment.status = status
        db_session.commit()

        return jsonify({'status': 'success', 'message': 'Payment updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route for verifying JWT tokens (optional)
@payment_routes.route('/api/v1/payment/verify-token', methods=['POST'])
@token_required
def verify_token(current_user):
    try:
        return jsonify({
            'status': 'success',
            'message': 'Token is valid',
            'user_id': current_user.id
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route for handling payment cancellation
@payment_routes.route('/api/v1/payment/cancel', methods=['POST'])
@token_required
def cancel_payment(current_user):
    try:
        data = request.get_json()
        payment_id = data.get('payment_id')

        if not payment_id:
            return jsonify({'error': 'Payment ID is required'}), 400

        # Check if the payment exists
        payment = PaymentModel.query.filter_by(payment_id=payment_id, user_id=current_user.id).first()

        if not payment:
            return jsonify({'error': 'Payment not found'}), 404

        # Cancel the payment using the payment controller
        cancellation = payment_controller.cancel_payment(payment)

        return jsonify({
            'status': 'success',
            'message': 'Payment cancelled successfully',
            'payment_id': cancellation.payment_id,
            'status': cancellation.status
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500