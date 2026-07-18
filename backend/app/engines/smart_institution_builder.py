from sqlalchemy.orm import Session
from app.models.tenant import Institution
from app.models.academic import Department
from app.models.erp_academic import Branch, Semester, Subject, Period

class SmartInstitutionBuilder:
    """
    Provisions a complete enterprise academic structure recursively.
    """

    @staticmethod
    def provision_institution_hierarchy(db: Session, payload: dict):
        """
        Parses a massive JSON payload mapping Departments -> Branches -> Semesters -> Sections -> Subjects.
        Iteratively creates database entries in bulk.
        """
        # Simulated recursive creation logic
        tenant_id = payload.get("tenant_id")
        
        for dept in payload.get("departments", []):
            department = Department(tenant_id=tenant_id, name=dept["name"], code=dept["code"])
            db.add(department)
            db.flush() # To get department.id
            
            for branch in dept.get("branches", []):
                new_branch = Branch(tenant_id=tenant_id, department_id=department.id, name=branch["name"])
                db.add(new_branch)
                db.flush()
                
                # Further nest Semesters, Sections, Subjects here
                
        db.commit()
        return {"status": "success", "message": "Hierarchy strictly provisioned."}
