from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime, date

from app.db.database import get_db
from app.api.deps import get_current_management
from app.models.user import User
from app.models.academic import Event
from app.engines.dashboard_engine import DashboardEngine
from app.engines.enterprise_analytics_engine import enterprise_analytics_engine
from typing import Optional

router = APIRouter()

class SmartPromoteRequest(BaseModel):
    new_academic_year: str
    new_semester_name: str
    duplicate_timetable: bool = False
    section_id: Optional[int] = None

class EventCreate(BaseModel):
    title: str
    description: str = None
    event_date: datetime

class EventOut(BaseModel):
    id: int
    title: str
    description: str
    event_date: datetime
    created_at: datetime
    
    class Config:
        orm_mode = True

@router.get("/")
def get_management_dashboard():
    return {"status": "ok", "message": "Management API Gateway"}


@router.get("/me/dashboard")
def get_my_management_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_management),
):
    """Mobile-first management snapshot scoped to the caller's institution."""
    from app.models.attendance import AttendanceRecord, AttendanceSummary
    from app.models.erp_academic import LeaveRequest, Timetable
    from app.models.profiles import StudentProfile
    from app.models.sms import SmsQueue
    from app.models.academic import Section
    from app.models.tenant import Institution

    tenant_id = current_user.tenant_id
    institution = db.query(Institution).filter(Institution.id == tenant_id).first()
    today = date.today()
    total_students = db.query(StudentProfile).join(Section).filter(
        Section.tenant_id == tenant_id
    ).count()
    today_records = db.query(AttendanceRecord).filter(
        AttendanceRecord.tenant_id == tenant_id,
        AttendanceRecord.date == today,
    ).all()
    marked_students = {record.student_id for record in today_records}
    present_students = {
        record.student_id for record in today_records if record.is_present
    }
    pending_leaves = db.query(LeaveRequest).filter(
        LeaveRequest.tenant_id == tenant_id,
        LeaveRequest.status == "PENDING",
    ).count()
    sms_attention = db.query(SmsQueue).filter(
        SmsQueue.tenant_id == tenant_id,
        SmsQueue.status.in_(["PENDING", "FAILED"]),
    ).count()
    shortage_students = db.query(AttendanceSummary).filter(
        AttendanceSummary.tenant_id == tenant_id,
        AttendanceSummary.subject_id == None,
        AttendanceSummary.is_shortage == True,
    ).count()
    timetable_slots = db.query(Timetable).filter(
        Timetable.tenant_id == tenant_id
    ).count()
    upcoming_events = db.query(Event).filter(
        Event.tenant_id == tenant_id,
        Event.event_date >= datetime.combine(today, datetime.min.time()),
    ).order_by(Event.event_date.asc()).limit(5).all()

    attention = []
    if pending_leaves:
        attention.append({"type": "LEAVES", "title": "Leave requests need a decision", "count": pending_leaves})
    if sms_attention:
        attention.append({"type": "SMS", "title": "SMS messages need review", "count": sms_attention})
    if shortage_students:
        attention.append({"type": "ATTENDANCE", "title": "Students need attendance support", "count": shortage_students})

    return {
        "status": "success",
        "data": {
            "generated_at": datetime.utcnow().isoformat(),
            "today": today.isoformat(),
            "institution": {
                "id": institution.id if institution else tenant_id,
                "name": institution.name if institution else "Your institution",
                "logo_url": institution.logo_url if institution else None,
            },
            "overview": {
                "total_students": total_students,
                "marked_students": len(marked_students),
                "present_students": len(present_students),
                "attendance_rate": round((len(present_students) / len(marked_students)) * 100, 1) if marked_students else 0.0,
                "timetable_slots": timetable_slots,
            },
            "attention": attention,
            "upcoming_events": [
                {
                    "id": event.id,
                    "title": event.title,
                    "date": event.event_date.isoformat(),
                    "priority": event.priority or "MEDIUM",
                }
                for event in upcoming_events
            ],
        },
    }

@router.post("/events", response_model=EventOut)
def create_event(
    event_in: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_management)
):
    new_event = Event(
        tenant_id=current_user.tenant_id,
        title=event_in.title,
        description=event_in.description,
        event_date=event_in.event_date
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

@router.get("/events", response_model=List[EventOut])
def get_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_management)
):
    events = db.query(Event).filter(
        Event.tenant_id == current_user.tenant_id
    ).order_by(Event.event_date.desc()).all()
    return events

@router.get("/student/{student_id}/dashboard")
def get_management_student_dashboard(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_management)
):
    """
    Allows Management/Admin to view the detailed individual student mega-dashboard,
    exactly as the Parent sees it (Attendance %, Timeline, CGPA, Faculty Comments).
    """
    payload = DashboardEngine.get_student_mega_payload(
        db=db, 
        student_id=student_id, 
        tenant_id=current_user.tenant_id
    )
    
    if not payload:
        raise HTTPException(status_code=404, detail="Student not found")
        
    return {
        "status": "success",
        "data": payload
    }

