from sqlalchemy.orm import Session
from app.engines.reporting_engine import ReportingEngine
from app.engines.analytics_engine import AnalyticsEngine
from app.engines.institution_health_engine import InstitutionHealthEngine

class AIEngine:
    """
    The LLM Tool-Calling Context Router.
    Parses NLP queries, delegates to internal Engines, and formats the response.
    """

    @staticmethod
    def process_query(db: Session, tenant_id: int, query: str):
        """
        Receives natural language like: "Which departments are weak?"
        and routes it to the appropriate internal engines.
        """
        query_lower = query.lower()
        
        if "weak" in query_lower or "performance" in query_lower:
            # Route to Analytics Engine
            delta = AnalyticsEngine.department_performance_delta(db, tenant_id)
            
            # Format conversational response
            weak_depts = [dept for dept, data in delta.items() if data["trend"] == "DOWN"]
            if weak_depts:
                return f"Based on this week's analytics, {', '.join(weak_depts)} is showing a downward trend."
            return "All departments are stable or improving this week."
            
        elif "risk" in query_lower or "attendance" in query_lower:
            # Route to Analytics Engine for risk prediction
            risks = AnalyticsEngine.predict_attendance_risk(db, tenant_id)
            critical = [r for r in risks if r["risk_level"] == "CRITICAL"]
            
            if critical:
                return f"I found {len(critical)} subjects where students are at critical risk of falling below the 75% mandate, notably in {critical[0]['subject']}."
            return "Attendance levels are currently within safe margins."
            
        elif "health" in query_lower:
            # Route to Institution Health Engine
            score, alerts = InstitutionHealthEngine.calculate_health_score(db, tenant_id)
            return f"The institution health score is {score}%. I have {len(alerts)} active alerts."
            
        else:
            return "I am EduFlow AI. I can analyze attendance risk, department performance, and overall institution health. How can I assist you today?"
