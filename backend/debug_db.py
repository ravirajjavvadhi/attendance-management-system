import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import traceback

os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_6NLRJU8SBIuO@ep-restless-salad-aobtxx22-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

from app.db.database import Base
from app.models.academic import Section, Class, Department, Event, AcademicSession
from app.models.profiles import StudentProfile, FacultyProfile
from app.models.attendance import AttendanceRecord, AttendanceSummary
from app.models.notification import NotificationLog
from sqlalchemy import func, case

engine = create_engine(os.environ["DATABASE_URL"])
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

print("Connection established!")

try:
    print("Testing total_students query...")
    active_tenant_id = 1
    total_students = db.query(func.count(StudentProfile.id)).join(Section, StudentProfile.section_id == Section.id).filter(Section.tenant_id == active_tenant_id).scalar() or 0
    print(f"Total students: {total_students}")
    
    if total_students == 0:
        total_students = db.query(func.count(StudentProfile.id)).scalar() or 0
        print(f"Total students (fallback): {total_students}")
        
    print("Testing attendance_stats query...")
    attendance_stats = db.query(
        StudentProfile.id,
        StudentProfile.name,
        Section.name.label("section_name"),
        func.count(AttendanceRecord.id).label("total"),
        func.sum(case((AttendanceRecord.is_present == True, 1), else_=0)).label("present")
    ).join(Section, StudentProfile.section_id == Section.id) \
     .join(AttendanceRecord, StudentProfile.id == AttendanceRecord.student_id) \
     .filter(Section.tenant_id == active_tenant_id) \
     .group_by(StudentProfile.id, StudentProfile.name, Section.name).all()
     
    print(f"Attendance stats count: {len(attendance_stats)}")
    
    print("Testing NotificationLog query...")
    recent_logs = db.query(NotificationLog).filter(NotificationLog.tenant_id == active_tenant_id).order_by(NotificationLog.created_at.desc()).limit(5).all()
    for log in recent_logs:
        print(f"Log ID: {log.id}, Message: {log.message}")
        
    print("Testing department overview query...")
    all_students_dept = db.query(
        Department.name,
        func.count(StudentProfile.id)
    ).join(Section, StudentProfile.section_id == Section.id) \
     .join(Class, Section.class_id == Class.id) \
     .join(Department, Class.department_id == Department.id) \
     .filter(Section.tenant_id == active_tenant_id) \
     .group_by(Department.name).all()
    print(f"Dept total count: {len(all_students_dept)}")
    
    print("Testing get_student_mega_payload query...")
    student_id = 42 # From user's screenshot
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    print(f"Student 42 name: {student.name if student else 'Not Found'}")
    
    if student:
        print(f"Testing ReportingEngine for student {student.id}...")
        from app.engines.reporting_engine import ReportingEngine
        report = ReportingEngine.generate_attendance_report(db, tenant_id=active_tenant_id, filters={"student_id": student.id})
        print(f"Report items: {len(report)}")
        
except Exception as e:
    print(f"ERROR OCCURRED:")
    traceback.print_exc()

print("Done!")
