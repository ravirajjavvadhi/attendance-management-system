from sqlalchemy.orm import Session
from datetime import datetime
from .scheduling_engine import SchedulingEngine
from .notification_engine import NotificationEngine
from app.models.attendance import AttendanceSession, AttendanceRecord

class AttendanceEngine:
    """
    The core attendance pipeline.
    Create Session -> Lock Session -> Verify -> Analyze -> Notify -> Save
    """

    @staticmethod
    def start_attendance_session(db: Session, tenant_id: int, faculty_user_id: int):
        """
        Automatically resolves the class via Scheduling Engine and opens an attendance session.
        """
        # Checks Calendar AND Timetable
        window = SchedulingEngine.get_current_attendance_window(db, faculty_user_id)
        
        if window["status"] == "CLOSED":
            raise Exception(f"Cannot open session: {window['reason']}")
            
        timetable_id = window["timetable_id"]
        today = datetime.now().date()
        
        # Check if session already exists for today
        existing_session = db.query(AttendanceSession).filter(
            AttendanceSession.timetable_id == timetable_id,
            AttendanceSession.date == today
        ).first()
        
        if existing_session:
            return existing_session
            
        # Create new session
        new_session = AttendanceSession(
            tenant_id=tenant_id,
            timetable_id=timetable_id,
            date=today,
            status="OPEN",
            faculty_user_id=faculty_user_id
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        return new_session

    @staticmethod
    def lock_attendance_session(db: Session, session_id: int):
        """
        Locks the session to prevent further changes and triggers absentee notifications.
        """
        session = db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
        if not session:
            raise Exception("Session not found")
            
        session.status = "LOCKED"
        db.commit()
        
        # Find all absentees for this session
        absentees = db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id == session_id,
            AttendanceRecord.is_present == False
        ).all()
        
        absent_student_ids = [record.student_id for record in absentees]
        subject_id = absentees[0].subject_id if absentees else None
        
        from .timeline_engine import TimelineEngine
        TimelineEngine.record_event(
            db=db,
            tenant_id=session.tenant_id,
            user_id=session.faculty_user_id,
            event_type="ATTENDANCE_LOCKED",
            description=f"Attendance session locked for {len(absentees)} absentees.",
            context={
                "absent_student_ids": absent_student_ids,
                "date": str(session.date),
                "subject_id": subject_id
            }
        )
            
        return {"status": "success", "message": f"Session {session_id} locked. {len(absentees)} absentee notifications dispatched via Timeline."}
