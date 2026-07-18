from sqlalchemy.orm import Session
from datetime import datetime
from .academic_calendar_engine import AcademicCalendarEngine
from .timetable_engine import TimetableEngine

class SchedulingEngine:
    """
    The real-time timekeeper.
    Fuses the Academic Calendar, Current Period, and Timetable.
    """

    @staticmethod
    def get_current_attendance_window(db: Session, faculty_user_id: int):
        """
        Determines if a faculty member currently has an open attendance window.
        1. Checks if today is a Working Day.
        2. Resolves current class via Timetable Engine.
        """
        now = datetime.now()
        
        # 1. Check Academic Calendar
        if not AcademicCalendarEngine.is_attendance_required(db, now.date()):
            return {"status": "CLOSED", "reason": "Today is a Holiday or Non-Working Day."}
            
        # 2. Check Timetable (which checks Period internally)
        active_class = TimetableEngine.resolve_current_class_for_faculty(db, faculty_user_id, now)
        
        if not active_class:
            return {"status": "CLOSED", "reason": "No active class scheduled for this time."}
            
        return {
            "status": "OPEN",
            "timetable_id": active_class.id,
            "subject_id": active_class.subject_id,
            "section_id": active_class.section_id
        }
