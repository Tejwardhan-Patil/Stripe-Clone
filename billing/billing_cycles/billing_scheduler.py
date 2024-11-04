import datetime
import time
import logging
from threading import Thread
from sqlalchemy import create_engine, text
from billing.invoices.invoice_generator import InvoiceGenerator
from billing.tax.tax_calculator import TaxCalculator
from database.models.user import User
from database.config.db_connections import DBSession

# Configure logging for billing scheduler
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BillingScheduler")

class BillingScheduler:
    def __init__(self, interval=86400):
        """
        Initialize the BillingScheduler with a specified interval for checking subscriptions.
        By default, it runs every 24 hours (86400 seconds).
        """
        self.interval = interval
        self.db_session = DBSession()
        self.invoice_generator = InvoiceGenerator()
        self.tax_calculator = TaxCalculator()

    def start_scheduler(self):
        """
        Start the billing scheduler to run as a background thread.
        This method initializes a background thread that checks for subscription billing cycles.
        """
        logger.info("Starting Billing Scheduler")
        scheduler_thread = Thread(target=self.run, daemon=True)
        scheduler_thread.start()

    def run(self):
        """
        The main loop that checks and processes subscriptions for billing.
        This method runs indefinitely, checking for active subscriptions and generating invoices.
        """
        while True:
            logger.info("Checking for subscriptions that need billing.")
            try:
                self.process_billing_cycles()
            except Exception as e:
                logger.error(f"An error occurred during billing cycle processing: {e}")
            time.sleep(self.interval)

    def process_billing_cycles(self):
        """
        Processes billing cycles by fetching all active subscriptions from the database.
        It generates an invoice for any subscription whose next billing date is today or earlier.
        """
        current_date = datetime.datetime.utcnow().date()
        subscriptions = self.get_active_subscriptions(current_date)

        for subscription in subscriptions:
            user_id = subscription['user_id']
            subscription_id = subscription['id']
            logger.info(f"Processing subscription {subscription_id} for user {user_id}.")
            try:
                self.generate_invoice(subscription)
                self.update_billing_date(subscription)
            except Exception as e:
                logger.error(f"Failed to process subscription {subscription_id}: {e}")

    def get_active_subscriptions(self, current_date):
        """
        Retrieves all active subscriptions from the database that require billing.
        """
        try:
            query = text("""
                SELECT id, user_id, plan_price, next_billing_date 
                FROM subscriptions 
                WHERE is_active = true AND next_billing_date <= :current_date
            """)
            return self.db_session.execute(query, {'current_date': current_date}).fetchall()
        except Exception as e:
            logger.error(f"Error fetching active subscriptions: {e}")
            return []

    def generate_invoice(self, subscription):
        """
        Generate an invoice for a specific subscription.
        This involves calculating the total cost, applying taxes, and saving the invoice.
        """
        try:
            user_id = subscription['user_id']
            plan_price = subscription['plan_price']
            total_cost_with_tax = self.tax_calculator.calculate_tax(user_id, plan_price)

            # Generate and save the invoice
            invoice = self.invoice_generator.create_invoice(user_id, subscription['id'], total_cost_with_tax)
            self.save_invoice(invoice)

            logger.info(f"Generated invoice for user {user_id}, subscription {subscription['id']}")
        except Exception as e:
            logger.error(f"Error generating invoice for subscription {subscription['id']}: {e}")

    def update_billing_date(self, subscription):
        """
        Update the next billing date of the subscription after processing the current cycle.
        """
        next_billing_date = subscription['next_billing_date'] + datetime.timedelta(days=30)
        try:
            query = text("""
                UPDATE subscriptions 
                SET next_billing_date = :next_billing_date 
                WHERE id = :subscription_id
            """)
            self.db_session.execute(query, {'next_billing_date': next_billing_date, 'subscription_id': subscription['id']})
            self.db_session.commit()
            logger.info(f"Updated next billing date for subscription {subscription['id']}")
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to update billing date for subscription {subscription['id']}: {e}")

    def save_invoice(self, invoice):
        """
        Save the generated invoice to the database.
        """
        try:
            query = text("""
                INSERT INTO invoices (user_id, subscription_id, total_cost, created_at) 
                VALUES (:user_id, :subscription_id, :total_cost, :created_at)
            """)
            self.db_session.execute(query, {
                'user_id': invoice.user_id,
                'subscription_id': invoice.subscription_id,
                'total_cost': invoice.total_cost,
                'created_at': invoice.created_at
            })
            self.db_session.commit()
            logger.info(f"Invoice {invoice.id} saved successfully.")
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to save invoice: {e}")

    def stop_scheduler(self):
        """
        Stops the billing scheduler gracefully by setting the stop event.
        """
        logger.info("Stopping Billing Scheduler")
        self.stop_event.set()

if __name__ == "__main__":
    # Initialize and start the billing scheduler
    billing_scheduler = BillingScheduler()
    billing_scheduler.start_scheduler()