import os
import requests
from typing import Dict, List
from backend.src.models.user_model import User
from backend.src.models.payment_model import Payment
from backend.src.config.env_config import get_env_variable

class SMSService:
    def __init__(self):
        self.api_key = get_env_variable("SMS_API_KEY")
        self.api_url = get_env_variable("SMS_API_URL")
        self.sender_number = get_env_variable("SMS_SENDER_NUMBER")

    def send_sms(self, recipient_number: str, message: str) -> bool:
        payload = {
            "to": recipient_number,
            "from": self.sender_number,
            "body": message
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(self.api_url, json=payload, headers=headers)
            if response.status_code == 200:
                return True
            return False
        except requests.RequestException as e:
            print(f"Failed to send SMS: {e}")
            return False

class NotificationManager:
    def __init__(self, sms_service: SMSService):
        self.sms_service = sms_service

    def notify_user_of_payment(self, user: User, payment: Payment) -> None:
        message = f"Hello {user.first_name}, your payment of {payment.amount} {payment.currency} was successful. Thank you!"
        self.sms_service.send_sms(user.phone_number, message)

    def notify_subscription_renewal(self, user: User, plan_name: str, renewal_date: str) -> None:
        message = f"Dear {user.first_name}, your subscription to {plan_name} will renew on {renewal_date}. Ensure you have sufficient balance."
        self.sms_service.send_sms(user.phone_number, message)

    def send_generic_notification(self, users: List[User], message: str) -> None:
        for user in users:
            self.sms_service.send_sms(user.phone_number, message)

class AlertService:
    def __init__(self, notification_manager: NotificationManager):
        self.notification_manager = notification_manager

    def send_failed_payment_alert(self, user: User, payment: Payment) -> None:
        message = f"Hello {user.first_name}, your payment of {payment.amount} {payment.currency} failed. Please update your payment method."
        self.notification_manager.sms_service.send_sms(user.phone_number, message)

    def send_fraud_alert(self, user: User, transaction_id: str) -> None:
        message = f"Alert: Suspicious activity detected in transaction {transaction_id}. Please contact support."
        self.notification_manager.sms_service.send_sms(user.phone_number, message)

class AdminNotificationService:
    def __init__(self, sms_service: SMSService, admin_phone_numbers: List[str]):
        self.sms_service = sms_service
        self.admin_phone_numbers = admin_phone_numbers

    def notify_admin_of_system_error(self, error_message: str) -> None:
        message = f"System Alert: An error occurred - {error_message}"
        for admin_number in self.admin_phone_numbers:
            self.sms_service.send_sms(admin_number, message)

    def notify_admin_of_high_risk_transaction(self, transaction_id: str, risk_score: int) -> None:
        message = f"High-Risk Transaction Alert: Transaction {transaction_id} has a risk score of {risk_score}. Immediate attention required."
        for admin_number in self.admin_phone_numbers:
            self.sms_service.send_sms(admin_number, message)

def send_payment_success_sms(user_id: int, payment_id: int):
    user = User.get_by_id(user_id)
    payment = Payment.get_by_id(payment_id)
    if user and payment:
        sms_service = SMSService()
        notification_manager = NotificationManager(sms_service)
        notification_manager.notify_user_of_payment(user, payment)

def send_subscription_renewal_sms(user_id: int, plan_name: str, renewal_date: str):
    user = User.get_by_id(user_id)
    if user:
        sms_service = SMSService()
        notification_manager = NotificationManager(sms_service)
        notification_manager.notify_subscription_renewal(user, plan_name, renewal_date)

def send_failed_payment_alert(user_id: int, payment_id: int):
    user = User.get_by_id(user_id)
    payment = Payment.get_by_id(payment_id)
    if user and payment:
        sms_service = SMSService()
        alert_service = AlertService(NotificationManager(sms_service))
        alert_service.send_failed_payment_alert(user, payment)

def send_fraud_alert(user_id: int, transaction_id: str):
    user = User.get_by_id(user_id)
    if user:
        sms_service = SMSService()
        alert_service = AlertService(NotificationManager(sms_service))
        alert_service.send_fraud_alert(user, transaction_id)

def notify_admin_of_system_error(error_message: str):
    admin_numbers = get_env_variable("ADMIN_PHONE_NUMBERS").split(",")
    sms_service = SMSService()
    admin_service = AdminNotificationService(sms_service, admin_numbers)
    admin_service.notify_admin_of_system_error(error_message)

def notify_admin_of_high_risk_transaction(transaction_id: str, risk_score: int):
    admin_numbers = get_env_variable("ADMIN_PHONE_NUMBERS").split(",")
    sms_service = SMSService()
    admin_service = AdminNotificationService(sms_service, admin_numbers)
    admin_service.notify_admin_of_high_risk_transaction(transaction_id, risk_score)

if __name__ == "__main__":
    # Usage
    send_payment_success_sms(user_id=123, payment_id=456)
    send_subscription_renewal_sms(user_id=123, plan_name="Pro Plan", renewal_date="2024-10-20")
    send_failed_payment_alert(user_id=123, payment_id=789)
    send_fraud_alert(user_id=123, transaction_id="TXN123456")
    notify_admin_of_system_error("Database connection failed")
    notify_admin_of_high_risk_transaction(transaction_id="TXN987654", risk_score=85)