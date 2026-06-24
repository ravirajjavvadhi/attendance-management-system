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
        # Drop the old notification_logs table so create_all recreates it with the new schema (channel, recipient, provider_response)
        conn.execute(text("DROP TABLE IF EXISTS notification_logs CASCADE"))
        conn.commit()
except Exception as e:
    print("Drop table error:", e)

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
