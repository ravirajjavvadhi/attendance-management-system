from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date as date_cls, datetime
from app.models.profiles import StudentProfile, FacultyProfile, FacultyComment
from app.models.academic import Section, Event
from app.models.attendance import AttendanceRecord
from app.models.erp_academic import Timetable, Subject, Period, SemesterResult, SubjectMark
from app.models.user import User as UserModel
from app.models.communication import TimelineEvent
from app.models.notification import NotificationLog
from app.engines.reporting_engine import ReportingEngine

class DashboardEngine:
    @staticmethod
    def get_student_mega_payload(db: Session, student_id: int, tenant_id: int):
        student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
        if not student:
            return None
            
        student_name = student.name or "Student"
        student_roll = student.roll_number or "N/A"
        
        sec = db.query(Section).filter(Section.id == student.section_id).first()
        section_name = sec.name if sec else "N/A"
            
        # 1. Reporting Engine: Attendance Summary
        attendance_report = ReportingEngine.generate_attendance_report(
            db=db, tenant_id=tenant_id, filters={"student_id": student.id}
        )
        
        total_classes_overall = sum(item["total_classes"] for item in attendance_report)
        attended_overall = sum(item["total_present"] for item in attendance_report)
        attendance_pct = round((attended_overall / total_classes_overall * 100), 1) if total_classes_overall > 0 else 100.0

        # 2. Academic Engine: CGPA & Marks
        sem_result = db.query(SemesterResult).filter(SemesterResult.student_id == student.id).order_by(SemesterResult.id.desc()).first()
        cgpa = sem_result.sgpa / 100.0 if sem_result and sem_result.sgpa > 0 else 0.0
        credits = sem_result.credits_earned if sem_result else 0
        
        academic_performance = []
        if sem_result:
            marks = db.query(SubjectMark).filter(SubjectMark.result_id == sem_result.id).all()
            for m in marks:
                subj = db.query(Subject).filter(Subject.id == m.subject_id).first()
                if subj:
                    academic_performance.append({
                        "subject": subj.name,
                        "marks": m.marks_obtained,
                        "grade": m.grade
                    })
        
        if not academic_performance:
            academic_performance = []
            cgpa = cgpa if cgpa > 0 else 0.0
            credits = credits if credits > 0 else 0

        # Timeline Engine & Real Timetable for Today
        from zoneinfo import ZoneInfo
        ist = ZoneInfo('Asia/Kolkata')
        now_ist = datetime.now(ist)
        day_name = now_ist.strftime("%A").upper()
        today_date = now_ist.date()
        now_time = now_ist.time()

        tt_entries = db.query(Timetable).filter(Timetable.section_id == student.section_id, Timetable.day_of_week == day_name).all()
        def get_period_sort_key(e):
            period = db.query(Period).filter(Period.id == e.period_id).first()
            if period and period.start_time:
                return str(period.start_time)
            return "23:59:59"
            
        tt_entries = sorted(tt_entries, key=get_period_sort_key)
        
        # Fetch today's attendance
        attendance_today = db.query(AttendanceRecord).filter(
            AttendanceRecord.student_id == student.id,
            AttendanceRecord.date == today_date
        ).all()
        attendance_map = {att.period: att for att in attendance_today if att.period is not None}

        # 4. Faculty Comments
        comments_db = db.query(FacultyComment).filter(FacultyComment.student_id == student.id).order_by(FacultyComment.id.desc()).limit(5).all()
        
        faculty_comments = []
        for c in comments_db:
            fac_user = db.query(UserModel).filter(UserModel.id == c.faculty_user_id).first()
            fac_name = "Dr. Unknown"
            if fac_user:
                fac_prof = db.query(FacultyProfile).filter(FacultyProfile.user_id == fac_user.id).first()
                fac_name = fac_prof.name if fac_prof else fac_user.email
            faculty_comments.append({
                "faculty_name": fac_name,
                "comment": c.comment,
                "date": c.created_at
            })
        
        if not faculty_comments:
            faculty_comments = []

        current_class_info = {"status": "FREE", "subject": "No class", "faculty": "", "room": ""}
        
        today_timetable = []
        timeline = []

        for tt in tt_entries:
            subject = db.query(Subject).filter(Subject.id == tt.subject_id).first()
            period = db.query(Period).filter(Period.id == tt.period_id).first()
            faculty = db.query(UserModel).filter(UserModel.id == tt.faculty_user_id).first()
            faculty_name = "Unknown"
            if faculty:
                fac_prof = db.query(FacultyProfile).filter(FacultyProfile.user_id == faculty.id).first()
                faculty_name = fac_prof.name if (fac_prof and fac_prof.name) else (faculty.email or "Unknown")
            
            if subject and period:
                # Timetable status
                status = "UPCOMING"
                if period.start_time <= now_time <= period.end_time:
                    status = "LIVE NOW"
                    current_class_info = {
                        "status": "In Class",
                        "subject": subject.name,
                        "faculty": faculty_name,
                        "room": tt.room_number or "Room N/A"
                    }
                elif now_time > period.end_time:
                    status = "COMPLETED"
                    
                today_timetable.append({
                    "period": period.period_number,
                    "time": f"{period.start_time.strftime('%H:%M')} - {period.end_time.strftime('%H:%M')}",
                    "subject": subject.name,
                    "faculty": faculty_name,
                    "status": status
                })

                # Timeline auto-generation
                att_record = attendance_map.get(period.period_number)
                
                timeline_title = ""
                timeline_desc = ""
                timeline_type = "academic"
                
                if att_record:
                    timeline_title = f"{subject.name} (Period {period.period_number})"
                    if att_record.is_present:
                        timeline_desc = f"Marked Present by {faculty_name}"
                        timeline_type = "attendance_present"
                    else:
                        timeline_desc = f"Marked Absent by {faculty_name}"
                        timeline_type = "attendance_absent"
                else:
                    timeline_title = f"{subject.name} (Period {period.period_number})"
                    if status == "COMPLETED":
                        timeline_desc = "Auto-Marked Present"
                        timeline_type = "attendance_present"
                    elif status == "LIVE NOW":
                        timeline_desc = "Class is Live"
                        timeline_type = "academic"
                    else:
                        timeline_desc = "Upcoming"
                        timeline_type = "academic"

                timeline.append({
                    "time": period.start_time.strftime("%I:%M %p"),
                    "title": timeline_title,
                    "description": timeline_desc,
                    "type": timeline_type
                })

        # AI Insight Logic
        from app.engines.ai_engine import AIEngine
        insight_text = AIEngine.get_student_insight(db, student.id)
        
        ai_insights = {
            "trend": "Analysis",
            "message": insight_text,
            "score": "N/A"
        }

        # Fetch Real Notifications (For Parents)
        timeline_events = db.query(TimelineEvent).filter(
            TimelineEvent.user_id == student.user_id
        ).order_by(TimelineEvent.timestamp.desc()).limit(15).all()
        
        notifications_list = []
        for e in timeline_events:
            notifications_list.append({
                "id": e.id,
                "title": "Student Update",
                "message": f"[{e.event_type}] {e.description}",
                "date": e.timestamp.strftime("%Y-%m-%d %H:%M"),
                "type": "ACADEMIC",
                "isRead": False
            })

        return {
            "studentStatus": {
                "name": student_name,
                "roll_number": student_roll,
                "current_status": current_class_info["status"],
                "current_subject": current_class_info["subject"],
                "current_faculty": current_class_info["faculty"],
                "current_room": current_class_info["room"],
                "branch": "Computer Science",
                "semester": f"Section {section_name}"
            },
            "quickStats": {
                "attendance_percentage": attendance_pct,
                "cgpa": cgpa,
                "credits_earned": credits
            },
            "timeline": timeline,
            "academicPerformance": academic_performance,
            "subjectWiseAttendance": attendance_report,
            "aiInsights": ai_insights,
            "notifications": notifications_list,
            "facultyComments": faculty_comments,
            "todayTimetable": today_timetable if today_timetable else [
                {"period": 1, "subject": "No classes scheduled today", "status": "FREE"}
            ],
            "upcomingExams": [
                {"subject": "Physics", "date": "2026-08-10", "type": "Midterm"}
            ],
            "assignments": [
                {"subject": "Math", "title": "Calculus Assignment 1", "due_date": "2026-07-25"}
            ],
            "studentAnalytics": {
                "internal_average": 86.0,
                "subjects_count": 7,
                "assignments_pending": 2,
                "exam_countdown": 5
            }
        }
