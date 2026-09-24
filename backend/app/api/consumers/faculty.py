from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, date
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_faculty
from app.db.database import get_db
from app.models.profiles import FacultyProfile
from app.models.user import User

router = APIRouter()


class ParentUpdateRequest(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    message: str = Field(min_length=2, max_length=2000)

class FacultyLeaveCreate(BaseModel):
    start_date: date
    end_date: date
    reason: str = Field(min_length=2, max_length=1000)
    handover_note: str | None = Field(default=None, max_length=1000)

@router.post('/me/leave-requests', status_code=status.HTTP_201_CREATED)
def create_faculty_leave_request(request: FacultyLeaveCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_faculty)):
    from app.models.erp_academic import FacultyLeaveRequest
    if request.end_date < request.start_date:
        raise HTTPException(status_code=400, detail='End date must be on or after the start date')
    leave = FacultyLeaveRequest(tenant_id=current_user.tenant_id, faculty_user_id=current_user.id, start_date=request.start_date, end_date=request.end_date, reason=request.reason.strip(), handover_note=request.handover_note.strip() if request.handover_note else None)
    db.add(leave); db.commit(); db.refresh(leave)
    return {'status': 'success', 'data': {'id': leave.id, 'status': leave.status}}

@router.get('/me/leave-requests')
def get_my_faculty_leave_requests(db: Session = Depends(get_db), current_user: User = Depends(get_current_faculty)):
    from app.models.erp_academic import FacultyLeaveRequest
    rows = db.query(FacultyLeaveRequest).filter(FacultyLeaveRequest.tenant_id == current_user.tenant_id, FacultyLeaveRequest.faculty_user_id == current_user.id).order_by(FacultyLeaveRequest.created_at.desc()).all()
    return {'status': 'success', 'data': [{'id': row.id, 'start_date': row.start_date, 'end_date': row.end_date, 'reason': row.reason, 'handover_note': row.handover_note, 'status': row.status} for row in rows]}


@router.post("/learners/{student_id}/parent-update", status_code=status.HTTP_201_CREATED)
def send_parent_update(
    student_id: int,
    request: ParentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty),
):
    """Deliver a faculty-written learner update to the authorised parent inbox."""
    from app.api.academic import _require_academic_student_access
    from app.models.communication import TimelineEvent
    from app.models.notification import NotificationLog
    from app.models.profiles import ParentProfile, ParentStudentLink

    student = _require_academic_student_access(db, current_user, student_id)
    link = db.query(ParentStudentLink).filter(
        ParentStudentLink.student_id == student.id,
        ParentStudentLink.receive_notifications == True,
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="No parent notification link is available for this learner")
    parent = db.query(ParentProfile).filter(ParentProfile.id == link.parent_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent profile not found")
    parent_user = db.query(User).filter(User.id == parent.user_id).first()
    if not parent_user:
        raise HTTPException(status_code=404, detail="Parent account not found")

    notification = NotificationLog(
        tenant_id=current_user.tenant_id,
        student_id=student.id,
        channel="IN_APP",
        recipient=parent_user.email or parent_user.mobile_number,
        status="SENT",
        event_type="ACADEMIC",
        entity_type="faculty_parent_update",
        title=request.title.strip(),
        message=request.message.strip(),
    )
    db.add(notification)
    if student.user_id:
        db.add(TimelineEvent(
            tenant_id=current_user.tenant_id,
            user_id=student.user_id,
            event_type="FACULTY_PARENT_UPDATE",
            description=f"{request.title.strip()}: {request.message.strip()}",
        ))
    db.commit()
    db.refresh(notification)
    return {"status": "success", "data": {"id": notification.id, "delivery": "IN_APP"}}


@router.get("/me/dashboard")
def get_my_faculty_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty),
):
    """Return the faculty member's own timetable and authorised sections."""
    # Reuse the established schedule and section policy until these contracts are
    # extracted into a dedicated dashboard service.
    from app.api.academic import get_faculty_weekly_schedule, get_sections

    schedule = get_faculty_weekly_schedule(db=db, current_user=current_user)
    sections = get_sections(db=db, current_user=current_user)
    profile = db.query(FacultyProfile).filter(
        FacultyProfile.user_id == current_user.id
    ).first()

    return {
        "status": "success",
        "data": {
            "faculty": {
                "name": profile.name if profile and profile.name else current_user.email,
                "employee_id": profile.employee_id if profile else None,
                "access_level": profile.access_level if profile else None,
            },
            "schedule": schedule,
            "sections": [
                {"id": section.id, "name": section.name, "class_id": section.class_id}
                for section in sections
            ],
        },
    }

@router.get("/{tenant_id}/derive-session")
def derive_attendance_session(tenant_id: int, faculty_id: int):
    """
    Timetable Engine Logic:
    Instead of faculty manually picking Period/Subject, the system derives it:
    Current Time -> Academic Calendar -> Period -> Timetable -> Subject & Section.
    """
    now = datetime.now().time()
    # Logic to query Period where start_time <= now <= end_time
    # Then query Timetable for that period_id, day_of_week, and faculty_id
    
    return {
        "status": "success", 
        "derived_session": {
            "period_number": 3,
            "subject_name": "Data Structures",
            "section_name": "CSE-A",
            "timetable_id": 105
        }
    }

@router.get("/")
def get_faculty_dashboard():
    return {"status": "ok", "message": "Faculty API Gateway Active"}
