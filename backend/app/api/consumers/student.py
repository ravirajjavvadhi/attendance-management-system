from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_student_dashboard():
    return {"status": "ok", "message": "Student API Gateway"}
