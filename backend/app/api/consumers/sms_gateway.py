from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_sms_gateway():
    return {"status": "ok", "message": "SMS Gateway Engine"}
