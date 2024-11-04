import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import logging
from typing import List
from backend.src.models.user_model import User
from backend.src.config.env_config import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
from backend.src.utils.email_util import validate_email, format_email_content

logging.basicConfig(level=logging.INFO)

class EmailNotificationManager:
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.smtp_user = SMTP_USER
        self.smtp_password = SMTP_PASSWORD

    def send_email(self, recipient: str, subject: str, body: str, attachments: List[str] = None) -> bool:
        """Sends an email notification."""
        if not validate_email(recipient):
            logging.error(f"Invalid email address: {recipient}")
            return False

        try:
            message = MIMEMultipart()
            message["From"] = self.smtp_user
            message["To"] = recipient
            message["Subject"] = subject

            message.attach(MIMEText(body, "html"))

            if attachments:
                for attachment in attachments:
                    with open(attachment, "rb") as file:
                        attach = MIMEApplication(file.read(), Name=attachment.split('/')[-1])
                        attach["Content-Disposition"] = f'attachment; filename="{attachment.split("/")[-1]}"'
                        message.attach(attach)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, recipient, message.as_string())
                logging.info(f"Email sent to {recipient}")

            return True
        except Exception as e:
            logging.error(f"Failed to send email to {recipient}: {str(e)}")
            return False

    def notify_transaction(self, user: User, amount: float, transaction_id: str) -> bool:
        """Send transaction-related email notifications."""
        subject = "Transaction Confirmation"
        body = format_email_content("transaction_email_template.html", user=user, amount=amount, transaction_id=transaction_id)
        
        return self.send_email(user.email, subject, body)

    def notify_subscription(self, user: User, plan_name: str, expiry_date: str) -> bool:
        """Send subscription-related email notifications."""
        subject = "Subscription Confirmation"
        body = format_email_content("subscription_email_template.html", user=user, plan_name=plan_name, expiry_date=expiry_date)
        
        return self.send_email(user.email, subject, body)

    def notify_password_reset(self, user: User, reset_link: str) -> bool:
        """Send password reset email notification."""
        subject = "Password Reset Request"
        body = format_email_content("password_reset_email_template.html", user=user, reset_link=reset_link)

        return self.send_email(user.email, subject, body)

    def notify_invoice(self, user: User, invoice_id: str, amount_due: float, due_date: str, invoice_pdf_path: str) -> bool:
        """Send invoice-related email notifications with PDF attachment."""
        subject = "Invoice Issued"
        body = format_email_content("invoice_email_template.html", user=user, invoice_id=invoice_id, amount_due=amount_due, due_date=due_date)
        
        return self.send_email(user.email, subject, body, attachments=[invoice_pdf_path])

    def notify_fraud_alert(self, user: User, transaction_id: str, risk_score: float) -> bool:
        """Send fraud alert notification to the user."""
        subject = "Suspicious Activity Detected"
        body = format_email_content("fraud_alert_email_template.html", user=user, transaction_id=transaction_id, risk_score=risk_score)
        
        return self.send_email(user.email, subject, body)

    def notify_refund(self, user: User, amount: float, refund_id: str) -> bool:
        """Send refund confirmation email notification."""
        subject = "Refund Processed"
        body = format_email_content("refund_email_template.html", user=user, amount=amount, refund_id=refund_id)
        
        return self.send_email(user.email, subject, body)

# Utility functions

def validate_email(email: str) -> bool:
    """Validates the email address format."""
    import re
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None

def format_email_content(template_path: str, **kwargs) -> str:
    """Formats the email content based on a template and dynamic values."""
    try:
        with open(f"backend/src/templates/{template_path}", "r") as template_file:
            template_content = template_file.read()
        for key, value in kwargs.items():
            template_content = template_content.replace(f"{{{{ {key} }}}}", str(value))
        return template_content
    except Exception as e:
        logging.error(f"Error loading template {template_path}: {str(e)}")
        return ""

# Error handler for email notifications

class EmailNotificationError(Exception):
    """Custom exception for email notification errors."""
    def __init__(self, message: str):
        super().__init__(message)
        logging.error(f"EmailNotificationError: {message}")

# Usage

if __name__ == "__main__":
    email_manager = EmailNotificationManager()
    
    # User
    user = User(id=1, email="person1@website.com", name="Person One")

    # Notify user of a successful transaction
    email_manager.notify_transaction(user, 150.00, "txn_123456789")

    # Notify user of a subscription confirmation
    email_manager.notify_subscription(user, "Pro Plan", "2024-12-31")

    # Notify user of password reset
    email_manager.notify_password_reset(user, "https://website.com/reset?token=abc123")

    # Notify user of an issued invoice
    email_manager.notify_invoice(user, "INV_987654321", 120.00, "2024-09-15", "/invoice.pdf")

    # Notify user of a fraud alert
    email_manager.notify_fraud_alert(user, "txn_987654321", 0.85)

    # Notify user of a refund
    email_manager.notify_refund(user, 100.00, "refund_123456789")