class DocumentUploadRequest(BaseModel):
    title: str
    category: str
    file_url: str

class LeaveStatusUpdate(BaseModel):
    status: str

@router.get('/faculty-leaves')
def get_faculty_leaves(db: Session = Depends(get_db), current_user: User = Depends(get_current_management)):
    from app.models.erp_academic import FacultyLeaveRequest
    rows = db.query(FacultyLeaveRequest, User).join(User, User.id == FacultyLeaveRequest.faculty_user_id).filter(FacultyLeaveRequest.tenant_id == current_user.tenant_id).order_by(FacultyLeaveRequest.created_at.desc()).all()
    return {'status': 'success', 'data': [{'id': leave.id, 'faculty_name': user.email, 'start_date': leave.start_date, 'end_date': leave.end_date, 'reason': leave.reason, 'handover_note': leave.handover_note, 'status': leave.status} for leave, user in rows]}

@router.put('/faculty-leaves/{leave_id}/status')
def update_faculty_leave_status(leave_id: int, request: LeaveStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_management)):
    from app.models.erp_academic import FacultyLeaveRequest
    leave = db.query(FacultyLeaveRequest).filter(FacultyLeaveRequest.id == leave_id, FacultyLeaveRequest.tenant_id == current_user.tenant_id).first()
    if not leave: raise HTTPException(status_code=404, detail='Faculty leave request not found')
    next_status = request.status.upper()
    if next_status not in {'APPROVED', 'REJECTED'}: raise HTTPException(status_code=400, detail='Status must be APPROVED or REJECTED')
    if leave.status != 'PENDING': raise HTTPException(status_code=409, detail='Only pending requests can be decided')
    leave.status = next_status; db.commit()
    return {'status': 'success', 'data': {'id': leave.id, 'status': leave.status}}

@router.get("/leaves")
def get_all_leaves(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_management)
):
    from app.models.erp_academic import LeaveRequest
    from app.models.profiles import StudentProfile
    
    results = db.query(LeaveRequest, StudentProfile).join(
        StudentProfile, LeaveRequest.student_id == StudentProfile.id
    ).filter(
        LeaveRequest.tenant_id == current_user.tenant_id
    ).all()
    
    data = []
    for leave, student in results:
        data.append({
            "id": leave.id,
            "student_id": student.id,
            "student_name": student.name,
            "start_date": leave.start_date,
            "end_date": leave.end_date,
            "reason": leave.reason,
            "status": leave.status,
            "created_at": leave.created_at
        })
    return {"status": "success", "data": data}

@router.put("/leaves/{id}/status")
def update_leave_status(
    id: int,
    request: LeaveStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_management)
):
    from app.models.erp_academic import LeaveRequest
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == id, LeaveRequest.tenant_id == current_user.tenant_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    next_status = request.status.upper()
    if next_status not in {"APPROVED", "REJECTED"}:
        raise HTTPException(status_code=400, detail="Leave status must be APPROVED or REJECTED")
    if leave.status != "PENDING":
        raise HTTPException(status_code=409, detail="Only pending leave requests can be decided")

    leave.status = next_status
    db.commit()
    return {"status": "success", "message": f"Leave status updated to {next_status}"}

@router.post("/student/{student_id}/documents")
def upload_student_document(
    student_id: int,
    request: DocumentUploadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_management)
):
    from app.models.erp_academic import StudentDocument
    doc = StudentDocument(
        tenant_id=current_user.tenant_id,
        student_id=student_id,
        title=request.title,
        category=request.category,
        file_url=request.file_url
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {"status": "success", "data": {"id": doc.id}}

@router.get("/reports/master-attendance-sheet")
def get_master_attendance_sheet_endpoint(
    section_id: Optional[int] = None,
    session_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_management)
):
    """
    Returns university-grade tabular attendance ledger with multi-column per-subject counts, percentages, 
    75% warning badge, ML/OD counts, and Shortage %.
    """
    return enterprise_analytics_engine.get_master_attendance_sheet(db, current_user.tenant_id, section_id, session_id)

@router.post("/academic/smart-promote-semester")
def execute_smart_promote_semester(
    request: SmartPromoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_management)
):
    """
    1-Click Smart Term Transition automation. Archives current academic term, creates new session, 
    ports timetable if requested, resets active daily attendance, and triggers parental event stream notifications.
    """
    return enterprise_analytics_engine.execute_smart_term_promotion(
        db, 
        current_user.tenant_id, 
        request.new_academic_year, 
        request.new_semester_name, 
        request.duplicate_timetable,
        request.section_id
    )

@router.get("/analytics/enterprise")
def get_enterprise_analytics_endpoint(
    session_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_management)
):
    """
    Dynamic AI Analytics & Executive Insights engine generating live natural language trends, 
    student detention risk curves, subject difficulty indices, and faculty completion rates.
    """
    return enterprise_analytics_engine.get_enterprise_analytics(db, current_user.tenant_id, session_id)
