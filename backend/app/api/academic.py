from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User, UserRole
from app.models.academic import Class, Section, AcademicYear
from app.models.profiles import StudentProfile

router = APIRouter()

class StudentBulkCreate(BaseModel):
    class_id: int
    section_id: int
    roll_numbers: List[str]

@router.post("/students/bulk", status_code=status.HTTP_201_CREATED)
def bulk_create_students(
    request: StudentBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Smart Onboarding: Create student profiles instantly just using Roll Numbers.
    Details like Name and Parent Mobile can be updated later.
    """
    if current_user.role not in [UserRole.SUPERADMIN.value, UserRole.MANAGEMENT.value, UserRole.ADMIN.value]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to manage students")
        
    section = db.query(Section).filter(Section.id == request.section_id, Section.tenant_id == current_user.tenant_id).first()
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")
        
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

@router.put("/students/{student_id}", status_code=status.HTTP_200_OK)
def update_student_details(
    student_id: int,
    request: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Step 2 of Smart Onboarding: Management clicks a roll number to add details.
    """
    if current_user.role not in [UserRole.SUPERADMIN.value, UserRole.MANAGEMENT.value, UserRole.ADMIN.value]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to manage students")
        
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        
    student.name = request.name
    student.parent_mobile = request.parent_mobile
    db.commit()
    return {"message": "Student details updated successfully"}
