from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from datetime import date
from typing import List
from app.db.database import get_db
from app.models.attendance import AttendanceRecord, AttendanceStatusEnum
from app.models.academic import AcademicSession
from app.models.user import User, UserRole
from app.models.profiles import StudentProfile
from app.schemas.attendance import AttendanceSubmit, SmartAttendanceSubmit
from app.api.deps import get_current_faculty, get_current_management_or_faculty
from app.services.sms import queue_sms
from app.services.subject_code_service import SubjectCodeService
from app.engines.materialized_summary_engine import materialized_summary_engine

router = APIRouter()

@router.get("/status", status_code=status.HTTP_200_OK)
def get_attendance_status(
    section_id: int,
    date: str,
    period: int = None,
    db: Session = Depends(get_db),
    current_faculty: User = Depends(get_current_faculty)
):
    from datetime import datetime
    try:
        query_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
    query = db.query(AttendanceRecord).filter(
        AttendanceRecord.section_id == section_id,
        AttendanceRecord.date == query_date
    )
    
    if period is not None:
        query = query.filter(AttendanceRecord.period == period)
        
    records = query.all()
    
    if not records:
        return {"marked": False, "records": []}
        
    return {
        "marked": True,
        "records": [
            {"student_id": r.student_id, "is_present": r.is_present}
            for r in records
        ]
    }

