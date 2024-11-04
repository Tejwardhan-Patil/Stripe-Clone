import stripe
from flask import Flask, request, jsonify, abort
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables for Stripe API keys and email credentials
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Initialize Flask application
app = Flask(__name__)

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('stripe_integration')

# Function to send an email
def send_email(recipient, subject, message):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = recipient
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USERNAME, recipient, msg.as_string())
        server.quit()

        logger.info(f"Email sent to {recipient} with subject '{subject}'")
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")

# Function to create a payment intent
def create_payment_intent(amount, currency="usd"):
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            automatic_payment_methods={
                "enabled": True,
            },
        )
        return payment_intent
    except Exception as e:
        logger.error(f"Error creating payment intent: {str(e)}")
        abort(500, f"Payment intent creation failed: {str(e)}")

# Route to handle payment intent creation
@app.route('/create-payment-intent', methods=['POST'])
def create_payment_intent_route():
    data = request.json
    amount = data.get('amount')
    currency = data.get('currency', 'usd')

    if not amount:
        abort(400, "Amount is required.")

    intent = create_payment_intent(amount, currency)
    return jsonify({
        'clientSecret': intent['client_secret']
    })

# Function to handle webhook events
@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        abort(400, "Invalid payload.")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        abort(400, "Invalid signature.")

    handle_stripe_event(event)
    return jsonify(success=True)

# Function to handle different Stripe event types
def handle_stripe_event(event):
    event_type = event['type']
    data = event['data']['object']

    if event_type == 'payment_intent.succeeded':
        handle_payment_succeeded(data)
    elif event_type == 'payment_intent.payment_failed':
        handle_payment_failed(data)
    elif event_type == 'charge.refunded':
        handle_charge_refunded(data)
    else:
        logger.info(f"Unhandled event type: {event_type}")

# Function to handle successful payment
def handle_payment_succeeded(data):
    payment_id = data['id']
    amount_received = data['amount_received']
    customer_email = data.get('receipt_email')
    logger.info(f"Payment succeeded for ID: {payment_id}, amount: {amount_received}")

    # Log the payment to a file
    with open("payments.log", "a") as log_file:
        log_file.write(f"Payment succeeded - ID: {payment_id}, Amount: {amount_received}\n")

    # Send confirmation email to customer
    if customer_email:
        send_email(
            recipient=customer_email,
            subject="Payment Confirmation",
            message=f"Your payment of ${amount_received / 100:.2f} was successful."
        )

# Function to handle failed payment
def handle_payment_failed(data):
    payment_id = data['id']
    error_message = data['last_payment_error']['message']
    customer_email = data.get('receipt_email')
    logger.info(f"Payment failed for ID: {payment_id}, error: {error_message}")

    # Log the failure to a file
    with open("payments.log", "a") as log_file:
        log_file.write(f"Payment failed - ID: {payment_id}, Error: {error_message}\n")

    # Notify the customer of the failure
    if customer_email:
        send_email(
            recipient=customer_email,
            subject="Payment Failed",
            message=f"Your payment attempt failed due to the following error: {error_message}."
        )

# Function to handle refunded charge
def handle_charge_refunded(data):
    charge_id = data['id']
    refunded_amount = data['amount_refunded']
    customer_email = data.get('receipt_email')
    logger.info(f"Charge refunded for ID: {charge_id}, amount: {refunded_amount}")

    # Log the refund to a file
    with open("payments.log", "a") as log_file:
        log_file.write(f"Charge refunded - ID: {charge_id}, Amount Refunded: {refunded_amount}\n")

    # Notify the customer of the refund
    if customer_email:
        send_email(
            recipient=customer_email,
            subject="Refund Processed",
            message=f"A refund of ${refunded_amount / 100:.2f} has been processed for your payment."
        )

# Function to create a Stripe charge directly
def create_stripe_charge(amount, currency="usd", description=None, source=None):
    try:
        charge = stripe.Charge.create(
            amount=amount,
            currency=currency,
            description=description,
            source=source
        )
        return charge
    except Exception as e:
        logger.error(f"Error creating charge: {str(e)}")
        abort(500, f"Charge creation failed: {str(e)}")

# Route to create a direct charge
@app.route('/create-charge', methods=['POST'])
def create_charge_route():
    data = request.json
    amount = data.get('amount')
    currency = data.get('currency', 'usd')
    description = data.get('description')
    source = data.get('source')

    if not amount or not source:
        abort(400, "Amount and source are required.")

    charge = create_stripe_charge(amount, currency, description, source)
    return jsonify({
        'status': charge['status'],
        'chargeId': charge['id']
    })

# Function to retrieve a payment intent
def retrieve_payment_intent(payment_intent_id):
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return payment_intent
    except Exception as e:
        logger.error(f"Error retrieving payment intent: {str(e)}")
        abort(500, f"Payment intent retrieval failed: {str(e)}")

# Route to retrieve a payment intent
@app.route('/retrieve-payment-intent/<payment_intent_id>', methods=['GET'])
def retrieve_payment_intent_route(payment_intent_id):
    intent = retrieve_payment_intent(payment_intent_id)
    return jsonify({
        'id': intent['id'],
        'amount': intent['amount'],
        'currency': intent['currency'],
        'status': intent['status']
    })

# Function to refund a charge
def refund_charge(charge_id, amount=None):
    try:
        refund = stripe.Refund.create(
            charge=charge_id,
            amount=amount
        )
        return refund
    except Exception as e:
        logger.error(f"Error creating refund: {str(e)}")
        abort(500, f"Refund creation failed: {str(e)}")

# Route to process a refund
@app.route('/refund', methods=['POST'])
def refund_charge_route():
    data = request.json
    charge_id = data.get('chargeId')
    amount = data.get('amount')

    if not charge_id:
        abort(400, "Charge ID is required.")

    refund = refund_charge(charge_id, amount)
    return jsonify({
        'status': refund['status'],
        'refundId': refund['id']
    })

# Run the Flask app
if __name__ == '__main__':
    app.run(port=4242, debug=True)