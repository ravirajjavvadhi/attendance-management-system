from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.api.deps import get_current_admin
from app.models.user import User, UserRole
from app.models.academic import Class, Section, AcademicYear, Department
from app.models.profiles import StudentProfile

router = APIRouter()

class DepartmentCreate(BaseModel):
    name: str
    code: Optional[str] = None

class ClassCreate(BaseModel):
    name: str
    department_id: Optional[int] = None

class SectionCreate(BaseModel):
    name: str
    class_id: int

@router.get("/departments")
def get_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return db.query(Department).filter(Department.tenant_id == current_user.tenant_id).all()

@router.post("/departments", status_code=status.HTTP_201_CREATED)
def create_department(
    request: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    dept = Department(name=request.name, code=request.code, tenant_id=current_user.tenant_id)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept

@router.delete("/departments/{department_id}", status_code=status.HTTP_200_OK)
def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    dept = db.query(Department).filter(Department.id == department_id, Department.tenant_id == current_user.tenant_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    db.delete(dept)
    db.commit()
    return {"message": "Department deleted"}

@router.post("/classes")
def create_class(
    cls: ClassCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    new_class = Class(name=cls.name, department_id=cls.department_id, tenant_id=current_admin.tenant_id)
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class

@router.put("/classes/{class_id}")
def update_class(
    class_id: int,
    cls_update: ClassCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    db_class = db.query(Class).filter(Class.id == class_id, Class.tenant_id == current_admin.tenant_id).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    
    db_class.name = cls_update.name
    if cls_update.department_id:
        db_class.department_id = cls_update.department_id
        
    db.commit()
    db.refresh(db_class)
    return db_class

@router.get("/classes")
def get_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return db.query(Class).filter(Class.tenant_id == current_user.tenant_id).all()


@router.post("/sections", status_code=status.HTTP_201_CREATED)
def create_section(
    request: SectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    # Verify class belongs to tenant
    cls = db.query(Class).filter(Class.id == request.class_id, Class.tenant_id == current_user.tenant_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
        
    new_section = Section(name=request.name, class_id=cls.id, tenant_id=current_user.tenant_id)
    db.add(new_section)
    db.commit()
    db.refresh(new_section)
    return new_section

@router.post("/sections/{section_id}/assign", status_code=status.HTTP_200_OK)
def assign_faculty_to_section(
    section_id: int,
    faculty_user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    from app.models.profiles import FacultySectionAssignment
    # Verify section belongs to tenant
    query = db.query(Section).filter(Section.id == section_id)
    if current_user.role != UserRole.SUPERADMIN.value:
        query = query.filter(Section.tenant_id == current_user.tenant_id)
    section = query.first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
        
    # Check if already assigned
    existing = db.query(FacultySectionAssignment).filter(
        FacultySectionAssignment.faculty_user_id == faculty_user_id,
        FacultySectionAssignment.section_id == section_id
    ).first()
    
    if not existing:
        assignment = FacultySectionAssignment(faculty_user_id=faculty_user_id, section_id=section_id)
        db.add(assignment)
        db.commit()
    return {"message": "Faculty assigned to section successfully"}

@router.delete("/sections/{section_id}/assign/{faculty_user_id}", status_code=status.HTTP_200_OK)
def revoke_faculty_from_section(
    section_id: int,
    faculty_user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    from app.models.profiles import FacultySectionAssignment
    # Verify section belongs to tenant
    query = db.query(Section).filter(Section.id == section_id)
    if current_user.role != UserRole.SUPERADMIN.value:
        query = query.filter(Section.tenant_id == current_user.tenant_id)
    section = query.first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
        
    assignment = db.query(FacultySectionAssignment).filter(
        FacultySectionAssignment.faculty_user_id == faculty_user_id,
        FacultySectionAssignment.section_id == section_id
    ).first()
    
    if assignment:
        db.delete(assignment)
        db.commit()
    return {"message": "Assignment revoked successfully"}

from app.api.deps import get_current_management_or_faculty

@router.get("/sections")
def get_sections(
    class_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_management_or_faculty)
):
    from app.models.profiles import FacultyProfile, FacultySectionAssignment
    query = db.query(Section).filter(Section.tenant_id == current_user.tenant_id)
    if class_id:
        query = query.filter(Section.class_id == class_id)
        
    if current_user.role == "faculty":
        # Check access level
        profile = db.query(FacultyProfile).filter(FacultyProfile.user_id == current_user.id).first()
        if profile and profile.access_level != "FULL_INSTITUTION_ACCESS":
            # Filter to assigned sections only
            assigned_section_ids = [a.section_id for a in db.query(FacultySectionAssignment).filter(FacultySectionAssignment.faculty_user_id == current_user.id).all()]
            query = query.filter(Section.id.in_(assigned_section_ids))
            
    return query.all()

class StudentBulkCreate(BaseModel):
    class_id: int
    section_id: int
    roll_numbers: List[str]

@router.post("/students/bulk", status_code=status.HTTP_201_CREATED)
def bulk_create_students(
    request: StudentBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Smart Onboarding: Create student profiles instantly just using Roll Numbers.
    Details like Name and Parent Mobile can be updated later.
    """
    section = db.query(Section).filter(Section.id == request.section_id, Section.tenant_id == current_user.tenant_id).first()
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found or access denied")
        
    created_count = 0
    for roll in request.roll_numbers:
        exists = db.query(StudentProfile).filter(
            StudentProfile.section_id == section.id,
            StudentProfile.roll_number == roll
        ).first()
        
        if not exists:
            student = StudentProfile(
                section_id=section.id,
                roll_number=roll
            )
            db.add(student)
            created_count += 1
            
    db.commit()
    return {"message": f"Successfully onboarded {created_count} students.", "created_count": created_count}

class StudentUpdate(BaseModel):
    name: str
    parent_mobile: str
    parent_email: Optional[str] = None

@router.put("/students/{student_id}", status_code=status.HTTP_200_OK)
def update_student_details(
    student_id: int,
    request: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    # Enforce multi-tenant boundaries by joining StudentProfile with Section and checking tenant_id
    student = db.query(StudentProfile).join(Section).filter(
        StudentProfile.id == student_id,
        Section.tenant_id == current_user.tenant_id
    ).first()
    
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found or access denied")
        
    student.name = request.name
    student.parent_mobile = request.parent_mobile
    student.parent_email = request.parent_email
    
    # Auto-provision parent user and profile if parent_email is specified
    if request.parent_email:
        from app.models.user import User, UserRole
        from app.models.profiles import ParentProfile, ParentStudentLink
        from app.core.security import get_password_hash
        
        # Check if parent user already exists
        parent_user = db.query(User).filter(User.email == request.parent_email).first()
        if not parent_user:
            parent_user = User(
                email=request.parent_email,
                mobile_number=request.parent_mobile,
                hashed_password=get_password_hash("123456"),
                role=UserRole.PARENT.value,
                is_active=True,
                tenant_id=current_user.tenant_id
            )
            db.add(parent_user)
            db.commit()
            db.refresh(parent_user)
            
        # Ensure ParentProfile exists
        parent_profile = db.query(ParentProfile).filter(ParentProfile.user_id == parent_user.id).first()
        if not parent_profile:
            parent_profile = ParentProfile(
                user_id=parent_user.id,
                name=student.parent_name or "Parent",
                email=request.parent_email
            )
            db.add(parent_profile)
            db.commit()
            db.refresh(parent_profile)
            
        # Ensure ParentStudentLink exists
        link = db.query(ParentStudentLink).filter(
            ParentStudentLink.parent_id == parent_profile.id,
            ParentStudentLink.student_id == student.id
        ).first()
        if not link:
            link = ParentStudentLink(
                parent_id=parent_profile.id,
                student_id=student.id,
                relationship="PRIMARY",
                is_primary=True
            )
            db.add(link)
            db.commit()
            
    db.commit()
    return {"message": "Student details updated successfully"}

@router.delete("/students/{student_id}", status_code=status.HTTP_200_OK)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    student = db.query(StudentProfile).join(Section).filter(
        StudentProfile.id == student_id,
        Section.tenant_id == current_user.tenant_id
    ).first()
    
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        
    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}

@router.get("/students", status_code=status.HTTP_200_OK)
def get_students(
    section_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_management_or_faculty)
):
    from app.models.profiles import FacultyProfile, FacultySectionAssignment
    query = db.query(StudentProfile, Section).join(Section).filter(
        Section.tenant_id == current_user.tenant_id
    )
    
    if section_id:
        query = query.filter(Section.id == section_id)
        
    if current_user.role == UserRole.FACULTY.value:
        # Check access level
        profile = db.query(FacultyProfile).filter(FacultyProfile.user_id == current_user.id).first()
        if profile and profile.access_level != "FULL_INSTITUTION_ACCESS":
            assigned_section_ids = [a.section_id for a in db.query(FacultySectionAssignment).filter(FacultySectionAssignment.faculty_user_id == current_user.id).all()]
            query = query.filter(Section.id.in_(assigned_section_ids))
    
    query = query.order_by(StudentProfile.roll_number.asc())
    students = query.all()
    
    result = []
    for student, section in students:
        result.append({
            "id": student.id,
            "roll_number": student.roll_number,
            "name": student.name or "Not Provided",
            "parent_mobile": student.parent_mobile,
            "parent_email": student.parent_email,
            "section_name": section.name,
            "section_id": section.id,
            "status": "Active"
        })
        
    return result

class SubjectMarkInput(BaseModel):
    subject_id: int
    marks_obtained: float
    grade: str

class MarksSubmit(BaseModel):
    student_id: int
    semester_id: int
    sgpa: float
    credits_earned: int
    marks: List[SubjectMarkInput]

@router.post("/faculty/marks", status_code=status.HTTP_201_CREATED)
def submit_marks(
    request: MarksSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_management_or_faculty)
):
    from app.models.erp_academic import SemesterResult, SubjectMark
    
    # Check if result already exists
    result = db.query(SemesterResult).filter(
        SemesterResult.student_id == request.student_id,
        SemesterResult.semester_id == request.semester_id
    ).first()
    
    if result:
        result.sgpa = request.sgpa
        result.credits_earned = request.credits_earned
    else:
        result = SemesterResult(
            student_id=request.student_id,
            semester_id=request.semester_id,
            sgpa=request.sgpa,
            credits_earned=request.credits_earned
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        
    for mark in request.marks:
        sub_mark = db.query(SubjectMark).filter(
            SubjectMark.result_id == result.id,
            SubjectMark.subject_id == mark.subject_id
        ).first()
        
        if sub_mark:
            sub_mark.marks_obtained = mark.marks_obtained
            sub_mark.grade = mark.grade
        else:
            new_mark = SubjectMark(
                result_id=result.id,
                subject_id=mark.subject_id,
                marks_obtained=mark.marks_obtained,
                grade=mark.grade
            )
            db.add(new_mark)
            
    db.commit()
    return {"message": "Marks updated successfully"}

class RemarkCreate(BaseModel):
    remark_text: str

@router.post("/faculty/students/{student_id}/remarks", status_code=status.HTTP_201_CREATED)
def add_faculty_remark(
    student_id: int,
    request: RemarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_management_or_faculty)
):
    from app.models.erp_academic import FacultyRemark
    
    remark = FacultyRemark(
        student_id=student_id,
        faculty_user_id=current_user.id,
        remark_text=request.remark_text
    )
    db.add(remark)
    db.commit()
    db.refresh(remark)
    return remark

@router.get("/faculty/live-class", status_code=status.HTTP_200_OK)
def get_faculty_live_class(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_management_or_faculty)
):
    from app.models.academic import Timetable, Period
    from zoneinfo import ZoneInfo
    from datetime import datetime
    
    ist = ZoneInfo('Asia/Kolkata')
    now_ist = datetime.now(ist)
    day_name = now_ist.strftime("%A").upper()
    now_time = now_ist.time()
    
    # Get all timetable entries for this faculty for today
    tt_entries = db.query(Timetable).filter(
        Timetable.faculty_user_id == current_user.id,
        Timetable.day_of_week == day_name
    ).all()
    
    for tt in tt_entries:
        period = db.query(Period).filter(Period.id == tt.period_id).first()
        if period and period.start_time and period.end_time:
            # We add a 10 minute buffer before class starts so they can prepare attendance
            # and a 10 minute buffer after it ends
            from datetime import timedelta, date, time
            
            # Combine with a dummy date to do timedelta math
            dummy_date = date(2000, 1, 1)
            start_dt = datetime.combine(dummy_date, period.start_time) - timedelta(minutes=10)
            end_dt = datetime.combine(dummy_date, period.end_time) + timedelta(minutes=10)
            now_dt = datetime.combine(dummy_date, now_time)
            
            if start_dt.time() <= now_dt.time() <= end_dt.time():
                from app.models.academic import Section, Class as AcademicClass, Department
                from app.models.erp_academic import Subject
                section = db.query(Section).filter(Section.id == tt.section_id).first()
                subject = db.query(Subject).filter(Subject.id == tt.subject_id).first()
                
                time_str = f"{period.start_time.strftime('%I:%M %p')} - {period.end_time.strftime('%I:%M %p')}"
                
                if section:
                    academic_class = db.query(AcademicClass).filter(AcademicClass.id == section.class_id).first()
                    department = db.query(Department).filter(Department.id == academic_class.department_id).first() if academic_class else None
                    
                    return {
                        "live": True,
                        "section_id": tt.section_id,
                        "period_number": period.period_number,
                        "section_name": section.name,
                        "year_name": academic_class.name if academic_class else "",
                        "department_name": department.name if department else "",
                        "subject_name": subject.name if subject else "Unknown",
                        "time": time_str
                    }
                else:
                    return {
                        "live": True,
                        "section_id": tt.section_id,
                        "period_number": period.period_number,
                        "subject_name": subject.name if subject else "Unknown",
                        "time": time_str
                    }
                
    return {"live": False}

@router.get("/faculty/weekly-schedule", status_code=status.HTTP_200_OK)
def get_faculty_weekly_schedule(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_management_or_faculty)
):
    from app.models.academic import Section, Class as AcademicClass, Department
    from app.models.erp_academic import Subject, Timetable, Period
    from zoneinfo import ZoneInfo
    from datetime import datetime, timedelta, date

    ist = ZoneInfo('Asia/Kolkata')
    now_ist = datetime.now(ist)
    current_day = now_ist.strftime("%A").upper()
    now_time = now_ist.time()

    tt_entries = db.query(Timetable).filter(
        Timetable.faculty_user_id == current_user.id
    ).all()

    schedule = {
        "MONDAY": [], "TUESDAY": [], "WEDNESDAY": [], 
        "THURSDAY": [], "FRIDAY": [], "SATURDAY": []
    }

    dummy_date = date(2000, 1, 1)

    for tt in tt_entries:
        if tt.day_of_week not in schedule:
            continue
            
        period = db.query(Period).filter(Period.id == tt.period_id).first()
        section = db.query(Section).filter(Section.id == tt.section_id).first()
        subject = db.query(Subject).filter(Subject.id == tt.subject_id).first()
        
        if not (period and section and subject):
            continue
            
        academic_class = db.query(AcademicClass).filter(AcademicClass.id == section.class_id).first()
        department = db.query(Department).filter(Department.id == academic_class.department_id).first() if academic_class else None
        
        time_str = f"{period.start_time.strftime('%I:%M %p')} - {period.end_time.strftime('%I:%M %p')}"
        
        # Calculate status
        class_status = "Upcoming"
        is_live = False
        
        if tt.day_of_week == current_day:
            start_dt = datetime.combine(dummy_date, period.start_time) - timedelta(minutes=10)
            end_dt = datetime.combine(dummy_date, period.end_time) + timedelta(minutes=10)
            now_dt = datetime.combine(dummy_date, now_time)
            
            if now_dt < start_dt:
                class_status = "Upcoming"
            elif start_dt <= now_dt <= end_dt:
                class_status = "Live Now"
                is_live = True
            else:
                class_status = "Completed"
        
        schedule[tt.day_of_week].append({
            "section_id": tt.section_id,
            "period_number": period.period_number,
            "subject_name": subject.name,
            "section_name": section.name,
            "year_name": academic_class.name if academic_class else "",
            "department_name": department.name if department else "",
            "time": time_str,
            "status": class_status,
            "is_live": is_live,
            "day": tt.day_of_week,
            "period_start": period.start_time.strftime('%H:%M')
        })

    # Sort each day's schedule by period start time
    for day in schedule:
        schedule[day] = sorted(schedule[day], key=lambda x: x["period_start"])

    return {
        "current_day": current_day,
        "schedule": schedule
    }
