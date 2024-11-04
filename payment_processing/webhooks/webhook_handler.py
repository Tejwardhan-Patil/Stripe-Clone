import json
import hmac
import hashlib
from flask import Blueprint, request, jsonify
from payment_processing.payment_gateways.stripe_integration import StripeWebhookProcessor
from payment_processing.payment_gateways.paypal_integration import PayPalWebhookProcessor
import logging

# Initialize the logger
logging.basicConfig(filename='webhook_events.log', level=logging.INFO)

webhook_handler = Blueprint('webhook_handler', __name__)

# Define webhook routes for Stripe and PayPal
@webhook_handler.route('/webhook/stripe', methods=['POST'])
def handle_stripe_webhook():
    signature = request.headers.get('Stripe-Signature')
    payload = request.get_data(as_text=True)

    # Verify Stripe signature
    if not validate_stripe_signature(payload, signature):
        logging.error("Invalid Stripe signature")
        return jsonify({"error": "Invalid signature"}), 400

    try:
        event = json.loads(payload)
        # Process Stripe webhook event
        response = StripeWebhookProcessor.process_event(event)
        logging.info(f'Stripe webhook processed successfully: {event}')
        return jsonify(response), 200
    except Exception as e:
        logging.error(f'Stripe webhook processing failed: {str(e)}')
        return jsonify({"error": "Webhook processing failed"}), 500


@webhook_handler.route('/webhook/paypal', methods=['POST'])
def handle_paypal_webhook():
    transmission_id = request.headers.get('PayPal-Transmission-Id')
    transmission_sig = request.headers.get('PayPal-Transmission-Sig')
    cert_url = request.headers.get('PayPal-Cert-Url')
    auth_algo = request.headers.get('PayPal-Auth-Algo')
    webhook_id = 'PAYPAL_WEBHOOK_ID'

    payload = request.get_data(as_text=True)

    # Verify PayPal signature
    if not validate_paypal_signature(transmission_id, transmission_sig, cert_url, auth_algo, payload, webhook_id):
        logging.error("Invalid PayPal signature")
        return jsonify({"error": "Invalid signature"}), 400

    try:
        event = json.loads(payload)
        # Process PayPal webhook event
        response = PayPalWebhookProcessor.process_event(event)
        logging.info(f'PayPal webhook processed successfully: {event}')
        return jsonify(response), 200
    except Exception as e:
        logging.error(f'PayPal webhook processing failed: {str(e)}')
        return jsonify({"error": "Webhook processing failed"}), 500


def validate_stripe_signature(payload, signature):
    endpoint_secret = 'STRIPE_ENDPOINT_SECRET'
    try:
        computed_signature = hmac.new(
            endpoint_secret.encode('utf-8'),
            payload.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(computed_signature, signature)
    except Exception as e:
        logging.error(f'Stripe signature validation failed: {str(e)}')
        return False


def validate_paypal_signature(transmission_id, transmission_sig, cert_url, auth_algo, payload, webhook_id):
    # PayPal signature verification logic
    try:
        computed_signature = hmac.new(
            webhook_id.encode('utf-8'),
            transmission_id.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(computed_signature, transmission_sig)
    except Exception as e:
        logging.error(f'PayPal signature validation failed: {str(e)}')
        return False