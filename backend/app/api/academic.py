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

@router.post("/classes", status_code=status.HTTP_201_CREATED)
def create_class(
    request: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    new_class = Class(name=request.name, department_id=request.department_id, tenant_id=current_user.tenant_id)
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class

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
