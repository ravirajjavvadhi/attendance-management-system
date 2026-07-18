from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.profiles import StudentProfile, FacultyProfile, ParentProfile

class IdentityEngine:
    """
    Centralized identity service for EduFlow AI.
    Handles Role-Based Access Control and profile resolution.
    """
    
    @staticmethod
    def resolve_profile(db: Session, user_id: int, role: str):
        """
        Given a generic User ID and Role, fetches the exact profile entity.
        """
        if role == UserRole.STUDENT.value:
            return db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
        elif role == UserRole.FACULTY.value:
            return db.query(FacultyProfile).filter(FacultyProfile.user_id == user_id).first()
        elif role == UserRole.PARENT.value:
            return db.query(ParentProfile).filter(ParentProfile.user_id == user_id).first()
        return None

    @staticmethod
    def has_permission(user_role: str, required_role: str) -> bool:
        """
        Checks if the user has the required hierarchical permission.
        """
        hierarchy = {
            "SUPERADMIN": 1,
            "MANAGEMENT": 2,
            "PRINCIPAL": 3,
            "HOD": 4,
            "FACULTY": 5,
            "STUDENT": 6,
            "PARENT": 6
        }
        return hierarchy.get(user_role, 99) <= hierarchy.get(required_role, 99)
