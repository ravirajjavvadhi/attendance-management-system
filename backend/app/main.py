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
from app.models import user, tenant, academic, attendance, notification, profiles, device, sms

# Auto-create all tables in the database if they don't exist
from sqlalchemy import text
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE faculty_profiles ADD COLUMN access_level VARCHAR DEFAULT 'ASSIGNED_SECTION_ACCESS'"))
        conn.commit()
except Exception:
    pass

try:
    with engine.connect() as conn:
        # Drop the old notification_logs table so create_all recreates it
        conn.execute(text("DROP TABLE IF EXISTS notification_logs CASCADE"))
        conn.commit()
except Exception:
    pass

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
    "ALTER TABLE sms_queue ADD CONSTRAINT sms_queue_message_uuid_key UNIQUE (message_uuid)",
    "ALTER TABLE sms_queue ADD COLUMN IF NOT EXISTS priority_level VARCHAR DEFAULT 'NORMAL'",
    "ALTER TABLE sms_queue ADD COLUMN IF NOT EXISTS delivery_status VARCHAR DEFAULT 'UNKNOWN'",
    "ALTER TABLE devices ADD COLUMN IF NOT EXISTS is_charging BOOLEAN",
    "ALTER TABLE devices ADD COLUMN IF NOT EXISTS app_version VARCHAR",
    "ALTER TABLE devices ADD COLUMN IF NOT EXISTS foreground_service_running BOOLEAN",
    "ALTER TABLE devices ADD COLUMN IF NOT EXISTS network_type VARCHAR",
    "ALTER TABLE devices ADD COLUMN IF NOT EXISTS storage_remaining VARCHAR",
    "ALTER TABLE devices ADD COLUMN IF NOT EXISTS ram_usage VARCHAR",
    "ALTER TABLE devices ADD COLUMN IF NOT EXISTS android_version VARCHAR"
]

for migration in migrations:
    try:
        with engine.connect() as conn:
            conn.execute(text(migration))
            conn.commit()
    except Exception as e:
        print(f"Migration failed for {migration}: {e}")

Base.metadata.create_all(bind=engine)

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
