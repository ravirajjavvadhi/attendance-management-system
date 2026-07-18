from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from app.db.database import Base

class Exam(Base):
    __tablename__ = "exams"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=False)
    name = Column(String, nullable=False) # e.g. "Midterm 1", "End Semester"
    exam_type = Column(String, nullable=False) # INTERNAL, SEMESTER, LAB, PRACTICAL, QUIZ
    date = Column(Date, nullable=False)

class ExamResult(Base):
    __tablename__ = "exam_results"
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("erp_subjects.id"), nullable=False)
    marks_obtained = Column(Float, nullable=False)
    max_marks = Column(Float, nullable=False)
    cgpa_mapping = Column(Float, nullable=True) # E.g., 9.5
