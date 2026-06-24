import smtplib
from email.message import EmailMessage
from app.core.config import settings
from app.db.database import SessionLocal
from app.models.notification import NotificationLog, SMSTemplate
from app.models.sms import SmsQueue
from app.models.profiles import StudentProfile

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
            channel="EMAIL",
            recipient=to_email,
            status=status,
            message=f"Subject: {subject}\n\n{body}",
            provider_response=error_msg
        )
        db.add(log)
        db.commit()
    finally:
        db.close()
    
    return {"status": status}

def queue_sms(student_id: int, date: str, tenant_id: int, period: int = None):
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
            # Only create a failed log
            log = NotificationLog(
                tenant_id=tenant_id,
                channel="SMS",
                recipient="Unknown",
                status="FAILED",
                message=message,
                provider_response="Missing parent mobile number"
            )
            db.add(log)
        else:
            log_status = "PENDING"
            # Fetch Institution Name
            from app.models.tenant import Institution
            institution = db.query(Institution).filter(Institution.id == tenant_id).first()
            institution_name = institution.name if institution else "Our Institution"
            
            # Fetch Institution's Custom SMS Template
            template = db.query(SMSTemplate).filter(SMSTemplate.tenant_id == tenant_id).first()
            if template:
                message = template.absent_message.replace("{name}", student_name).replace("{roll_no}", roll_number)
            else:
                if period is not None:
                    message = (
                        "Attendance Alert\n\n"
                        "Dear Parent/Guardian,\n\n"
                        f"{student_name} ({roll_number}) was absent during Period {period} on {date}.\n\n"
                        f"Institution: {institution_name}\n\n"
                        "Regards,\n"
                        f"{institution_name}"
                    )
                else:
                    message = (
                        "Attendance Alert\n\n"
                        "Dear Parent/Guardian,\n\n"
                        f"{student_name} ({roll_number}) has been recorded absent on {date}.\n\n"
                        f"Institution: {institution_name}\n\n"
                        "Regards,\n"
                        f"{institution_name}"
                    )
            
            # Queue the SMS for the Android Gateway
            queue_item = SmsQueue(
                tenant_id=tenant_id,
                recipient_name=student_name,
                recipient_phone=profile.parent_mobile,
                message=message,
                status="PENDING",
                source_module="ATTENDANCE"
            )
            db.add(queue_item)
            
            # Also log it
            log = NotificationLog(
                tenant_id=tenant_id,
                channel="SMS",
                recipient=profile.parent_mobile,
                status="PENDING",
                message=message
            )
            db.add(log)
            
        db.commit()
        return {"status": log_status}
    finally:
        db.close()
