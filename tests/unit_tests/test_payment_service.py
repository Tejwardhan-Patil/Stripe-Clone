import unittest
import subprocess
import json
from backend.src.models.payment_model import Payment
from backend.src.utils.jwt_util import decode_token
from backend.src.config.database_config import get_database_session
from backend.src.middlewares.auth_middleware import authenticate_request
from decimal import Decimal
import datetime


class TestPaymentService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db_session = get_database_session()

    def setUp(self):
        self.db_session.begin()

    def tearDown(self):
        self.db_session.rollback()

    def call_payment_service(self, payment_details):
        """
        Calls the Java PaymentService using subprocess.
        """
        # Convert Python dictionary to JSON string
        payment_details_json = json.dumps(payment_details)

        # Call the Java PaymentService via subprocess
        process = subprocess.Popen(
            ['java', '-cp', 'backend/src/services/', 'PaymentService', payment_details_json],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout, stderr = process.communicate()

        if process.returncode != 0:
            raise Exception(f"Java service error: {stderr.decode()}")

        return json.loads(stdout.decode())

    def test_successful_payment(self):
        # Simulating successful payment process
        payment_details = {
            'amount': Decimal('100.00'),
            'currency': 'USD',
            'description': 'Test Payment',
            'payment_method': 'credit_card',
            'user_id': 1
        }

        response = self.call_payment_service(payment_details)

        self.assertEqual(response['status'], 'success')
        self.assertEqual(response['amount'], '100.00')
        self.assertEqual(response['currency'], 'USD')

        # Check the DB if the payment record is stored
        saved_payment = self.db_session.query(Payment).filter_by(user_id=1).first()
        self.assertIsNotNone(saved_payment)
        self.assertEqual(saved_payment.amount, Decimal('100.00'))
        self.assertEqual(saved_payment.currency, 'USD')

    def test_failed_payment_due_to_invalid_amount(self):
        # Invalid amount should throw an error
        payment_details = {
            'amount': Decimal('-10.00'),
            'currency': 'USD',
            'description': 'Test Payment',
            'payment_method': 'credit_card',
            'user_id': 1
        }

        with self.assertRaises(ValueError):
            self.call_payment_service(payment_details)

    def test_payment_service_handles_database_failure(self):
        # Simulating payment failure due to database issues
        payment_details = {
            'amount': Decimal('100.00'),
            'currency': 'USD',
            'description': 'Test Payment',
            'payment_method': 'credit_card',
            'user_id': 1
        }

        # Inducing a DB failure by closing the session prematurely
        self.db_session.close()

        with self.assertRaises(Exception):
            self.call_payment_service(payment_details)

    def test_payment_service_uses_stripe_integration(self):
        # Using integration 
        payment_details = {
            'amount': Decimal('50.00'),
            'currency': 'USD',
            'description': 'Test Payment via Stripe',
            'payment_method': 'stripe',
            'user_id': 1
        }

        response = self.call_payment_service(payment_details)
        self.assertEqual(response['status'], 'success')

        saved_payment = self.db_session.query(Payment).filter_by(user_id=1).first()
        self.assertIsNotNone(saved_payment)
        self.assertEqual(saved_payment.amount, Decimal('50.00'))

    def test_payment_service_uses_paypal_integration(self):
        # Using PayPal integration 
        payment_details = {
            'amount': Decimal('75.00'),
            'currency': 'USD',
            'description': 'Test Payment via PayPal',
            'payment_method': 'paypal',
            'user_id': 1
        }

        response = self.call_payment_service(payment_details)
        self.assertEqual(response['status'], 'success')

        saved_payment = self.db_session.query(Payment).filter_by(user_id=1).first()
        self.assertIsNotNone(saved_payment)
        self.assertEqual(saved_payment.amount, Decimal('75.00'))

    def test_successful_refund(self):
        # Simulate a payment to refund
        payment = Payment(
            id=1,
            amount=Decimal('100.00'),
            currency='USD',
            description='Test Payment',
            status='completed',
            user_id=1,
            created_at=datetime.datetime.now()
        )
        self.db_session.add(payment)
        self.db_session.commit()

        # Simulate refund process
        refund_details = {
            'payment_id': 1,
            'refund_amount': Decimal('50.00')
        }

        response = self.call_payment_service(refund_details)
        self.assertEqual(response['status'], 'success')
        self.assertEqual(response['refund_amount'], '50.00')

        # Check if the payment has been refunded
        updated_payment = self.db_session.query(Payment).filter_by(id=1).first()
        self.assertEqual(updated_payment.status, 'refunded')

    def test_refund_failure_due_to_invalid_amount(self):
        # Simulate a payment to refund
        payment = Payment(
            id=1,
            amount=Decimal('100.00'),
            currency='USD',
            description='Test Payment',
            status='completed',
            user_id=1,
            created_at=datetime.datetime.now()
        )
        self.db_session.add(payment)
        self.db_session.commit()

        # Try to refund more than the original amount
        refund_details = {
            'payment_id': 1,
            'refund_amount': Decimal('150.00')
        }

        with self.assertRaises(ValueError):
            self.call_payment_service(refund_details)

    def test_payment_concurrent_requests(self):
        # Simulate concurrent payments (race conditions)
        payment_details_1 = {
            'amount': Decimal('200.00'),
            'currency': 'USD',
            'description': 'Test Payment 1',
            'payment_method': 'credit_card',
            'user_id': 1
        }

        payment_details_2 = {
            'amount': Decimal('300.00'),
            'currency': 'USD',
            'description': 'Test Payment 2',
            'payment_method': 'credit_card',
            'user_id': 1
        }

        response_1 = self.call_payment_service(payment_details_1)
        response_2 = self.call_payment_service(payment_details_2)

        self.assertEqual(response_1['status'], 'success')
        self.assertEqual(response_2['status'], 'success')

        # Ensure both payments are processed correctly
        saved_payment_1 = self.db_session.query(Payment).filter_by(description='Test Payment 1').first()
        saved_payment_2 = self.db_session.query(Payment).filter_by(description='Test Payment 2').first()

        self.assertIsNotNone(saved_payment_1)
        self.assertIsNotNone(saved_payment_2)

    def test_payment_timeout(self):
        # Simulate a slow operation that times out
        payment_details = {
            'amount': Decimal('300.00'),
            'currency': 'USD',
            'description': 'Test Payment Timeout',
            'payment_method': 'credit_card',
            'user_id': 1
        }

        with self.assertRaises(TimeoutError):
            self.call_payment_service(payment_details)


if __name__ == '__main__':
    unittest.main()