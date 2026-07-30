import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime

os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_6NLRJU8SBIuO@ep-restless-salad-aobtxx22-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

from app.models.attendance import AttendanceRecord
from app.models.erp_academic import Timetable, Period

engine = create_engine(os.environ["DATABASE_URL"])
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

student_id = 42 # Wait, what is the student's ID? Let's check all attendance today!
today_date = datetime.date(2026, 7, 29) # Or let's just query last 50 records today

print(f"--- Attendance Records for {today_date} ---")
records = db.query(AttendanceRecord).filter(AttendanceRecord.date == today_date).limit(50).all()
for r in records:
    print(f"Student: {r.student_id}, Period: {r.period}, Present: {r.is_present}, Marked_by: {r.marked_by}")

print(f"--- Unique Students with Attendance Today ---")
student_ids = list(set([r.student_id for r in records]))
print(student_ids)

