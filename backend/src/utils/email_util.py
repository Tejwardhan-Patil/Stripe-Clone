import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import logging
from typing import List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailUtil:
    def __init__(self, smtp_server: str, smtp_port: int, smtp_username: str, smtp_password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password

    def send_email(
        self, 
        subject: str, 
        body: str, 
        recipients: List[str], 
        sender: str, 
        cc: Optional[List[str]] = None, 
        bcc: Optional[List[str]] = None, 
        html: bool = False, 
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        Sends an email with optional CC, BCC, HTML support and attachments.
        """
        try:
            # Create a multipart email
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = subject

            if cc:
                msg['Cc'] = ", ".join(cc)
                recipients += cc

            if bcc:
                recipients += bcc

            # Attach email body (either plain text or HTML)
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            # Attach files if provided
            if attachments:
                for attachment in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    with open(attachment, 'rb') as file:
                        part.set_payload(file.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename={os.path.basename(attachment)}',
                    )
                    msg.attach(part)

            # Connect to SMTP server and send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(sender, recipients, msg.as_string())

            logger.info(f"Email sent to {', '.join(recipients)} successfully.")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {', '.join(recipients)}. Error: {str(e)}")
            return False

    def send_welcome_email(self, recipient_email: str, username: str) -> bool:
        """
        Sends a welcome email to a new user.
        """
        subject = "Welcome to Website!"
        body = f"""
        <html>
            <body>
                <h1>Welcome, {username}!</h1>
                <p>We're glad to have you with us. Feel free to explore all the features on our platform.</p>
                <p>Best regards,<br>Website Team</p>
            </body>
        </html>
        """
        sender = "no-reply@website.com"
        return self.send_email(
            subject=subject,
            body=body,
            recipients=[recipient_email],
            sender=sender,
            html=True
        )

    def send_password_reset_email(self, recipient_email: str, reset_token: str) -> bool:
        """
        Sends a password reset email to the user.
        """
        subject = "Password Reset Request"
        reset_link = f"https://website.com/reset-password?token={reset_token}"
        body = f"""
        <html>
            <body>
                <h1>Password Reset</h1>
                <p>We received a request to reset your password. Click the link below to reset your password:</p>
                <p><a href="{reset_link}">Reset Password</a></p>
                <p>If you did not request a password reset, please ignore this email.</p>
                <p>Best regards,<br>Website Team</p>
            </body>
        </html>
        """
        sender = "no-reply@website.com"
        return self.send_email(
            subject=subject,
            body=body,
            recipients=[recipient_email],
            sender=sender,
            html=True
        )

    def send_invoice_email(self, recipient_email: str, invoice_pdf_path: str) -> bool:
        """
        Sends an email with the invoice as an attachment.
        """
        subject = "Your Invoice from Website"
        body = """
        <html>
            <body>
                <h1>Invoice</h1>
                <p>Thank you for your purchase. Please find the attached invoice.</p>
                <p>Best regards,<br>Website Team</p>
            </body>
        </html>
        """
        sender = "billing@website.com"
        return self.send_email(
            subject=subject,
            body=body,
            recipients=[recipient_email],
            sender=sender,
            html=True,
            attachments=[invoice_pdf_path]
        )

"""
# Usage
if __name__ == "__main__":
    email_util = EmailUtil(
        smtp_server="smtp.website.com", 
        smtp_port=587, 
        smtp_username="username", 
        smtp_password="password"
    )
    
    # Send a welcome email
    email_util.send_welcome_email(recipient_email="user@website.com", username="User")

    # Send a password reset email
    email_util.send_password_reset_email(recipient_email="user@website.com", reset_token="abc123")

    # Send an invoice email with an attachment
    email_util.send_invoice_email(recipient_email="user@website.com", invoice_pdf_path="/invoice.pdf")
"""