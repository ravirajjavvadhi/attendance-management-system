from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Any, Dict
from pydantic import BaseModel
import re

from app.db.database import get_db
from app.api.deps import get_current_admin
from app.models.user import User, UserRole
from app.models.academic import Section, Class, AcademicYear
from app.models.erp_academic import Subject, Period, Timetable, FacultySubjectAllocation, Branch, Semester
from app.models.profiles import FacultyProfile
from app.services.gemini_service import parse_timetable_image

router = APIRouter()

class TimetableConfirmRequest(BaseModel):
    section_id: int
    semester_name: str
    subjects: List[Dict[str, Any]]
    periods: List[Dict[str, Any]]
    schedule: Dict[str, Any]

@router.post("/parse")
async def parse_timetable(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin)
):
    try:
        content = await file.read()
        parsed_data = parse_timetable_image(content, file.content_type)
        return parsed_data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error during parsing")

@router.post("/confirm", status_code=status.HTTP_201_CREATED)
def confirm_timetable(
    request: TimetableConfirmRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    section = db.query(Section).filter(Section.id == request.section_id, Section.tenant_id == current_user.tenant_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
        
    active_year = db.query(AcademicYear).filter(
        AcademicYear.tenant_id == current_user.tenant_id,
        AcademicYear.is_active == True
    ).first()
    if not active_year:
        raise HTTPException(status_code=400, detail="No active academic year found")
        
    # 1. Clear old timetable for this section (for simplicity in this implementation)
    db.query(Timetable).filter(
        Timetable.section_id == section.id, 
        Timetable.tenant_id == current_user.tenant_id
    ).delete()
    
    # 2. Create/Get Periods
    period_map = {} # period_number -> period_id
    for p_data in request.periods:
        num = p_data.get("number")
        if not num:
            continue
        period = db.query(Period).filter(
            Period.tenant_id == current_user.tenant_id,
            Period.period_number == num
        ).first()
        
        if not period:
            time_str = p_data.get("time", "")
            # basic parse like "9:30-10:30"
            start = "09:00:00"
            end = "10:00:00"
            try:
                parts = time_str.split("-")
                if len(parts) == 2:
                    start_part = parts[0].strip()
                    end_part = parts[1].strip()
                    
                    # Convert H:MM to HH:MM:00
                    def format_time(t):
                        t = t.replace(".", ":")
                        if len(t.split(":")) == 2:
                            h, m = t.split(":")
                            # Simple AM/PM logic based on values (usually college starts at 9am)
                            hi = int(h)
                            if hi < 8: hi += 12 # e.g. 1, 2, 3 PM
                            return f"{hi:02d}:{m}:00"
                        return "09:00:00"
                        
                    start = format_time(start_part)
                    end = format_time(end_part)
            except Exception:
                pass
                
            period = Period(
                tenant_id=current_user.tenant_id,
                name=f"Period {num}",
                period_number=num,
                start_time=start,
                end_time=end,
                is_break=False
            )
            db.add(period)
            db.flush()
            
        period_map[num] = period.id
        
    # 3. Create/Get Subjects & Match Faculty
    subject_map = {} # code or short -> subject_id
    faculty_map = {} # subject_code -> faculty_user_id
    
    # Simple fuzzy match helper
    def find_faculty(name):
        if not name: return None
        search = f"%{name.split()[-1]}%" # Search by last name
        faculty = db.query(User).filter(
            User.tenant_id == current_user.tenant_id,
            User.role == UserRole.FACULTY.value,
            User.full_name.ilike(search)
        ).first()
        return faculty
        
    for s_data in request.subjects:
        code = s_data.get("code") or s_data.get("short")
        if not code: continue
        
        subj = db.query(Subject).filter(
            Subject.tenant_id == current_user.tenant_id,
            Subject.code == code
        ).first()
        
        if not subj:
            subj = Subject(
                tenant_id=current_user.tenant_id,
                name=s_data.get("name", code),
                code=code,
                credits=s_data.get("credits", 0)
            )
            db.add(subj)
            db.flush()
            
        subject_map[code] = subj.id
        subject_map[s_data.get("short", code)] = subj.id
        
        faculty_name = s_data.get("faculty")
        fac_user = find_faculty(faculty_name)
        if fac_user:
            faculty_map[code] = fac_user.id
            faculty_map[s_data.get("short", code)] = fac_user.id
            
            # Create allocation
            alloc = db.query(FacultySubjectAllocation).filter(
                FacultySubjectAllocation.tenant_id == current_user.tenant_id,
                FacultySubjectAllocation.section_id == section.id,
                FacultySubjectAllocation.subject_id == subj.id,
                FacultySubjectAllocation.academic_year_id == active_year.id
            ).first()
            
            if not alloc:
                alloc = FacultySubjectAllocation(
                    tenant_id=current_user.tenant_id,
                    faculty_user_id=fac_user.id,
                    subject_id=subj.id,
                    section_id=section.id,
                    academic_year_id=active_year.id
                )
                db.add(alloc)

    # 4. Create Timetable Entries
    for day, entries in request.schedule.items():
        if not isinstance(entries, list): continue
        for entry in entries:
            if entry.get("break"): continue
            
            p_num = entry.get("period")
            s_code = entry.get("subject_code")
            
            if p_num in period_map and s_code in subject_map:
                tt = Timetable(
                    tenant_id=current_user.tenant_id,
                    academic_year_id=active_year.id,
                    section_id=section.id,
                    period_id=period_map[p_num],
                    day_of_week=day.upper(),
                    subject_id=subject_map[s_code],
                    faculty_user_id=faculty_map.get(s_code, current_user.id) # Fallback to admin if no faculty matched for now
                )
                db.add(tt)
                
    db.commit()
    return {"message": "Timetable saved successfully"}

@router.get("/{section_id}")
def get_timetable(
    section_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    entries = db.query(Timetable).filter(
        Timetable.section_id == section_id,
        Timetable.tenant_id == current_user.tenant_id
    ).all()
    
    result = []
    for e in entries:
        subject = db.query(Subject).filter(Subject.id == e.subject_id).first()
        period = db.query(Period).filter(Period.id == e.period_id).first()
        faculty = db.query(User).filter(User.id == e.faculty_user_id).first()
        
        result.append({
            "id": e.id,
            "day_of_week": e.day_of_week,
            "period": {
                "id": period.id,
                "name": period.name,
                "number": period.period_number,
                "start": str(period.start_time),
                "end": str(period.end_time)
            },
            "subject": {
                "id": subject.id,
                "name": subject.name,
                "code": subject.code
            },
            "faculty": {
                "id": faculty.id,
                "name": faculty.full_name
            }
        })
    return result
