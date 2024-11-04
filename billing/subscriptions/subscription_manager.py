from datetime import datetime, timedelta
from backend.src.models.user_model import UserModel
from backend.src.models.payment_model import PaymentModel
from payment_processing.payment_gateways.stripe_integration import StripeAPI
from billing.invoices.invoice_generator import InvoiceGenerator
from billing.tax.tax_calculator import TaxCalculator
from backend.src.utils.email_util import send_subscription_email
from backend.src.utils.jwt_util import generate_jwt_token

class SubscriptionManager:
    def __init__(self):
        self.stripe_api = StripeAPI()
        self.invoice_generator = InvoiceGenerator()
        self.tax_calculator = TaxCalculator()

    def create_subscription(self, user_id, plan_id, payment_method):
        user = UserModel.find_by_id(user_id)
        if not user:
            raise Exception(f"User with ID {user_id} not found")
        
        # Charge payment method and create a subscription with Stripe
        stripe_subscription = self.stripe_api.create_subscription(user.stripe_customer_id, plan_id, payment_method)

        # Generate an invoice for the first billing cycle
        invoice = self.invoice_generator.generate_invoice(user_id, stripe_subscription['id'], plan_id)
        
        # Apply tax to the invoice
        tax = self.tax_calculator.calculate_tax(user.billing_address, invoice['total'])
        invoice['total'] += tax

        # Save subscription details
        new_subscription = PaymentModel(
            user_id=user_id,
            plan_id=plan_id,
            stripe_subscription_id=stripe_subscription['id'],
            status=stripe_subscription['status'],
            next_billing_date=datetime.now() + timedelta(days=30),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        new_subscription.save()

        # Send email confirmation to user
        send_subscription_email(user.email, "Subscription Created", invoice)

        return new_subscription

    def cancel_subscription(self, user_id, subscription_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            raise Exception(f"User with ID {user_id} not found")

        subscription = PaymentModel.find_by_id(subscription_id)
        if not subscription or subscription.user_id != user_id:
            raise Exception(f"Subscription with ID {subscription_id} not found for user {user_id}")
        
        # Cancel the subscription via Stripe API
        canceled_subscription = self.stripe_api.cancel_subscription(subscription.stripe_subscription_id)

        # Update the subscription status in the database
        subscription.status = canceled_subscription['status']
        subscription.updated_at = datetime.now()
        subscription.save()

        # Send cancellation email to user
        send_subscription_email(user.email, "Subscription Cancelled", canceled_subscription)

        return subscription

    def update_subscription(self, user_id, subscription_id, new_plan_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            raise Exception(f"User with ID {user_id} not found")
        
        subscription = PaymentModel.find_by_id(subscription_id)
        if not subscription or subscription.user_id != user_id:
            raise Exception(f"Subscription with ID {subscription_id} not found for user {user_id}")

        # Update the subscription via Stripe API
        updated_subscription = self.stripe_api.update_subscription(subscription.stripe_subscription_id, new_plan_id)

        # Update the subscription in the database
        subscription.plan_id = new_plan_id
        subscription.updated_at = datetime.now()
        subscription.save()

        # Send email confirmation of the update
        send_subscription_email(user.email, "Subscription Updated", updated_subscription)

        return subscription

    def retrieve_subscription(self, user_id, subscription_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            raise Exception(f"User with ID {user_id} not found")
        
        subscription = PaymentModel.find_by_id(subscription_id)
        if not subscription or subscription.user_id != user_id:
            raise Exception(f"Subscription with ID {subscription_id} not found for user {user_id}")
        
        return subscription

    def list_active_subscriptions(self, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            raise Exception(f"User with ID {user_id} not found")
        
        # Fetch active subscriptions from the database
        active_subscriptions = PaymentModel.query.filter_by(user_id=user_id, status="active").all()

        return active_subscriptions

    def handle_failed_payment(self, user_id, subscription_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            raise Exception(f"User with ID {user_id} not found")
        
        subscription = PaymentModel.find_by_id(subscription_id)
        if not subscription or subscription.user_id != user_id:
            raise Exception(f"Subscription with ID {subscription_id} not found for user {user_id}")

        # Mark the subscription as failed in the database
        subscription.status = "failed"
        subscription.updated_at = datetime.now()
        subscription.save()

        # Send email notification to the user about the failed payment
        send_subscription_email(user.email, "Payment Failed", subscription)

        return subscription

    def renew_subscription(self, subscription_id):
        subscription = PaymentModel.find_by_id(subscription_id)
        if not subscription:
            raise Exception(f"Subscription with ID {subscription_id} not found")

        if subscription.status != "active":
            raise Exception("Cannot renew a subscription that is not active")
        
        user = UserModel.find_by_id(subscription.user_id)
        if not user:
            raise Exception(f"User with ID {subscription.user_id} not found")

        # Charge the user's payment method through Stripe
        renewal = self.stripe_api.renew_subscription(subscription.stripe_subscription_id)

        # Update next billing date
        subscription.next_billing_date = datetime.now() + timedelta(days=30)
        subscription.updated_at = datetime.now()
        subscription.save()

        # Generate a new invoice
        invoice = self.invoice_generator.generate_invoice(subscription.user_id, subscription.stripe_subscription_id, subscription.plan_id)
        
        # Apply tax to the invoice
        tax = self.tax_calculator.calculate_tax(user.billing_address, invoice['total'])
        invoice['total'] += tax

        # Send email confirmation for the renewal
        send_subscription_email(user.email, "Subscription Renewed", invoice)

        return renewal

    def process_webhook_event(self, event_data):
        event_type = event_data['type']

        if event_type == 'invoice.payment_failed':
            self.handle_failed_payment(event_data['data']['object']['customer'], event_data['data']['object']['subscription'])

        elif event_type == 'invoice.payment_succeeded':
            subscription_id = event_data['data']['object']['subscription']
            subscription = PaymentModel.find_by_stripe_id(subscription_id)
            subscription.status = "active"
            subscription.next_billing_date = datetime.now() + timedelta(days=30)
            subscription.save()

        elif event_type == 'customer.subscription.deleted':
            subscription_id = event_data['data']['object']['id']
            subscription = PaymentModel.find_by_stripe_id(subscription_id)
            subscription.status = "canceled"
            subscription.save()

        else:
            raise Exception(f"Unhandled event type: {event_type}")