import asyncio
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.academic import Department, Class, Section

def fix_db():
    db = SessionLocal()
    try:
        # Fix Department Typo
        dept = db.query(Department).filter(Department.id == 4).first()
        if dept:
            dept.name = "COMPUTER SCIENCE AND ENGINEERING"
            
        # Fix Class Name
        cls = db.query(Class).filter(Class.id == 4).first()
        if cls:
            cls.name = "3rd Year - 5th Semester"
            
        # Fix Section Name
        sec = db.query(Section).filter(Section.id == 3).first()
        if sec:
            sec.name = "D"
            
        db.commit()
        print("Successfully updated database records!")
            
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_db()
