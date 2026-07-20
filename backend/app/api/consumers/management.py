from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime

from app.db.database import get_db
from app.api.deps import get_current_management
from app.models.user import User
from app.models.academic import Event

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
