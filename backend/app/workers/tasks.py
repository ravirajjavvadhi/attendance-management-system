import smtplib
from email.message import EmailMessage
from typing import List, Dict, Any
from app.workers.celery_app import celery_app
from app.core.config import settings
from app.db.database import SessionLocal
from app.models.user import User
from app.models.notification import NotificationLog, SMSTemplate
from app.models.profiles import StudentProfile

@celery_app.task
def send_email(to_email: str, subject: str, body: str, recipient_id: int, tenant_id: int):
    if not settings.SMTP_HOST:
        return {"status": "skipped", "reason": "SMTP not configured"}

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email

    status = "FAILED"
    error_msg = None
    try:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        status = "SENT"
    except Exception as e:
        error_msg = str(e)
        
    db = SessionLocal()
    try:
        log = NotificationLog(
            tenant_id=tenant_id,
            user_id=recipient_id,
            type="EMAIL",
            status=status,
            content=f"Subject: {subject}\n\n{body}",
            error_message=error_msg
        )
        db.add(log)
        db.commit()
    finally:
        db.close()
    
    return {"status": status}

@celery_app.task
def queue_sms(student_id: int, date: str, tenant_id: int):
    """
    Background worker that formats the custom SMS for a student's absence and
    queues it for the Android SIM gateway. Will silently catch missing phone numbers.
    """
    db = SessionLocal()
    try:
        profile = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
        
        if not profile:
            return {"status": "skipped", "reason": "Student profile not found"}
            
        student_name = profile.name or "Student"
        roll_number = profile.roll_number
        
        # Determine status based on parent mobile availability
        if not profile.parent_mobile:
            log_status = "FAILED_MISSING_NUMBER"
            message = f"Failed to send SMS to {student_name} ({roll_number}): No parent mobile number provided."
        else:
            log_status = "PENDING"
            # Fetch Institution's Custom SMS Template
            template = db.query(SMSTemplate).filter(SMSTemplate.tenant_id == tenant_id).first()
            if template:
                message = template.absent_message.replace("{name}", student_name).replace("{roll_no}", roll_number)
            else:
                message = f"Dear Parent, {student_name} (Roll No: {roll_number}) is absent today."
        
        log = NotificationLog(
            tenant_id=tenant_id,
            user_id=student_id, # Using student_id (StudentProfile.id) as the recipient ID here
            type="SMS",
            status=log_status,
            content=message
        )
        db.add(log)
        db.commit()
        return {"status": log_status}
    finally:
        db.close()
