import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_6NLRJU8SBIuO@ep-restless-salad-aobtxx22-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

from app.models.tenant import Institution
from app.models.attendance import AttendanceRecord

engine = create_engine(os.environ["DATABASE_URL"])
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

print("--- Tenant settings ---")
for inst in db.query(Institution).all():
    print(f"Institution {inst.id}: periods_per_day = {inst.periods_per_day}")

print("\n--- Recent Attendance Records (Last 10) ---")
recent_records = db.query(AttendanceRecord).order_by(AttendanceRecord.id.desc()).limit(10).all()
for r in recent_records:
    print(f"Record {r.id}: student={r.student_id}, date={r.date}, period={r.period}, present={r.is_present}, status={r.status}, marked_by={r.marked_by}")

