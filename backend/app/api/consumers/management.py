from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime

from app.db.database import get_db
from app.api.deps import get_current_management
from app.models.user import User
from app.models.academic import Event
from app.engines.dashboard_engine import DashboardEngine

router = APIRouter()

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
    
    leave.status = request.status
    db.commit()
    return {"status": "success", "message": f"Leave status updated to {request.status}"}

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
