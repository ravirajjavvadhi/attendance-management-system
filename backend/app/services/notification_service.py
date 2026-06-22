import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from app.core.config import settings

class NotificationService:
    def __init__(self):
        # We allow fallback to environment variables directly if settings is not populated during early init
        self.smtp_username = settings.SMTP_USERNAME or os.environ.get("EMAIL_USER")
        self.smtp_password = settings.SMTP_PASSWORD or os.environ.get("EMAIL_PASS")
        self.smtp_host = settings.SMTP_HOST or "smtp.gmail.com"
        self.smtp_port = settings.SMTP_PORT or 587
        self.email_from = settings.EMAIL_FROM or self.smtp_username

    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """
        Sends an HTML email using the configured SMTP server.
        """
        if not self.smtp_username or not self.smtp_password:
            print("ERROR: SMTP credentials not configured. Cannot send email.")
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"EduFlow AI <{self.email_from}>"
        msg["To"] = to_email

        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            print(f"Successfully sent email to {to_email}")
            return True
        except Exception as e:
            print(f"Failed to send email to {to_email}: {str(e)}")
            return False

notification_service = NotificationService()
