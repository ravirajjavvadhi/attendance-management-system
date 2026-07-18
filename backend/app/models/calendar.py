from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Time
from app.db.database import Base

class SemesterTerm(Base):
    __tablename__ = "semester_terms"
    id = Column(Integer, primary_key=True, index=True)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=False)
    name = Column(String, nullable=False) # e.g. "Odd Semester" or "Sem 1"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

class CalendarDay(Base):
    __tablename__ = "calendar_days"
    id = Column(Integer, primary_key=True, index=True)
    semester_term_id = Column(Integer, ForeignKey("semester_terms.id"), nullable=False)
    date = Column(Date, nullable=False)
    day_type = Column(String, nullable=False) # WORKING, HOLIDAY, EXAM, EVENT
    description = Column(String, nullable=True) # e.g. "Diwali", "Midterm 1"
    is_attendance_required = Column(Boolean, default=True)