@router.get("/stats/today")
def get_today_stats(
    tenant_id: int = None,
    db: Session = Depends(get_db),
    current_management: User = Depends(get_current_management_or_faculty)
):
    from sqlalchemy import func
    from zoneinfo import ZoneInfo
    from datetime import datetime
    today = datetime.now(ZoneInfo('Asia/Kolkata')).date()
    
    # SuperAdmin, Admin, Management or Principal can specify tenant_id to view overview, or auto-detect active tenant
    active_tenant_id = current_management.tenant_id
    if tenant_id and current_management.role in ["SUPERADMIN", "ADMIN", "MANAGEMENT", "PRINCIPAL"]:
        active_tenant_id = tenant_id
    else:
        from app.models.tenant import Institution
        from app.models.academic import Section
        sec_count = db.query(Section).filter(Section.tenant_id == active_tenant_id).count()
        if sec_count == 0 or active_tenant_id == 1:
            first_tenant = db.query(Institution).filter(Institution.subdomain != "system").first()
            if first_tenant:
                active_tenant_id = first_tenant.id
            else:
                any_tenant = db.query(Section.tenant_id).filter(Section.tenant_id != None).first()
                if any_tenant:
                    active_tenant_id = any_tenant[0]
    
    from app.models.academic import Section, Class, Department
    # Total students in tenant (fallback to checking all student profiles if tenant filter yields 0)
    total_students = db.query(func.count(StudentProfile.id)) \
        .join(Section, StudentProfile.section_id == Section.id) \
        .filter(Section.tenant_id == active_tenant_id).scalar() or 0
    if total_students == 0:
        total_students = db.query(func.count(StudentProfile.id)).scalar() or 0
        
    # Attendance for today (check Period 1 or any period today)
    attendance_records = db.query(AttendanceRecord).filter(
        AttendanceRecord.tenant_id == active_tenant_id,
        AttendanceRecord.date == today
    ).all()
    if not attendance_records:
        attendance_records = db.query(AttendanceRecord).filter(AttendanceRecord.date == today).all()
    # If no attendance is marked for today yet, fetch the latest recorded date in the system so the dashboard is never empty!
    if not attendance_records:
        latest_rec = db.query(AttendanceRecord).order_by(AttendanceRecord.date.desc()).first()
        if latest_rec:
            attendance_records = db.query(AttendanceRecord).filter(AttendanceRecord.date == latest_rec.date).all()
    
    present_today = sum(1 for r in attendance_records if r.is_present)
    absent_today = sum(1 for r in attendance_records if not r.is_present)
    
    # Low attendance alerts (students with < 75% attendance)
    from app.models.notification import NotificationLog
    from sqlalchemy import case

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
    if not attendance_stats:
        attendance_stats = db.query(
            StudentProfile.id,
            StudentProfile.name,
            func.coalesce(Section.name, "General").label("section_name"),
            func.count(AttendanceRecord.id).label("total"),
            func.sum(case((AttendanceRecord.is_present == True, 1), else_=0)).label("present")
        ).outerjoin(Section, StudentProfile.section_id == Section.id) \
         .join(AttendanceRecord, StudentProfile.id == AttendanceRecord.student_id) \
         .group_by(StudentProfile.id, StudentProfile.name, Section.name).all()

    alerts = []
    for stat in attendance_stats:
        if stat.total > 0:
            rate = (stat.present / stat.total) * 100
            if rate < 75:
                alerts.append({
                    "name": stat.name or f"Student #{stat.id}",
                    "class": f"Section {stat.section_name}",
                    "rate": f"{rate:.1f}%",
                    "status": "Critical" if rate < 50 else "Warning"
                })
                 
    alerts.sort(key=lambda x: float(x["rate"].replace("%", "")))
    
    # Recent Notifications (fallback to all notifications if none for active_tenant_id)
    recent_logs = db.query(NotificationLog) \
        .filter(NotificationLog.tenant_id == active_tenant_id) \
        .order_by(NotificationLog.created_at.desc()) \
        .limit(5).all()
    if not recent_logs:
        recent_logs = db.query(NotificationLog) \
            .order_by(NotificationLog.created_at.desc()) \
            .limit(5).all()
        
    notifications = []
    for log in recent_logs:
        notifications.append({
            "id": log.id,
            "type": log.channel,
            "status": log.status,
            "content": log.message,
            "time": log.created_at.strftime("%I:%M %p") if log.created_at else ""
        })

    # Department-wise morning attendance (Period 1)
    from app.models.academic import Class, Department
    
    all_students_dept = db.query(
        Department.name,
        func.count(StudentProfile.id)
    ).join(Section, StudentProfile.section_id == Section.id) \
     .join(Class, Section.class_id == Class.id) \
     .join(Department, Class.department_id == Department.id) \
     .filter(Section.tenant_id == active_tenant_id) \
     .group_by(Department.name).all()
    if not all_students_dept:
        all_students_dept = db.query(
            Department.name,
            func.count(StudentProfile.id)
        ).outerjoin(Class, Class.department_id == Department.id) \
         .outerjoin(Section, Section.class_id == Class.id) \
         .outerjoin(StudentProfile, StudentProfile.section_id == Section.id) \
         .group_by(Department.name).all()
     
    dept_totals = {name: count for name, count in all_students_dept}
    
    present_dept_stats = db.query(
        Department.name,
        func.count(AttendanceRecord.id)
    ).join(Section, AttendanceRecord.section_id == Section.id) \
     .join(Class, Section.class_id == Class.id) \
     .join(Department, Class.department_id == Department.id) \
     .filter(
        AttendanceRecord.is_present == True,
        AttendanceRecord.date == (attendance_records[0].date if attendance_records else today)
    ).group_by(Department.name).all()
    
    dept_presents = {name: count for name, count in present_dept_stats}
    
    department_overview = []
    for dept_name, total in dept_totals.items():
        present = dept_presents.get(dept_name, 0)
        department_overview.append({
            "department": dept_name,
            "present": present,
            "total": total,
            "rate": round((present / total * 100), 1) if total > 0 else 0
        })
        
    department_overview.sort(key=lambda x: x["rate"])

    return {
        "total_students": total_students,
        "present_today": present_today,
        "absent_today": absent_today,
        "attendance_rate": f"{(present_today / total_students * 100):.1f}%" if total_students > 0 else "0%",
        "alerts": alerts[:5], # top 5 lowest
        "notifications": notifications,
        "department_overview": department_overview
    }

