import asyncio
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.academic import Department, Class, Section

def inspect_db():
    db = SessionLocal()
    try:
        depts = db.query(Department).all()
        print("--- Departments ---")
        for d in depts:
            print(f"ID: {d.id}, Name: {d.name}, Code: {d.code}")
            
        classes = db.query(Class).all()
        print("\n--- Classes ---")
        for c in classes:
            print(f"ID: {c.id}, Name: {c.name}, DeptID: {c.department_id}")
            
        sections = db.query(Section).all()
        print("\n--- Sections ---")
        for s in sections:
            print(f"ID: {s.id}, Name: {s.name}, ClassID: {s.class_id}")
            
    finally:
        db.close()

if __name__ == "__main__":
    inspect_db()
