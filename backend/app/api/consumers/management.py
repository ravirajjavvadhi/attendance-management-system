from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_management_dashboard():
    return {"status": "ok", "message": "Management API Gateway"}
