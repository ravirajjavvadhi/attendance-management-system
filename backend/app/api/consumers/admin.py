from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.tenant import Institution, InstitutionModules
from app.models.erp_academic import Branch, Semester, Subject, Period
from app.models.academic import Department, AcademicYear
from pydantic import BaseModel
from typing import List

router = APIRouter()

class SmartBuildRequest(BaseModel):
    institution_type: str # e.g. "Engineering College"
    academic_year_name: str # e.g. "2024-2025"
    branches: List[str] # e.g. ["CSE", "ECE", "IT"]
    years: int # e.g. 4
    semesters_per_year: int # e.g. 2
    sections_per_branch: int # e.g. 3
    periods_per_day: int # e.g. 8

@router.get("/")
def get_admin_dashboard():
    return {"status": "ok", "message": "Admin API Gateway"}

@router.post("/{tenant_id}/smart-build")
def smart_build_institution(tenant_id: int, request: SmartBuildRequest, db: Session = Depends(get_db)):
    """
    Wizard Step 8: Auto-generate the complete ERP Academic Structure in under two minutes.
    """
    institution = db.query(Institution).filter(Institution.id == tenant_id).first()
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
        
    # Enable all ERP modules for this premium onboarding
    modules = InstitutionModules(tenant_id=tenant_id, has_parent_app=True, has_student_app=True, has_ai_analytics=True)
    db.add(modules)
    
    # 1. Create Academic Year
    acad_year = AcademicYear(tenant_id=tenant_id, name=request.academic_year_name, is_current=True)
    db.add(acad_year)
    db.commit()
    db.refresh(acad_year)
    
    # 2. Create Default Department
    dept = Department(tenant_id=tenant_id, name="General Academics", code="GEN")
    db.add(dept)
    db.commit()
    db.refresh(dept)
    
    # 3. Create Branches, Semesters, Sections, Subjects
    for branch_name in request.branches:
        branch = Branch(tenant_id=tenant_id, department_id=dept.id, name=branch_name, code=branch_name[:3].upper())
        db.add(branch)
        db.commit()
        db.refresh(branch)
        
        # We will create Semesters and Subjects dynamically
        total_semesters = request.years * request.semesters_per_year
        for sem_num in range(1, total_semesters + 1):
            sem = Semester(tenant_id=tenant_id, academic_year_id=acad_year.id, branch_id=branch.id, name=f"Semester {sem_num}", term_number=sem_num)
            db.add(sem)
            db.commit()
            db.refresh(sem)
            
            # Add some dummy subjects for each semester
            for sub_num in range(1, 6):
                subj = Subject(tenant_id=tenant_id, branch_id=branch.id, semester_id=sem.id, name=f"{branch_name} Subj {sub_num} (Sem {sem_num})", credits=3)
                db.add(subj)
    
    # 4. Create Periods
    from datetime import time
    for p in range(1, request.periods_per_day + 1):
        # 9 AM start, 50 mins each roughly
        start_hour = 9 + (p-1)
        if start_hour > 23: start_hour = 23 # Prevent overflow for huge periods
        period = Period(tenant_id=tenant_id, name=f"Period {p}", period_number=p, start_time=time(hour=start_hour, minute=0), end_time=time(hour=start_hour, minute=50))
        db.add(period)
        
    db.commit()
    
    return {"status": "success", "message": "Smart Build Complete!"}