@router.post("/submit")
def submit_attendance(
    attendance_data: AttendanceSubmit,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_faculty: User = Depends(get_current_faculty)
):
    # Determine active academic session for term tracking
    active_session = db.query(AcademicSession).filter(
        AcademicSession.tenant_id == current_faculty.tenant_id,
        AcademicSession.is_current == True
    ).first()
    session_id_val = active_session.id if active_session else None

    # Process the attendance list
    absent_student_ids = []
    
    # Pre-fetch subject_id based on Timetable for this section and period
    subject_id = None
    if attendance_data.period is not None:
        from app.models.erp_academic import Timetable, Period
        from zoneinfo import ZoneInfo
        from datetime import datetime
        
        ist = ZoneInfo('Asia/Kolkata')
        day_name = datetime.now(ist).strftime("%A").upper()
        
        period = db.query(Period).filter(Period.period_number == attendance_data.period).first()
        if period:
            target_date_obj = attendance_data.date
            target_day_name = target_date_obj.strftime("%A").upper()
            tt = db.query(Timetable).filter(
                Timetable.section_id == attendance_data.section_id,
                Timetable.period_id == period.id,
                Timetable.day_of_week == target_day_name
            ).first()
            if tt:
                subject_id = tt.subject_id
                
    subject_name = "Class"
    subj_display = "Class"
    if subject_id:
        from app.models.erp_academic import Subject
        subj = db.query(Subject).filter(Subject.id == subject_id).first()
        if subj:
            subject_name = subj.name
            subj_display = f"{subj.name} ({SubjectCodeService.get_display_code(subj)})"
    
    for record in attendance_data.records:
        query = db.query(AttendanceRecord).filter(
            AttendanceRecord.student_id == record.student_id,
            AttendanceRecord.date == attendance_data.date
        )
        if attendance_data.period is not None:
            query = query.filter(AttendanceRecord.period == attendance_data.period)
        
        db_record = query.first()
        status_enum = AttendanceStatusEnum.PRESENT.value if record.is_present else AttendanceStatusEnum.ABSENT.value
        
        if db_record:
            db_record.is_present = record.is_present
            db_record.status = status_enum
            db_record.marked_by = current_faculty.id
            db_record.academic_session_id = session_id_val
            if subject_id:
                db_record.subject_id = subject_id
        else:
            new_record = AttendanceRecord(
                tenant_id=current_faculty.tenant_id,
                student_id=record.student_id,
                section_id=attendance_data.section_id,
                date=attendance_data.date,
                period=attendance_data.period,
                subject_id=subject_id,
                academic_session_id=session_id_val,
                is_present=record.is_present,
                status=status_enum,
                marked_by=current_faculty.id
            )
            db.add(new_record)
            
        # Add TimelineEvent
        from app.models.communication import TimelineEvent
        student_prof = db.query(StudentProfile).filter(StudentProfile.id == record.student_id).first()
        if student_prof and student_prof.user_id:
            event_type = "ATTENDANCE_PRESENT" if record.is_present else "ATTENDANCE_ABSENT"
            desc = f"Marked Present for {subj_display}" if record.is_present else f"Marked Absent for {subj_display}"
            t_event = TimelineEvent(
                tenant_id=current_faculty.tenant_id,
                user_id=student_prof.user_id,
                event_type=event_type,
                description=desc
            )
            db.add(t_event)

        if not record.is_present:
            absent_student_ids.append(record.student_id)
            
            # Send Notification to Parent
            if student_prof and student_prof.user_id:
                from app.models.notification import NotificationLog
                from app.models.profiles import ParentStudentLink, ParentProfile
                
                link = db.query(ParentStudentLink).filter(ParentStudentLink.student_id == student_prof.id).first()
                if link:
                    parent = db.query(ParentProfile).filter(ParentProfile.id == link.parent_id).first()
                    if parent:
                        parent_user = db.query(User).filter(User.id == parent.user_id).first()
                        if parent_user:
                            notif = NotificationLog(
                                tenant_id=current_faculty.tenant_id,
                                student_id=student_prof.id,
                                channel="PUSH",
                                recipient=parent_user.email or parent_user.mobile_number,
                                status="SENT",
                                event_type="ATTENDANCE",
                                title=f"Absence Alert: {subj_display}",
                                message=f"Your child {student_prof.name} was marked ABSENT for {subj_display} on {attendance_data.date} (Period {attendance_data.period or 'Daily'})."
                            )
                            db.add(notif)
            
    db.commit()
    
    # Trigger Materialized Summary Engine updates
    all_std_ids = [r.student_id for r in attendance_data.records]
    if all_std_ids:
        materialized_summary_engine.process_attendance_submission(
            db, current_faculty.tenant_id, attendance_data.section_id, subject_id, current_faculty.id, attendance_data.date, all_std_ids
        )
    
    # Trigger background tasks using FastAPI for absent students
    for student_id in absent_student_ids:
        background_tasks.add_task(queue_sms, student_id, str(attendance_data.date), current_faculty.tenant_id)

    return {"message": "Attendance saved successfully", "absent_count": len(absent_student_ids)}

