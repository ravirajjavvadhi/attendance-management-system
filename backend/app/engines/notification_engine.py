from sqlalchemy.orm import Session
from app.models.profiles import ParentStudentLink, ParentProfile, StudentProfile
from app.models.user import User
from app.models.notification import NotificationLog

class NotificationEngine:
    """
    The unified communication bus.
    Routes events through Push -> In-App -> SMS -> Email
    """

    @staticmethod
    def dispatch(db: Session, tenant_id: int, event_type: str, student_id: int, context: dict):
        """
        Accepts any event and routes it to the correct channels based on Parent preferences.
        """
        student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
        if not student:
            return

        links = db.query(ParentStudentLink).filter(ParentStudentLink.student_id == student_id).all()
        
        for link in links:
            parent_profile = db.query(ParentProfile).filter(ParentProfile.id == link.parent_id).first()
            if not parent_profile:
                continue
                
            user = db.query(User).filter(User.id == parent_profile.user_id).first()
            if not user or not user.mobile_number:
                continue

            message = f"EduFlow: Notice regarding {student.name}: {event_type} - {context.get('date', '')}"
            priority = "HIGH" if "ABSENT" in event_type or "EMERGENCY" in event_type else "NORMAL"
            
            # --- TIER 1: Push Notification (FCM) ---
            push_success = False
            if link.receive_push and parent_profile.device_token:
                # Mock FCM Send
                push_success = True
                
            # --- TIER 2: In-App Notification (Database) ---
            # Storing it so the Parent App dashboard can read it
            
            # --- TIER 3: Android SMS Gateway Queue ---
            # If critical priority or push failed or parent explicitly requested SMS
            if link.receive_sms or (not push_success and priority == "HIGH"):
                log = NotificationLog(
                    tenant_id=tenant_id,
                    channel="SMS",
                    recipient=user.mobile_number,
                    status="PENDING",
                    message=message
                )
                db.add(log)
                
            # --- TIER 4: Email / WhatsApp / Voice AI ---
            # Future expansion stubs
                
        db.commit()
