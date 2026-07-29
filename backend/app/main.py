from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router

from contextlib import asynccontextmanager
from app.services.simulator import start_simulator

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start SMS Simulator Background Task
    # start_simulator() # DISABLED: So the real Android app can process SMS!
    yield
    # Shutdown

app = FastAPI(title="EduFlow AI API", description="Smart Academic Operations & Attendance Automation Platform", lifespan=lifespan)

from app.db.database import engine, Base
from app.models import user, tenant, academic, attendance, notification, profiles, device, sms, erp_academic

# Auto-create all tables in the database if they don't exist
Base.metadata.create_all(bind=engine)

from sqlalchemy import text
migrations = [
    "ALTER TABLE attendance_records DROP CONSTRAINT IF EXISTS attendance_records_student_id_fkey",
    "ALTER TABLE attendance_records ADD CONSTRAINT attendance_records_student_id_fkey FOREIGN KEY (student_id) REFERENCES student_profiles(id)",
    "ALTER TABLE institutions ADD COLUMN IF NOT EXISTS periods_per_day INTEGER DEFAULT 0",
    "ALTER TABLE institutions ADD COLUMN IF NOT EXISTS notification_preference VARCHAR DEFAULT 'PARENT'",
    "ALTER TABLE attendance_records ADD COLUMN IF NOT EXISTS period INTEGER",
    "ALTER TABLE institutions ADD COLUMN IF NOT EXISTS max_sms_per_device_per_day INTEGER DEFAULT 70",
    "ALTER TABLE institutions ADD COLUMN IF NOT EXISTS sms_engine VARCHAR DEFAULT 'LEGACY'",
    "ALTER TABLE sms_queue ADD COLUMN IF NOT EXISTS processed_by_device_id INTEGER REFERENCES devices(id)",
    "ALTER TABLE sms_queue ADD COLUMN IF NOT EXISTS message_uuid VARCHAR",
    "ALTER TABLE sms_queue ADD COLUMN IF NOT EXISTS priority_level VARCHAR DEFAULT 'NORMAL'",
    "ALTER TABLE sms_queue ADD COLUMN IF NOT EXISTS delivery_status VARCHAR DEFAULT 'UNKNOWN'",
    "ALTER TABLE devices ADD COLUMN IF NOT EXISTS is_charging BOOLEAN",
    "ALTER TABLE devices ADD COLUMN IF NOT EXISTS app_version VARCHAR",
    "ALTER TABLE devices ADD COLUMN IF NOT EXISTS foreground_service_running BOOLEAN",
    "ALTER TABLE devices ADD COLUMN IF NOT EXISTS network_type VARCHAR",
    "ALTER TABLE devices ADD COLUMN IF NOT EXISTS storage_remaining VARCHAR",
    "ALTER TABLE devices ADD COLUMN IF NOT EXISTS ram_usage VARCHAR",
    "ALTER TABLE devices ADD COLUMN IF NOT EXISTS android_version VARCHAR",
    # ── Tier-1 Enterprise & Academic OS Migrations (Render Production Sync) ──
    "ALTER TABLE sections ADD COLUMN IF NOT EXISTS academic_session_id INTEGER",
    "ALTER TABLE sections ADD COLUMN IF NOT EXISTS admission_year INTEGER",
    "ALTER TABLE events ADD COLUMN IF NOT EXISTS category VARCHAR DEFAULT 'GENERAL'",
    "ALTER TABLE events ADD COLUMN IF NOT EXISTS priority VARCHAR DEFAULT 'MEDIUM'",
    "ALTER TABLE events ADD COLUMN IF NOT EXISTS target_audience VARCHAR DEFAULT 'ALL'",
    "ALTER TABLE events ADD COLUMN IF NOT EXISTS academic_session_id INTEGER",
    "ALTER TABLE notification_logs ADD COLUMN IF NOT EXISTS message VARCHAR",
    "ALTER TABLE notification_logs ADD COLUMN IF NOT EXISTS title VARCHAR DEFAULT 'System Alert'",
    "ALTER TABLE notification_logs ADD COLUMN IF NOT EXISTS event_type VARCHAR DEFAULT 'GENERAL'",
    "ALTER TABLE notification_logs ADD COLUMN IF NOT EXISTS entity_type VARCHAR",
    "ALTER TABLE notification_logs ADD COLUMN IF NOT EXISTS entity_id INTEGER",
    "ALTER TABLE notification_logs ADD COLUMN IF NOT EXISTS is_read BOOLEAN DEFAULT FALSE",
    "ALTER TABLE notification_logs ADD COLUMN IF NOT EXISTS read_at TIMESTAMP WITH TIME ZONE",
    "ALTER TABLE notification_logs ADD COLUMN IF NOT EXISTS deleted_by_parent BOOLEAN DEFAULT FALSE",
    "ALTER TABLE notification_logs ADD COLUMN IF NOT EXISTS student_id INTEGER",
    "ALTER TABLE attendance_sessions ADD COLUMN IF NOT EXISTS academic_session_id INTEGER",
    "ALTER TABLE attendance_records ADD COLUMN IF NOT EXISTS subject_id INTEGER",
    "ALTER TABLE attendance_records ADD COLUMN IF NOT EXISTS session_id INTEGER",
    "ALTER TABLE attendance_records ADD COLUMN IF NOT EXISTS academic_session_id INTEGER",
    "ALTER TABLE attendance_records ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'PRESENT'",
    "ALTER TABLE attendance_records ADD COLUMN IF NOT EXISTS marked_by INTEGER",
    "ALTER TABLE attendance_summaries ADD COLUMN IF NOT EXISTS academic_session_id INTEGER",
    "ALTER TABLE attendance_summaries ADD COLUMN IF NOT EXISTS medical_leave_count INTEGER DEFAULT 0",
    "ALTER TABLE attendance_summaries ADD COLUMN IF NOT EXISTS od_count INTEGER DEFAULT 0",
    "ALTER TABLE attendance_summaries ADD COLUMN IF NOT EXISTS shortage_percentage FLOAT DEFAULT 0.0",
    "ALTER TABLE attendance_summaries ADD COLUMN IF NOT EXISTS is_shortage BOOLEAN DEFAULT FALSE",
    "ALTER TABLE subject_summaries ADD COLUMN IF NOT EXISTS academic_session_id INTEGER",
    "ALTER TABLE faculty_summaries ADD COLUMN IF NOT EXISTS academic_session_id INTEGER",
    "ALTER TABLE department_summaries ADD COLUMN IF NOT EXISTS academic_session_id INTEGER",
    "ALTER TABLE institution_summaries ADD COLUMN IF NOT EXISTS academic_session_id INTEGER",
    "ALTER TABLE erp_timetable ADD COLUMN IF NOT EXISTS academic_session_id INTEGER",
    "ALTER TABLE erp_subjects ADD COLUMN IF NOT EXISTS generated_code VARCHAR",
    "ALTER TABLE erp_subjects ADD COLUMN IF NOT EXISTS is_auto_generated BOOLEAN DEFAULT TRUE",
    "ALTER TABLE erp_subjects ADD COLUMN IF NOT EXISTS credits INTEGER DEFAULT 0",
    "ALTER TABLE erp_subjects ADD COLUMN IF NOT EXISTS subject_type VARCHAR DEFAULT 'THEORY'",
    "ALTER TABLE erp_subjects ADD COLUMN IF NOT EXISTS prerequisites VARCHAR",
    "ALTER TABLE erp_subjects ADD COLUMN IF NOT EXISTS outcomes VARCHAR",
    "ALTER TABLE erp_subjects ADD COLUMN IF NOT EXISTS is_elective BOOLEAN DEFAULT FALSE",
    "ALTER TABLE faculty_profiles ADD COLUMN IF NOT EXISTS access_level VARCHAR DEFAULT 'ASSIGNED_SECTION_ACCESS'",
    "ALTER TABLE parent_profiles ADD COLUMN IF NOT EXISTS pin_hash VARCHAR",
    "ALTER TABLE parent_profiles ADD COLUMN IF NOT EXISTS device_token VARCHAR",
    "ALTER TABLE parent_profiles ADD COLUMN IF NOT EXISTS biometric_enabled BOOLEAN DEFAULT FALSE",
    "ALTER TABLE parent_profiles ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'ACTIVE'",
    "ALTER TABLE parent_student_links ADD COLUMN IF NOT EXISTS relationship VARCHAR DEFAULT 'PRIMARY'",
    "ALTER TABLE parent_student_links ADD COLUMN IF NOT EXISTS is_primary BOOLEAN DEFAULT FALSE",
    "ALTER TABLE parent_student_links ADD COLUMN IF NOT EXISTS receive_notifications BOOLEAN DEFAULT TRUE",
    "ALTER TABLE parent_student_links ADD COLUMN IF NOT EXISTS receive_sms BOOLEAN DEFAULT TRUE",
    "ALTER TABLE parent_student_links ADD COLUMN IF NOT EXISTS receive_push BOOLEAN DEFAULT TRUE",
]

for migration in migrations:
    try:
        with engine.connect() as conn:
            conn.execute(text(migration))
            conn.commit()
    except Exception:
        pass

try:
    with engine.connect() as conn:
        conn.execute(text("UPDATE notification_logs SET message = content WHERE message IS NULL"))
        conn.commit()
except Exception:
    pass

# Enable CORS for production (Vercel) and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For strict production, change this to your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to EduFlow AI API"}
