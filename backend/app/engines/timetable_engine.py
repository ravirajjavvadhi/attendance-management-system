from sqlalchemy.orm import Session
from datetime import datetime
from app.models.erp_academic import Timetable, Period

class TimetableEngine:
    """
    The heart of the platform's automation.
    Resolves exactly what class is happening at any given moment.
    """

    @staticmethod
    def resolve_current_class_for_faculty(db: Session, faculty_user_id: int, check_time: datetime = None):
        """
        Returns the Timetable entry for a faculty member based on the current time and day.
        Eliminates the need for manual dropdown selection during attendance.
        """
        if not check_time:
            check_time = datetime.now()
            
        current_day = check_time.strftime("%A").upper() # e.g., "MONDAY"
        current_time_only = check_time.time()
        
        # 1. Find the active period for the current time
        active_period = db.query(Period).filter(
            Period.start_time <= current_time_only,
            Period.end_time >= current_time_only
        ).first()
        
        if not active_period:
            return None # No active class right now
            
        # 2. Find the timetable entry for this faculty, day, and period
        active_class = db.query(Timetable).filter(
            Timetable.faculty_user_id == faculty_user_id,
            Timetable.day_of_week == current_day,
            Timetable.period_id == active_period.id
        ).first()
        
        return active_class

    @staticmethod
    def resolve_schedule_for_student(db: Session, student_id: int, date: datetime):
        """
        Returns the full day's timetable for a specific student's section.
        """
        pass
