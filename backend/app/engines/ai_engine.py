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

    @staticmethod
    def get_student_insight(db: Session, student_id: int):
        from datetime import date
        import os
        from sqlalchemy import func
        try:
            from groq import Groq
        except ImportError:
            Groq = None
            
        from app.models.erp_academic import StudentAIInsight, SemesterResult
        from app.models.attendance import AttendanceRecord
        from app.models.profiles import StudentProfile
        
        today = date.today()
        # Check if insight already exists for today
        existing_insight = db.query(StudentAIInsight).filter(
            StudentAIInsight.student_id == student_id,
            func.date(StudentAIInsight.date) == today
        ).first()
        
        if existing_insight:
            return existing_insight.insight_text
            
        # Fetch stats
        student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
        if not student:
            return ""
            
        attendance_records = db.query(AttendanceRecord).filter(AttendanceRecord.student_id == student_id).all()
        total_classes = len(attendance_records)
        attended_classes = sum(1 for r in attendance_records if r.is_present)
        attendance_pct = round((attended_classes / total_classes * 100), 1) if total_classes > 0 else 100.0
        
        sem_result = db.query(SemesterResult).filter(SemesterResult.student_id == student_id).order_by(SemesterResult.id.desc()).first()
        cgpa = sem_result.sgpa / 100.0 if sem_result and sem_result.sgpa > 0 else 0.0
        
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key or not Groq:
            return "AI Insights currently unavailable."
            
        try:
            client = Groq(api_key=api_key)
            prompt = f"Student {student.name or 'N/A'} has an attendance of {attendance_pct}% and a CGPA of {cgpa}. Write a 3-sentence actionable insight for this student."
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
            )
            insight_text = chat_completion.choices[0].message.content.strip()
            
            new_insight = StudentAIInsight(
                student_id=student_id,
                insight_text=insight_text,
                model_used="llama3-8b-8192"
            )
            db.add(new_insight)
            db.commit()
            return insight_text
        except Exception as e:
            print(f"Groq API Error: {e}")
            return "AI Insights currently unavailable."
