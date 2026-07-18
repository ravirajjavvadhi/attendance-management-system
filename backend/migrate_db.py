import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import engine, Base
from sqlalchemy import text

def apply_migrations():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE faculty_profiles ADD COLUMN access_level VARCHAR DEFAULT 'ASSIGNED_SECTION_ACCESS'"))
            print("Added access_level to faculty_profiles")
        except Exception as e:
            print("access_level already exists or error:", e)

        try:
            conn.execute(text("ALTER TABLE sms_queue ADD COLUMN processing_started_at TIMESTAMP WITH TIME ZONE;"))
            print("Added processing_started_at to sms_queue")
        except Exception as e:
            print("processing_started_at already exists or error:", e)

        try:
            conn.execute(text("UPDATE sms_queue SET status = 'IN_PROGRESS' WHERE status = 'PROCESSING';"))
            print("Migrated PROCESSING to IN_PROGRESS")
        except Exception as e:
            print("Failed to migrate status:", e)

        try:
            conn.execute(text("ALTER TABLE attendance_records ADD COLUMN subject_id INTEGER REFERENCES erp_subjects(id);"))
            print("Added subject_id to attendance_records")
        except Exception as e:
            print("subject_id already exists or error:", e)

        try:
            conn.execute(text("ALTER TABLE attendance_records ADD COLUMN timetable_id INTEGER REFERENCES erp_timetable(id);"))
            print("Added timetable_id to attendance_records")
        except Exception as e:
            print("timetable_id already exists or error:", e)

        conn.commit()

    # Create new tables (like faculty_section_assignments, erp models)
    from app.models.profiles import ParentProfile, ParentStudentLink, StudentProfile, FacultyProfile
    from app.models.academic import AcademicYear, Section
    from app.models.erp_academic import Branch, Semester, Subject, Period, Timetable, FacultySubjectAllocation
    from app.models.calendar import SemesterTerm, CalendarDay
    from app.models.attendance import AttendanceRecord, AttendanceSession
    from app.models.examination import Exam, ExamResult
    from app.models.assignment import Assignment, AssignmentSubmission
    from app.models.communication import CampusNotice, TimelineEvent
    from app.models.tenant import InstitutionModules
    Base.metadata.create_all(bind=engine)
    print("Created new tables.")

if __name__ == "__main__":
    apply_migrations()
