import os
import sys

# Add backend to path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ["EMAIL_USER"] = "kevryntech@gmail.com"
os.environ["EMAIL_PASS"] = "oyjgiiqradkxzyrs"

from app.services.notification_service import notification_service
from app.services.email_templates import get_institution_welcome_email

def send_test_welcome_email():
    management_email = "javvadhichintu@gmail.com"
    management_name = "Javvadi Chintu"
    institution_name = "Testing Institute"
    generated_password = "temp_password_123" # The one generated during the earlier creation
    portal_url = "https://edu-flow-ai-jlr.vercel.app"

    email_content = get_institution_welcome_email(
        management_name=management_name,
        institution_name=institution_name,
        management_email=management_email,
        generated_password=generated_password,
        portal_url=portal_url
    )
    
    print(f"Sending test welcome email to {management_email}...")
    success = notification_service.send_email(
        to_email=management_email,
        subject="Welcome to EduFlow AI – Your Institution Has Been Successfully Onboarded",
        html_content=email_content
    )
    
    if success:
        print("Success! Check your inbox.")
    else:
        print("Failed to send.")

if __name__ == "__main__":
    send_test_welcome_email()
