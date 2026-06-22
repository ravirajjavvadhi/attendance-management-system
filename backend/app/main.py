from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router

app = FastAPI(title="EduFlow AI API", description="Smart Academic Operations & Attendance Automation Platform")

# Enable CORS for production (Vercel) and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For strict production, change this to your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to EduFlow AI API"}
