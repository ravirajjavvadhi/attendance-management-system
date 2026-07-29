import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_6NLRJU8SBIuO@ep-restless-salad-aobtxx22-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

from app.models.academic import Section, Class, Department
from app.models.profiles import StudentProfile

engine = create_engine(os.environ["DATABASE_URL"])
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

print("--- Tenant ID Analysis ---")
sections = db.query(Section).all()
for sec in sections[:5]:
    print(f"Section {sec.id} - {sec.name}: tenant_id = {sec.tenant_id}")

student = db.query(StudentProfile).filter(StudentProfile.id == 42).first()
if student:
    print(f"\nStudent 42 belongs to section {student.section_id}")
    sec = db.query(Section).filter(Section.id == student.section_id).first()
    if sec:
        print(f"Which has tenant_id = {sec.tenant_id}")
        
print("\n--- Why is get_student_mega_payload failing? ---")
try:
    from app.engines.dashboard_engine import DashboardEngine
    print(f"Testing DashboardEngine for student 42 with tenant_id={sec.tenant_id if sec else 1}")
    payload = DashboardEngine.get_student_mega_payload(db, 42, sec.tenant_id if sec else 1)
    if payload:
        print(f"Successfully generated payload! Length: {len(str(payload))}")
    else:
        print("Payload is None!")
except Exception as e:
    import traceback
    traceback.print_exc()

