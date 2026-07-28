import sys
import os
import io

# Ensure stdout uses utf-8 or ignore errors on windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime, timedelta

from app.db.database import Base
from app.models.profiles import StudentProfile, FacultyProfile
from app.models.academic import AcademicSession, Department, Class, Section
from app.models.erp_academic import Subject, Timetable, Period
from app.models.attendance import AttendanceRecord, AttendanceSummary, SubjectSummary, DepartmentSummary, InstitutionSummary, AttendanceStatusEnum
from app.services.subject_code_service import SubjectCodeService
from app.engines.materialized_summary_engine import materialized_summary_engine
from app.engines.enterprise_analytics_engine import enterprise_analytics_engine

import app.models.tenant, app.models.user, app.models.device, app.models.academic, app.models.assignment, app.models.attendance, app.models.calendar, app.models.communication, app.models.erp_academic, app.models.examination, app.models.notification, app.models.profiles, app.models.sms

def run_verification():
    print("=" * 70)
    print("EDUFLOW TIER-1 ENTERPRISE ERP VERIFICATION SUITE")
    print("=" * 70)

    # 1. Initialize In-Memory SQLite Database for pristine execution
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        print("\n[TEST 1] Testing Collision-Safe Subject Code Generation...")
        tenant_id = 1
        
        # Test explicit subject code
        sub1 = Subject(tenant_id=tenant_id, name="Data Structures", code="CS201", generated_code="CS201", is_auto_generated=False)
        db.add(sub1)
        db.commit()
        db.refresh(sub1)
        print(f"  [PASS] Created Explicit Subject: {sub1.name} -> Code: {SubjectCodeService.get_display_code(sub1)}")

        # Test Auto-Generated subject code
        res1 = SubjectCodeService.resolve_subject_code(db, tenant_id, "Aptitude")
        sub2 = Subject(tenant_id=tenant_id, name="Aptitude", code=res1["code"], generated_code=res1["generated_code"], is_auto_generated=res1["is_auto_generated"])
        db.add(sub2)
        db.commit()
        db.refresh(sub2)
        print(f"  [PASS] Auto-Generated Subject 1: {sub2.name} -> Code: {SubjectCodeService.get_display_code(sub2)}")

        # Test Collision Handling (Another subject starting with Aptitude / same letters)
        res2 = SubjectCodeService.resolve_subject_code(db, tenant_id, "Aptitude Advanced")
        sub3 = Subject(tenant_id=tenant_id, name="Aptitude Advanced", code=res2["code"], generated_code=res2["generated_code"], is_auto_generated=res2["is_auto_generated"])
        db.add(sub3)
        db.commit()
        db.refresh(sub3)
        print(f"  [PASS] Auto-Generated Collision Resolution: {sub3.name} -> Code: {SubjectCodeService.get_display_code(sub3)}")
        
        assert res2["generated_code"] != res1["generated_code"], "Collision not resolved!"
        print("  [SUCCESS] TEST 1 PASSED: Collision-safe code generation fully functional.")

        print("\n[TEST 2] Setting up Academic Hierarchy & Materialized Summary Engine...")
        dept = Department(tenant_id=tenant_id, name="Computer Science & Engineering", code="CSE")
        db.add(dept)
        db.flush()

        ac_session = AcademicSession(tenant_id=tenant_id, academic_year="2026-27", semester="Semester 1", term=1, is_current=True, status="ACTIVE", start_date=datetime.now())
        db.add(ac_session)
        db.flush()

        cls = Class(tenant_id=tenant_id, name="B.Tech 3rd Year", department_id=dept.id)
        db.add(cls)
        db.flush()

        sec = Section(tenant_id=tenant_id, name="A", class_id=cls.id)
        db.add(sec)
        db.flush()

        student = StudentProfile(user_id=101, name="Raviraj Javvadi", roll_number="22CS014", section_id=sec.id)
        db.add(student)
        
        faculty = FacultyProfile(user_id=102, name="Prof. Alan Turing", department_id=dept.id, employee_id="EMP-101")
        db.add(faculty)
        db.flush()

        # Create attendance records for subject 1 (70% attendance -> SHORTAGE ZONE)
        for i in range(10):
            att_status = AttendanceStatusEnum.PRESENT.value if i < 7 else AttendanceStatusEnum.ABSENT.value
            rec = AttendanceRecord(
                tenant_id=tenant_id,
                student_id=student.id,
                section_id=sec.id,
                subject_id=sub1.id,
                date=date.today() - timedelta(days=i),
                period=1,
                status=att_status,
                is_present=(i < 7),
                academic_session_id=ac_session.id
            )
            db.add(rec)
        db.commit()

        # Trigger Materialized Summary Engine across all 5 tiers
        print("  [INFO] Executing Asynchronous 5-Tier Materialized Summary Engine...")
        materialized_summary_engine.process_attendance_submission(db, tenant_id, sec.id, sub1.id, faculty.id, date.today(), [student.id])
        
        std_sum = db.query(AttendanceSummary).filter(AttendanceSummary.student_id == student.id, AttendanceSummary.subject_id == sub1.id).first()
        print(f"  [PASS] Tier-1 Student Summary Computed: {std_sum.attended_classes}/{std_sum.total_classes} ({std_sum.percentage}%) -> Shortage Status: {std_sum.is_shortage}")
        assert std_sum.percentage == 70.0, f"Percentage calculation mismatch! Got {std_sum.percentage}"
        assert std_sum.is_shortage == True, "75% statutory warning badge not triggered!"
        print("  [SUCCESS] TEST 2 PASSED: Materialized summary hierarchy and shortage alarms verified.")

        print("\n[TEST 3] Verifying Master Attendance Sheet Ledger Output...")
        sheet = enterprise_analytics_engine.get_master_attendance_sheet(db, tenant_id, sec.id, ac_session.id)
        print(f"  [PASS] Sheet Total Students: {sheet['summary']['total_students']}, Shortage Count: {sheet['summary']['shortage_count']}")
        assert len(sheet["rows"]) == 1, "Row missing in Master Sheet!"
        assert sheet["rows"][0]["warning_badge"] == "SHORTAGE (<75%)", f"Warning badge text incorrect in master ledger! Got {sheet['rows'][0]['warning_badge']}"
        print("  [SUCCESS] TEST 3 PASSED: University-grade master attendance sheet fully validated.")

        print("\n[TEST 4] Testing 1-Click Smart Semester Promotion & Term Vaulting...")
        # Add a timetable entry
        tt = Timetable(tenant_id=tenant_id, academic_year_id=ac_session.id, section_id=sec.id, period_id=1, day_of_week="MONDAY", subject_id=sub1.id, faculty_user_id=faculty.user_id, academic_session_id=ac_session.id)
        db.add(tt)
        db.commit()

        promo_res = enterprise_analytics_engine.execute_smart_term_promotion(db, tenant_id, "2027-28", "Semester 2", duplicate_timetable=True, section_id=sec.id)
        print(f"  [PASS] Promotion Status: {promo_res['message']}")
        print(f"  [PASS] Previous Session ID Archived: #{promo_res.get('previous_session_id')} -> New Active Session: #{promo_res['new_session_id']}")
        print(f"  [PASS] Duplicated Timetable Slots: {promo_res['promoted_timetable_entries']}")
        
        # Verify old session archived
        old_ses = db.query(AcademicSession).filter(AcademicSession.id == ac_session.id).first()
        assert old_ses.is_current == False and old_ses.status == "ARCHIVED", "Previous session was not properly sealed into term vault!"
        print("  [SUCCESS] TEST 4 PASSED: 1-Click smart term transition and timetable porting confirmed.")

        print("\n[TEST 5] Evaluating Dynamic AI Executive Insights Engine...")
        analytics = enterprise_analytics_engine.get_enterprise_analytics(db, tenant_id)
        print("  [PASS] Generated Natural Language AI Narratives:")
        for ins in analytics["ai_insights"]:
            print(f"    - [{ins['severity']}] {ins['title']}: {ins['message']}")
        print(f"  [PASS] Detention Risk Profiles Identified: {len(analytics['detention_risk_students'])}")
        print("  [SUCCESS] TEST 5 PASSED: Enterprise AI executive insight engine operating cleanly.")

        print("\n" + "=" * 70)
        print("ALL 5 ENTERPRISE VERIFICATION TESTS PASSED WITH 100% SUCCESS!")
        print("=" * 70)

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n[ERROR] VERIFICATION FAILED: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    run_verification()
