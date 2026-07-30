import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime

os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_6NLRJU8SBIuO@ep-restless-salad-aobtxx22-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

from app.models.attendance import AttendanceRecord

engine = create_engine(os.environ["DATABASE_URL"])
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

today_date = datetime.date(2026, 7, 29)
null_periods = db.query(AttendanceRecord).filter(AttendanceRecord.date == today_date, AttendanceRecord.period == None).count()
print(f"Records with period=None today: {null_periods}")
