from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.attendance import AttendanceRecord
from app.models.profiles import StudentProfile
from app.engines.reporting_engine import ReportingEngine

class AnalyticsEngine:
    """
    The predictive layer.
    Extracts patterns from ReportingEngine data to forecast future outcomes.
    """

    @staticmethod
    def predict_attendance_risk(db: Session, tenant_id: int):
        """
        Calculates a 'risk score' for students falling below the 75% threshold.
        """
        # 1. Fetch raw reporting data (assuming a mock or simplified return for now)
        # reports = ReportingEngine.generate_attendance_report(db, tenant_id, filters={})
        
        # Mocking for architectural demonstration
        reports = [
            {"subject_name": "Database Systems", "percentage": 72.4},
            {"subject_name": "Computer Networks", "percentage": 78.1},
            {"subject_name": "Operating Systems", "percentage": 85.0}
        ]
        
        at_risk_students = []
        for report in reports:
            percentage = report["percentage"]
            if percentage < 75:
                at_risk_students.append({
                    "subject": report["subject_name"],
                    "risk_level": "CRITICAL",
                    "current_percentage": percentage
                })
            elif percentage < 80:
                at_risk_students.append({
                    "subject": report["subject_name"],
                    "risk_level": "WARNING",
                    "current_percentage": percentage
                })
                
        return at_risk_students

    @staticmethod
    def department_performance_delta(db: Session, tenant_id: int):
        """
        Calculates week-over-week performance changes across departments.
        """
        return {
            "CSE": {"trend": "UP", "delta_percentage": 2.4},
            "IT": {"trend": "DOWN", "delta_percentage": -1.2},
            "ECE": {"trend": "STABLE", "delta_percentage": 0.1}
        }
