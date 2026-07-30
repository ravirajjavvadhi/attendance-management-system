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
records = db.query(AttendanceRecord).filter(AttendanceRecord.date == today_date).all()
print(f"Total attendance records for today: {len(records)}")

periods = {}
for r in records:
    periods[r.period] = periods.get(r.period, 0) + 1

print("Counts per period:")
for p, c in periods.items():
    print(f"Period {p}: {c} records")