@router.post("/submit/smart")
def submit_smart_attendance(
    attendance_data: SmartAttendanceSubmit,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_faculty: User = Depends(get_current_faculty)
):
    """
    BookMyShow Style: Faculty only submits the array of absent student IDs.
    The backend automatically defaults all other students in the section to Present.
    """
    active_session = db.query(AcademicSession).filter(
        AcademicSession.tenant_id == current_faculty.tenant_id,
        AcademicSession.is_current == True
    ).first()
    session_id_val = active_session.id if active_session else None

    # Pre-fetch subject_id based on Timetable for this section and period
    subject_id = None
    if attendance_data.period is not None:
        from app.models.erp_academic import Timetable, Period
        from zoneinfo import ZoneInfo
        from datetime import datetime
        
        period = db.query(Period).filter(Period.period_number == attendance_data.period).first()
        if period:
            target_date_obj = attendance_data.date
            target_day_name = target_date_obj.strftime("%A").upper()
            tt = db.query(Timetable).filter(
                Timetable.section_id == attendance_data.section_id,
                Timetable.period_id == period.id,
                Timetable.day_of_week == target_day_name
            ).first()
            if tt:
                subject_id = tt.subject_id
                
    subj_display = "Class"
    if subject_id:
        from app.models.erp_academic import Subject
        subj = db.query(Subject).filter(Subject.id == subject_id).first()
        if subj:
            subj_display = f"{subj.name} ({SubjectCodeService.get_display_code(subj)})"

    all_students = db.query(StudentProfile).filter(StudentProfile.section_id == attendance_data.section_id).all()
    newly_absent_students = []
    
    for student in all_students:
        is_present = student.id not in attendance_data.absent_student_ids
        status_enum = AttendanceStatusEnum.PRESENT.value if is_present else AttendanceStatusEnum.ABSENT.value
        
        query = db.query(AttendanceRecord).filter(
            AttendanceRecord.student_id == student.id,
            AttendanceRecord.date == attendance_data.date
        )
        if attendance_data.period is not None:
            query = query.filter(AttendanceRecord.period == attendance_data.period)
        else:
            query = query.filter(AttendanceRecord.period == None)
            
        db_record = query.first()
        
        if db_record:
            if db_record.is_present and not is_present:
                newly_absent_students.append(student)
            
            db_record.is_present = is_present
            db_record.status = status_enum
            db_record.marked_by = current_faculty.id
            db_record.academic_session_id = session_id_val
            if subject_id:
                db_record.subject_id = subject_id
        else:
            if not is_present:
                newly_absent_students.append(student)
                
            new_record = AttendanceRecord(
                tenant_id=current_faculty.tenant_id,
                student_id=student.id,
                section_id=attendance_data.section_id,
                date=attendance_data.date,
                period=attendance_data.period,
                subject_id=subject_id,
                academic_session_id=session_id_val,
                is_present=is_present,
                status=status_enum,
                marked_by=current_faculty.id
            )
            db.add(new_record)
            
        # Add TimelineEvent
        from app.models.communication import TimelineEvent
        if student.user_id:
            event_type = "ATTENDANCE_PRESENT" if is_present else "ATTENDANCE_ABSENT"
            desc = f"Marked {'Present' if is_present else 'Absent'} for {subj_display}"
            t_event = TimelineEvent(
                tenant_id=current_faculty.tenant_id,
                user_id=student.user_id,
                event_type=event_type,
                description=desc
            )
            db.add(t_event)
            
        # Generate immutable absence alert for parent if newly absent
        if not is_present and student in newly_absent_students and student.user_id:
            from app.models.notification import NotificationLog
            from app.models.profiles import ParentStudentLink, ParentProfile
            link = db.query(ParentStudentLink).filter(ParentStudentLink.student_id == student.id).first()
            if link:
                parent = db.query(ParentProfile).filter(ParentProfile.id == link.parent_id).first()
                if parent:
                    parent_user = db.query(User).filter(User.id == parent.user_id).first()
                    if parent_user:
                        notif = NotificationLog(
                            tenant_id=current_faculty.tenant_id,
                            student_id=student.id,
                            channel="PUSH",
                            recipient=parent_user.email or parent_user.mobile_number,
                            status="SENT",
                            event_type="ATTENDANCE",
                            title=f"Absence Alert: {subj_display}",
                            message=f"Your child {student.name} was marked ABSENT for {subj_display} on {attendance_data.date} (Period {attendance_data.period or 'Daily'})."
                        )
                        db.add(notif)

    db.commit()
    
    # Trigger Materialized Summary Engine updates
    all_std_ids = [s.id for s in all_students]
    if all_std_ids:
        materialized_summary_engine.process_attendance_submission(
            db, current_faculty.tenant_id, attendance_data.section_id, subject_id, current_faculty.id, attendance_data.date, all_std_ids
        )
    
    # Trigger background SMS for newly added absentees only
    for student in newly_absent_students:
        background_tasks.add_task(queue_sms, student.id, str(attendance_data.date), current_faculty.tenant_id, attendance_data.period)

    return {"message": "Smart Attendance saved successfully", "absent_count": len(newly_absent_students)}

@router.get("/report")
def get_attendance_report(
    section_id: int, 
    report_date: date, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_management_or_faculty)
):
    records = db.query(AttendanceRecord).filter(
        AttendanceRecord.section_id == section_id,
        AttendanceRecord.date == report_date,
        AttendanceRecord.tenant_id == current_user.tenant_id
    ).all()
    
    return records
@router.get("/reports/weekly")
def get_weekly_report(
    db: Session = Depends(get_db),
    current_management: User = Depends(get_current_management_or_faculty)
):
    """
    Returns the attendance rate for the last 5 days (e.g., Mon-Fri).
    """
    from datetime import timedelta
    from sqlalchemy import func
    
    today = date.today()
    days = []
    for i in range(4, -1, -1):
        day = today - timedelta(days=i)
        
        # Get total records for this day
        records = db.query(AttendanceRecord).filter(
            AttendanceRecord.tenant_id == current_management.tenant_id,
            AttendanceRecord.date == day
        ).all()
        
        total = len(records)
        present = sum(1 for r in records if r.is_present)
        rate = int((present / total * 100)) if total > 0 else 0
        
        days.append({
            "name": day.strftime("%a"), # Mon, Tue, etc
            "attendance": rate
        })
        
    return days
