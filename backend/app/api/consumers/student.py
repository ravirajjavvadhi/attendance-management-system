from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.database import get_db
from app.engines.dashboard_engine import DashboardEngine
from app.models.academic import Section
from app.models.profiles import StudentProfile
from app.models.user import User, UserRole

router = APIRouter()

@router.get("/")
def get_student_dashboard():
    return {"status": "ok", "message": "Student API Gateway"}


@router.get("/me/dashboard")
def get_my_student_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return the signed-in student's own live dashboard payload."""
    if current_user.role != UserRole.STUDENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This dashboard is available to student accounts only",
        )

    student = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id
    ).first()
    if not student or not student.section_id:
        raise HTTPException(status_code=404, detail="Student profile or section not found")

    section = db.query(Section).filter(
        Section.id == student.section_id,
        Section.tenant_id == current_user.tenant_id,
    ).first()
    if not section:
        raise HTTPException(status_code=403, detail="Student profile is outside this institution")

    payload = DashboardEngine.get_student_mega_payload(
        db=db,
        student_id=student.id,
        tenant_id=current_user.tenant_id,
    )
    if not payload:
        raise HTTPException(status_code=404, detail="Student dashboard data not found")

    return {"status": "success", "data": payload}
