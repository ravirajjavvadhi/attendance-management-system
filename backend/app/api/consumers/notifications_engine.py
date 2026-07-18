from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class NotificationEvent(BaseModel):
    tenant_id: int
    event_type: str # "ATTENDANCE_ABSENT", "FEES_DUE", "EXAM_RESULTS"
    recipients: List[int] # List of user IDs
    message_body: str
    priority: str = "NORMAL"

def process_notification_pipeline(event: NotificationEvent):
    """
    Generic Notification Pipeline:
    Event -> Priority Routing -> Push (Parent App) -> Fallback (SMS Gateway) -> Email
    """
    print(f"[{event.tenant_id}] Processing {event.event_type} for {len(event.recipients)} users.")
    # 1. Check if Institution has Parent App enabled
    # 2. Attempt FCM Push Notification
    # 3. If no FCM token or Push fails -> Route to SMS Queue (Android Gateway)
    # 4. Log in NotificationHistory
    print("Routed to SMS Gateway Fallback")

@router.post("/dispatch")
def dispatch_notification(event: NotificationEvent, background_tasks: BackgroundTasks):
    """
    Central engine for all communications in the ERP.
    """
    background_tasks.add_task(process_notification_pipeline, event)
    return {"status": "queued", "message": "Notification dispatched to generic engine pipeline"}

@router.get("/")
def get_notification_engine():
    return {"status": "ok", "message": "Notification Engine Active"}
