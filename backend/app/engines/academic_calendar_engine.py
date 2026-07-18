from sqlalchemy.orm import Session
from datetime import date
from app.models.calendar import CalendarDay

class AcademicCalendarEngine:
    """
    The heartbeat of the institution's schedule.
    """

    @staticmethod
    def get_day_type(db: Session, check_date: date):
        """
        Resolves if the given date is a WORKING, HOLIDAY, EXAM, or EVENT day.
        Returns the CalendarDay object if configured, else defaults to a standard working logic.
        """
        calendar_day = db.query(CalendarDay).filter(CalendarDay.date == check_date).first()
        if calendar_day:
            return calendar_day.day_type
            
        # Default logic (e.g., weekends are holidays)
        if check_date.weekday() >= 5: # Saturday/Sunday
            return "HOLIDAY"
            
        return "WORKING"

    @staticmethod
    def is_attendance_required(db: Session, check_date: date) -> bool:
        """
        Determines if attendance collection should run for a specific day.
        """
        day_type = AcademicCalendarEngine.get_day_type(db, check_date)
        return day_type in ["WORKING", "EXAM"]
