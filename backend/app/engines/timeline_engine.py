from sqlalchemy.orm import Session
from app.models.communication import TimelineEvent
from app.engines.notification_engine import NotificationEngine

class TimelineEngine:
    """
    The centralized event router.
    Every action in the ERP MUST pass through here to ensure an unbroken chronological audit trail.
    """

    @staticmethod
    def record_event(db: Session, tenant_id: int, user_id: int, event_type: str, description: str, context: dict = None):
        """
        Records an event in the timeline and intelligently routes side-effects.
        """
        # 1. Record the chronological event
        event = TimelineEvent(
            tenant_id=tenant_id,
            user_id=user_id,
            event_type=event_type,
            description=description
        )
        db.add(event)
        
        # 2. Automatically dispatch notifications if required
        if event_type == "ATTENDANCE_LOCKED":
            absent_student_ids = context.get("absent_student_ids", [])
            for student_id in absent_student_ids:
                NotificationEngine.dispatch(
                    db=db,
                    tenant_id=tenant_id,
                    event_type="ATTENDANCE_ABSENT",
                    student_id=student_id,
                    context={"date": context.get("date", ""), "subject_id": context.get("subject_id", "")}
                )
                
        db.commit()
        return event
