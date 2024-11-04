import paypalrestsdk
import logging
from flask import Flask, request, jsonify
from backend.src.config.env_config import get_env_variable
from backend.src.models.payment_model import Payment
from backend.src.utils.jwt_util import decode_token

# Initialize the PayPal SDK
paypalrestsdk.configure({
    'mode': get_env_variable('PAYPAL_MODE'),  # 'sandbox' or 'live'
    'client_id': get_env_variable('PAYPAL_CLIENT_ID'),
    'client_secret': get_env_variable('PAYPAL_CLIENT_SECRET')
})

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# PayPal payment creation
@app.route('/api/payments/paypal/create', methods=['POST'])
def create_paypal_payment():
    try:
        data = request.json
        user_token = request.headers.get('Authorization')
        user_data = decode_token(user_token)

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": str(data['amount']),
                    "currency": data['currency']
                },
                "description": "Payment for transaction by user: {}".format(user_data['user_id'])
            }],
            "redirect_urls": {
                "return_url": data['return_url'],
                "cancel_url": data['cancel_url']
            }
        })

        if payment.create():
            logging.info(f"PayPal Payment created successfully for user {user_data['user_id']}")
            return jsonify({'paymentID': payment.id}), 201
        else:
            logging.error(f"PayPal Payment creation failed: {payment.error}")
            return jsonify({'error': 'Payment creation failed'}), 500

    except Exception as e:
        logging.error(f"Error creating PayPal payment: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# PayPal payment execution
@app.route('/api/payments/paypal/execute', methods=['POST'])
def execute_paypal_payment():
    try:
        data = request.json
        payment_id = data['paymentID']
        payer_id = data['payerID']

        payment = paypalrestsdk.Payment.find(payment_id)

        if payment.execute({"payer_id": payer_id}):
            logging.info(f"Payment executed successfully: {payment_id}")
            # Save payment details to the database
            Payment.create({
                'user_id': data['user_id'],
                'payment_id': payment_id,
                'payment_method': 'PayPal',
                'amount': payment.transactions[0].amount.total,
                'currency': payment.transactions[0].amount.currency,
                'status': 'completed'
            })
            return jsonify({'status': 'success'}), 200
        else:
            logging.error(f"Payment execution failed: {payment.error}")
            return jsonify({'error': 'Payment execution failed'}), 500

    except Exception as e:
        logging.error(f"Error executing PayPal payment: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# Refund a PayPal payment
@app.route('/api/payments/paypal/refund', methods=['POST'])
def refund_paypal_payment():
    try:
        data = request.json
        payment_id = data['paymentID']
        refund_amount = data['refund_amount']

        payment = paypalrestsdk.Payment.find(payment_id)
        sale = payment.transactions[0].related_resources[0].sale

        refund = sale.refund({
            "amount": {
                "total": str(refund_amount),
                "currency": payment.transactions[0].amount.currency
            }
        })

        if refund.success():
            logging.info(f"Refund successful for payment: {payment_id}")
            # Update payment status in the database
            Payment.update(payment_id, {'status': 'refunded'})
            return jsonify({'status': 'refund_successful'}), 200
        else:
            logging.error(f"Refund failed: {refund.error}")
            return jsonify({'error': 'Refund failed'}), 500

    except Exception as e:
        logging.error(f"Error processing PayPal refund: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# Webhook for PayPal events
@app.route('/api/payments/paypal/webhook', methods=['POST'])
def paypal_webhook():
    try:
        event_body = request.get_json()
        event_type = event_body['event_type']

        if event_type == 'PAYMENT.SALE.COMPLETED':
            payment_id = event_body['resource']['id']
            logging.info(f"Payment completed: {payment_id}")
            Payment.update(payment_id, {'status': 'completed'})
        elif event_type == 'PAYMENT.SALE.REFUNDED':
            payment_id = event_body['resource']['sale_id']
            logging.info(f"Payment refunded: {payment_id}")
            Payment.update(payment_id, {'status': 'refunded'})
        else:
            logging.warning(f"Unhandled event type: {event_type}")

        return jsonify({'status': 'Webhook received'}), 200

    except Exception as e:
        logging.error(f"Error handling PayPal webhook: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# Helper function to verify webhook signatures
def verify_webhook_signature(headers, body):
    signature = headers.get('PayPal-Transmission-Sig')
    transmission_id = headers.get('PayPal-Transmission-Id')
    cert_url = headers.get('PayPal-Cert-Url')
    auth_algo = headers.get('PayPal-Auth-Algo')
    transmission_time = headers.get('PayPal-Transmission-Time')

    webhook_event = paypalrestsdk.WebhookEvent.verify({
        "transmission_id": transmission_id,
        "transmission_time": transmission_time,
        "cert_url": cert_url,
        "auth_algo": auth_algo,
        "transmission_sig": signature,
        "webhook_id": get_env_variable('PAYPAL_WEBHOOK_ID'),
        "webhook_event": body
    })

    return webhook_event['verification_status'] == 'SUCCESS'


# Webhook listener route
@app.route('/api/payments/paypal/verify-webhook', methods=['POST'])
def verify_webhook():
    try:
        headers = request.headers
        body = request.data.decode('utf-8')

        if verify_webhook_signature(headers, body):
            logging.info("Webhook verified successfully")
            return jsonify({'status': 'verified'}), 200
        else:
            logging.error("Webhook verification failed")
            return jsonify({'error': 'Webhook verification failed'}), 400

    except Exception as e:
        logging.error(f"Error verifying PayPal webhook: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)