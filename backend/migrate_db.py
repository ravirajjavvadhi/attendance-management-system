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

        conn.commit()

    # Create new tables (like faculty_section_assignments)
    from app.models.profiles import FacultySectionAssignment
    Base.metadata.create_all(bind=engine)
    print("Created new tables.")

if __name__ == "__main__":
    apply_migrations()
