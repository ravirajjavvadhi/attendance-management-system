from sqlalchemy.orm import Session
from app.models.erp_academic import FacultySubjectAllocation, Subject
from app.models.academic import AcademicYear, Section

class SubjectAllocationEngine:
    """
    Engine to manage strict Faculty -> Subject allocations.
    """

    @staticmethod
    def allocate_faculty_to_subject(db: Session, tenant_id: int, faculty_user_id: int, subject_id: int, section_id: int, academic_year_id: int):
        """
        Creates a permanent mapping of a faculty to a specific subject and section.
        """
        allocation = FacultySubjectAllocation(
            tenant_id=tenant_id,
            faculty_user_id=faculty_user_id,
            subject_id=subject_id,
            section_id=section_id,
            academic_year_id=academic_year_id
        )
        db.add(allocation)
        db.commit()
        db.refresh(allocation)
        return allocation
