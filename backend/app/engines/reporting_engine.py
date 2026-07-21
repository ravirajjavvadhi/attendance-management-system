from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Integer
from app.models.attendance import AttendanceRecord
from app.models.profiles import StudentProfile
from app.models.erp_academic import Subject

class ReportingEngine:
    """
    Answers "What happened."
    Massive, dynamic SQL/SQLAlchemy generator for reporting.
    """

    @staticmethod
    def generate_attendance_report(db: Session, tenant_id: int, filters: dict):
        """
        Generates standard aggregated reports based on dynamic filters.
        Used by the Management Dashboard to view sliced data.
        """
        query = db.query(
            AttendanceRecord.subject_id,
            Subject.name,
            func.count(AttendanceRecord.id).label("total_classes"),
            func.sum(cast(AttendanceRecord.is_present, Integer)).label("total_present")
        ).join(Subject, Subject.id == AttendanceRecord.subject_id)\
         .filter(AttendanceRecord.tenant_id == tenant_id)

        # Dynamically apply filters
        if "student_id" in filters:
            query = query.filter(AttendanceRecord.student_id == filters["student_id"])
        if "section_id" in filters:
            query = query.filter(AttendanceRecord.section_id == filters["section_id"])
        if "start_date" in filters and "end_date" in filters:
            query = query.filter(AttendanceRecord.date >= filters["start_date"], AttendanceRecord.date <= filters["end_date"])

        # Group by Subject to get aggregated stats
        query = query.group_by(AttendanceRecord.subject_id, Subject.name)
        
        results = query.all()
        
        report = []
        for row in results:
            percentage = (row.total_present / row.total_classes * 100) if row.total_classes > 0 else 0
            report.append({
                "subject_id": row.subject_id,
                "subject_name": row.name,
                "total_classes": row.total_classes,
                "total_present": row.total_present,
                "percentage": round(percentage, 2)
            })
            
        return report
