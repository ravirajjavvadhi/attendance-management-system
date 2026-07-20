from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel

from app.db.database import get_db
from app.api.deps import get_current_admin, get_current_management_or_faculty
from app.models.user import User, UserRole
from app.models.academic import Section, Class, AcademicYear, Department
from app.models.erp_academic import Subject, Period, Timetable, FacultySubjectAllocation

router = APIRouter()


# ─── Pydantic Models ──────────────────────────────────────────────────────────

class PeriodEntry(BaseModel):
    period_number: int
    subject_name: str
    subject_code: Optional[str] = None
    start_time: str   # "09:00"
    end_time: str     # "10:00"
    faculty_user_id: Optional[int] = None
    is_break: bool = False

class DaySchedule(BaseModel):
    day: str  # MONDAY, TUESDAY ...
    periods: List[PeriodEntry]

class SaveTimetableRequest(BaseModel):
    section_id: int
    days: List[DaySchedule]


# ─── GET timetable for a section ──────────────────────────────────────────────

@router.get("/{section_id}")
def get_timetable(
    section_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_management_or_faculty)
):
    section = db.query(Section).filter(
        Section.id == section_id,
        Section.tenant_id == current_user.tenant_id
    ).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    entries = db.query(Timetable).filter(
        Timetable.section_id == section_id,
        Timetable.tenant_id == current_user.tenant_id
    ).order_by(Timetable.day_of_week, Timetable.period_id).all()

    result: Dict[str, List] = {}
    for e in entries:
        subject = db.query(Subject).filter(Subject.id == e.subject_id).first()
        period = db.query(Period).filter(Period.id == e.period_id).first()
        faculty = db.query(User).filter(User.id == e.faculty_user_id).first()

        if e.day_of_week not in result:
            result[e.day_of_week] = []

        result[e.day_of_week].append({
            "id": e.id,
            "period_number": period.period_number if period else 0,
            "start_time": str(period.start_time) if period else "",
            "end_time": str(period.end_time) if period else "",
            "subject_name": subject.name if subject else "",
            "subject_code": subject.code if subject else "",
            "is_break": period.is_break if period else False,
            "faculty_id": faculty.id if faculty else None,
            "faculty_name": getattr(faculty, 'full_name', None) or (faculty.email if faculty else ""),
        })

    return result


# ─── GET faculty list for a tenant ────────────────────────────────────────────

@router.get("/faculty/list")
def get_faculty_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    faculty_users = db.query(User).filter(
        User.tenant_id == current_user.tenant_id,
        User.role == UserRole.FACULTY.value,
        User.is_active == True
    ).all()

    from app.models.profiles import FacultyProfile
    result = []
    for u in faculty_users:
        profile = db.query(FacultyProfile).filter(FacultyProfile.user_id == u.id).first()
        result.append({
            "id": u.id,
            "name": getattr(profile, 'name', None) or u.email,
            "email": u.email
        })
    return result


# ─── SAVE / REPLACE timetable for a section ───────────────────────────────────

@router.post("/save", status_code=status.HTTP_201_CREATED)
def save_timetable(
    request: SaveTimetableRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    section = db.query(Section).filter(
        Section.id == request.section_id,
        Section.tenant_id == current_user.tenant_id
    ).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    # Get or create active academic year
    active_year = db.query(AcademicYear).filter(
        AcademicYear.tenant_id == current_user.tenant_id,
        AcademicYear.is_active == True
    ).first()
    if not active_year:
        # Create a default academic year if none exists
        from datetime import date
        year = date.today().year
        active_year = AcademicYear(
            tenant_id=current_user.tenant_id,
            name=f"{year}-{year+1}",
            start_date=date(year, 6, 1),
            end_date=date(year + 1, 5, 31),
            is_active=True
        )
        db.add(active_year)
        db.flush()

    # Clear old timetable for this section
    db.query(Timetable).filter(
        Timetable.section_id == section.id,
        Timetable.tenant_id == current_user.tenant_id
    ).delete()

    for day_schedule in request.days:
        day = day_schedule.day.upper()
        for p_entry in day_schedule.periods:
            # Format times properly
            def fmt(t: str) -> str:
                t = t.strip()
                if len(t) == 5:  # "09:00"
                    return f"{t}:00"
                return t if t else "00:00:00"

            start = fmt(p_entry.start_time)
            end = fmt(p_entry.end_time)

            # Get or create Period
            period = db.query(Period).filter(
                Period.tenant_id == current_user.tenant_id,
                Period.period_number == p_entry.period_number,
                Period.start_time == start,
                Period.end_time == end
            ).first()

            if not period:
                period = Period(
                    tenant_id=current_user.tenant_id,
                    name=f"Period {p_entry.period_number}" if not p_entry.is_break else "Break",
                    period_number=p_entry.period_number,
                    start_time=start,
                    end_time=end,
                    is_break=p_entry.is_break
                )
                db.add(period)
                db.flush()

            if p_entry.is_break:
                continue  # Don't create timetable entry for breaks

            # Get or create Subject
            code = (p_entry.subject_code or p_entry.subject_name[:6].upper().replace(" ", "")).strip()
            subject = db.query(Subject).filter(
                Subject.tenant_id == current_user.tenant_id,
                Subject.code == code
            ).first()

            if not subject:
                subject = Subject(
                    tenant_id=current_user.tenant_id,
                    name=p_entry.subject_name,
                    code=code,
                    credits=0
                )
                db.add(subject)
                db.flush()

            faculty_id = p_entry.faculty_user_id or current_user.id

            # Create timetable entry
            tt = Timetable(
                tenant_id=current_user.tenant_id,
                academic_year_id=active_year.id,
                section_id=section.id,
                period_id=period.id,
                day_of_week=day,
                subject_id=subject.id,
                faculty_user_id=faculty_id
            )
            db.add(tt)

            # Create/update faculty-subject allocation
            if p_entry.faculty_user_id:
                alloc = db.query(FacultySubjectAllocation).filter(
                    FacultySubjectAllocation.tenant_id == current_user.tenant_id,
                    FacultySubjectAllocation.section_id == section.id,
                    FacultySubjectAllocation.subject_id == subject.id,
                    FacultySubjectAllocation.faculty_user_id == faculty_id,
                    FacultySubjectAllocation.academic_year_id == active_year.id
                ).first()
                if not alloc:
                    alloc = FacultySubjectAllocation(
                        tenant_id=current_user.tenant_id,
                        faculty_user_id=faculty_id,
                        subject_id=subject.id,
                        section_id=section.id,
                        academic_year_id=active_year.id
                    )
                    db.add(alloc)

    db.commit()
    return {"message": "Timetable saved successfully"}


# ─── DELETE timetable for a section ───────────────────────────────────────────

@router.delete("/{section_id}", status_code=status.HTTP_200_OK)
def delete_timetable(
    section_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    db.query(Timetable).filter(
        Timetable.section_id == section_id,
        Timetable.tenant_id == current_user.tenant_id
    ).delete()
    db.commit()
    return {"message": "Timetable cleared successfully"}
