from flask import Blueprint, request, jsonify
from middlewares.auth_middleware import auth_required
from utils.jwt_util import decode_jwt_token
from models.payment_model import Payment
from config.database_config import db
import subprocess
import stripe
import logging
import json

# Initialize blueprint for payment routes
payment_controller = Blueprint('payment_controller', __name__)

# Initialize logger
logger = logging.getLogger('payment_controller')

# Set Stripe API key
stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"

def run_java_service(class_name, method_name, *args):
    """
    Runs a Java service via subprocess.
    :param class_name: Java class name.
    :param method_name: Method to invoke.
    :param args: Arguments to pass to the Java method.
    :return: Dictionary with results from the Java method.
    """
    try:
        command = ['java', '-cp', 'services/payment_service', class_name, method_name] + list(args)
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            logger.info(f"Java service executed successfully: {result.stdout}")
            return json.loads(result.stdout)
        else:
            logger.error(f"Java service error: {result.stderr}")
            return {'error': 'Java service execution failed.'}
    except Exception as e:
        logger.error(f"Subprocess error: {str(e)}")
        return {'error': 'Internal server error.'}


@payment_controller.route('/create_payment_intent', methods=['POST'])
@auth_required
def create_payment_intent():
    """
    Creates a payment intent using the Java PaymentService.
    """
    try:
        # Get request data
        data = request.get_json()
        amount = data.get('amount')
        currency = data.get('currency', 'usd')

        if not amount or amount <= 0:
            return jsonify({'error': 'Invalid payment amount.'}), 400

        # Call Java service
        result = run_java_service('PaymentService', 'createPaymentIntent', str(amount), currency)

        if 'error' in result:
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        return jsonify({'error': 'Internal server error.'}), 500


@payment_controller.route('/capture_payment', methods=['POST'])
@auth_required
def capture_payment():
    """
    Captures a payment using the Java PaymentService.
    """
    try:
        data = request.get_json()
        payment_intent_id = data.get('payment_intent_id')

        if not payment_intent_id:
            return jsonify({'error': 'Payment intent ID is required.'}), 400

        result = run_java_service('PaymentService', 'capturePayment', payment_intent_id)

        if 'error' in result:
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        return jsonify({'error': 'Internal server error.'}), 500


@payment_controller.route('/refund_payment', methods=['POST'])
@auth_required
def refund_payment():
    """
    Refunds a payment using the Java PaymentService.
    """
    try:
        data = request.get_json()
        payment_intent_id = data.get('payment_intent_id')

        if not payment_intent_id:
            return jsonify({'error': 'Payment intent ID is required.'}), 400

        result = run_java_service('PaymentService', 'refundPayment', payment_intent_id)

        if 'error' in result:
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        return jsonify({'error': 'Internal server error.'}), 500


@payment_controller.route('/webhook', methods=['POST'])
def stripe_webhook():
    """
    Handles Stripe webhooks.
    """
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = "whsec_1234567890abcdef"

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Webhook signature verification failed: {str(e)}")
        return jsonify({'error': 'Signature verification failed'}), 400

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        logger.info(f"PaymentIntent succeeded: {payment_intent['id']}")
        handle_successful_payment(payment_intent)
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        logger.warning(f"PaymentIntent failed: {payment_intent['id']}")
        handle_failed_payment(payment_intent)

    return jsonify({'status': 'success'}), 200


def handle_successful_payment(payment_intent):
    """
    Handles successful payments by updating the database.
    """
    try:
        payment = Payment.query.filter_by(payment_intent_id=payment_intent['id']).first()

        if payment:
            payment.status = 'succeeded'
            db.session.commit()
            logger.info(f"Payment status updated to succeeded for Payment ID: {payment.id}")
        else:
            logger.error(f"PaymentIntent ID: {payment_intent['id']} not found.")
    except Exception as e:
        logger.error(f"Error updating payment status: {str(e)}")


def handle_failed_payment(payment_intent):
    """
    Handles failed payments.
    """
    try:
        payment = Payment.query.filter_by(payment_intent_id=payment_intent['id']).first()

        if payment:
            payment.status = 'failed'
            db.session.commit()
            logger.warning(f"Payment status updated to failed for Payment ID: {payment.id}")
        else:
            logger.error(f"PaymentIntent ID: {payment_intent['id']} not found.")
    except Exception as e:
        logger.error(f"Error updating payment status: {str(e)}")