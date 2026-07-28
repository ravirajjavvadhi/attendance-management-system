from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date as date_cls, datetime
from app.models.profiles import StudentProfile, FacultyProfile, FacultyComment
from app.models.academic import Section, Event, AcademicSession
from app.models.attendance import AttendanceRecord, AttendanceSummary, SubjectSummary, AttendanceStatusEnum
from app.models.erp_academic import Timetable, Subject, Period, SemesterResult, SubjectMark
from app.models.user import User as UserModel
from app.models.communication import TimelineEvent
from app.models.notification import NotificationLog
from app.engines.reporting_engine import ReportingEngine
from app.services.subject_code_service import SubjectCodeService

class DashboardEngine:
    @staticmethod
    def get_student_mega_payload(db: Session, student_id: int, tenant_id: int, session_id: int = None):
        student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
        if not student:
            return None
            
        student_name = student.name or "Student"
        student_roll = student.roll_number or "N/A"
        
        sec = db.query(Section).filter(Section.id == student.section_id).first()
        section_name = sec.name if sec else "N/A"

        # 0. Academic Session handling (Term Switcher)
        sessions_db = db.query(AcademicSession).filter(AcademicSession.tenant_id == tenant_id).order_by(AcademicSession.id.desc()).all()
        available_sessions = []
        active_session_id = session_id
        for s in sessions_db:
            available_sessions.append({
                "id": s.id,
                "academic_year": s.academic_year,
                "semester": s.semester,
                "term": s.term,
                "is_current": s.is_current,
                "status": s.status
            })
            if not active_session_id and s.is_current:
                active_session_id = s.id

        if not active_session_id and available_sessions:
            active_session_id = available_sessions[0]["id"]
            
        # 1. Reporting Engine: Attendance Summary & Materialized Summaries
        attendance_report = ReportingEngine.generate_attendance_report(
            db=db, tenant_id=tenant_id, filters={"student_id": student.id}
        )
        
        # Enrich with collision-safe subject codes and session scoping
        for item in attendance_report:
            if "subject_id" in item and item["subject_id"]:
                sub_obj = db.query(Subject).filter(Subject.id == item["subject_id"]).first()
                if sub_obj:
                    item["subject_code"] = SubjectCodeService.get_display_code(sub_obj)
                else:
                    item["subject_code"] = item.get("subject_code", "SUB")
            else:
                item["subject_code"] = item.get("subject_code", "SUB")
        
        total_classes_overall = sum(item["total_classes"] for item in attendance_report)
        attended_overall = sum(item["total_present"] for item in attendance_report)
        attendance_pct = round((attended_overall / total_classes_overall * 100), 1) if total_classes_overall > 0 else 100.0

        # Check overall summary from Materialized table if available
        if active_session_id:
            ov_mat = db.query(AttendanceSummary).filter(
                AttendanceSummary.tenant_id == tenant_id,
                AttendanceSummary.student_id == student.id,
                AttendanceSummary.subject_id == None,
                AttendanceSummary.academic_session_id == active_session_id
            ).first()
            if ov_mat:
                total_classes_overall = ov_mat.total_classes
                attended_overall = ov_mat.attended_classes
                attendance_pct = ov_mat.percentage

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
                        "subject_code": SubjectCodeService.get_display_code(subj),
                        "marks": m.marks_obtained,
                        "grade": m.grade
                    })

        # 3. Timeline Engine & Real Timetable for Today
        from zoneinfo import ZoneInfo
        ist = ZoneInfo('Asia/Kolkata')
        now_ist = datetime.now(ist)
        day_name = now_ist.strftime("%A").upper()
        today_date = now_ist.date()
        now_time = now_ist.time()

        tt_query = db.query(Timetable).filter(Timetable.section_id == student.section_id, Timetable.day_of_week == day_name)
        if active_session_id:
            tt_query = tt_query.filter((Timetable.academic_session_id == active_session_id) | (Timetable.academic_session_id == None))
        tt_entries = tt_query.all()

        def get_period_sort_key(e):
            period = db.query(Period).filter(Period.id == e.period_id).first()
            if period and period.start_time:
                return str(period.start_time)
            return "23:59:59"
            
        tt_entries = sorted(tt_entries, key=get_period_sort_key)
        
        # Fetch today's attendance records
        attendance_today = db.query(AttendanceRecord).filter(
            AttendanceRecord.student_id == student.id,
            AttendanceRecord.date == today_date
        ).all()
        attendance_map = {att.period: att for att in attendance_today if att.period is not None}

        today_timetable = []
        timeline = []
        current_class_info = {"status": "FREE", "subject": "No live class currently", "subject_code": "--", "faculty": "--", "room": "--"}
        all_completed_or_free = True
        total_periods_today = len(tt_entries)

        for tt in tt_entries:
            subject = db.query(Subject).filter(Subject.id == tt.subject_id).first()
            period = db.query(Period).filter(Period.id == tt.period_id).first()
            faculty = db.query(UserModel).filter(UserModel.id == tt.faculty_user_id).first()
            faculty_name = "Unknown Faculty"
            if faculty:
                fac_prof = db.query(FacultyProfile).filter(FacultyProfile.user_id == faculty.id).first()
                faculty_name = fac_prof.name if (fac_prof and fac_prof.name) else (faculty.email or "Faculty")
            
            if subject and period:
                sub_code = SubjectCodeService.get_display_code(subject)
                status = "UPCOMING"
                if period.start_time <= now_time <= period.end_time:
                    status = "LIVE NOW"
                    all_completed_or_free = False
                    current_class_info = {
                        "status": "LIVE NOW",
                        "subject": subject.name,
                        "subject_code": sub_code,
                        "faculty": faculty_name,
                        "room": tt.room_number or "Room N/A",
                        "period_number": period.period_number
                    }
                elif now_time > period.end_time:
                    status = "COMPLETED"
                else:
                    all_completed_or_free = False
                    
                today_timetable.append({
                    "period": period.period_number,
                    "time": f"{period.start_time.strftime('%H:%M')} - {period.end_time.strftime('%H:%M')}",
                    "subject": subject.name,
                    "subject_code": sub_code,
                    "faculty": faculty_name,
                    "room": tt.room_number or "N/A",
                    "status": status
                })

                att_record = attendance_map.get(period.period_number)
                timeline_title = f"{subject.name} ({sub_code}) - Period {period.period_number}"
                if att_record:
                    if att_record.is_present or att_record.status == AttendanceStatusEnum.PRESENT.value or att_record.status == AttendanceStatusEnum.ON_DUTY.value:
                        timeline_desc = f"Marked PRESENT ({att_record.status or 'PRESENT'}) by {faculty_name}"
                        timeline_type = "attendance_present"
                    else:
                        timeline_desc = f"Marked ABSENT ({att_record.status or 'ABSENT'}) by {faculty_name}"
                        timeline_type = "attendance_absent"
                else:
                    if status == "COMPLETED":
                        timeline_desc = "Session concluded; Attendance pending verification"
                        timeline_type = "academic"
                    elif status == "LIVE NOW":
                        timeline_desc = "Class session is currently in progress"
                        timeline_type = "academic"
                    else:
                        timeline_desc = "Scheduled upcoming session"
                        timeline_type = "academic"

                timeline.append({
                    "time": period.start_time.strftime("%I:%M %p"),
                    "title": timeline_title,
                    "description": timeline_desc,
                    "type": timeline_type
                })

        # 4. Today's Summary & Events Banner (For Parent & Student UI)
        attended_today_count = sum(1 for att in attendance_today if att.is_present or att.status in [AttendanceStatusEnum.PRESENT.value, AttendanceStatusEnum.ON_DUTY.value])
        today_percentage = round((attended_today_count / total_periods_today) * 100.0, 1) if total_periods_today > 0 else 100.0
        
        # Priority Events Banner
        events_query = db.query(Event).filter(Event.tenant_id == tenant_id)
        if active_session_id:
            events_query = events_query.filter((Event.academic_session_id == active_session_id) | (Event.academic_session_id == None))
        all_events = events_query.order_by(Event.event_date.desc()).limit(10).all()
        
        events_banner = []
        priority_map = {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 4}
        sorted_events = sorted(all_events, key=lambda x: priority_map.get(str(x.priority).upper(), 3))
        for ev in sorted_events:
            events_banner.append({
                "id": ev.id,
                "title": ev.title,
                "description": ev.description or "",
                "date": ev.event_date.strftime("%B %d, %Y"),
                "category": ev.category or "GENERAL",
                "priority": str(ev.priority or "HIGH").upper()
            })

        next_event_title = events_banner[0]["title"] if events_banner else "No further institutional events today"
        
        today_summary = {
            "is_completed": all_completed_or_free or total_periods_today == 0,
            "heading": f"Today's Summary ({today_percentage}%)",
            "attendance_fraction": f"{attended_today_count}/{total_periods_today} Periods Attended",
            "percentage_val": today_percentage,
            "status_label": "All Scheduled Classes Completed" if all_completed_or_free else "Classes Ongoing",
            "next_event": next_event_title
        }

        # 5. Faculty Comments
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

        # 6. AI Insight Logic
        from app.engines.ai_engine import AIEngine
        insight_text = AIEngine.get_student_insight(db, student.id)
        ai_insights = {
            "trend": "Good Progress" if attendance_pct >= 75 else "Action Required",
            "message": insight_text,
            "score": f"{attendance_pct}%"
        }
        
        # Day-by-Day Attendance Log
        daily_records = db.query(AttendanceRecord).filter(
            AttendanceRecord.student_id == student.id,
            (AttendanceRecord.period == 1) | (AttendanceRecord.period == None)
        ).order_by(AttendanceRecord.date.desc()).limit(14).all()
        
        daily_attendance_log = []
        for r in daily_records:
            daily_attendance_log.append({
                "date": r.date.strftime("%Y-%m-%d"),
                "status": "Present" if (r.is_present or r.status == AttendanceStatusEnum.PRESENT.value) else "Absent"
            })

        # 7. Immutable Notification Events (Filtered for Parent/Student)
        notif_query = db.query(NotificationLog).filter(
            NotificationLog.tenant_id == tenant_id,
            ((NotificationLog.student_id == student.id) | (NotificationLog.recipient.in_([student.roll_number, "ALL", "parent@eduflow.com"]))),
            NotificationLog.deleted_by_parent == False
        ).order_by(NotificationLog.created_at.desc()).limit(20).all()

        notifications_list = []
        for n in notif_query:
            notifications_list.append({
                "id": n.id,
                "title": n.title or ("Attendance Alert" if "absent" in n.message.lower() else "Institutional Event"),
                "message": n.message,
                "date": n.created_at.strftime("%B %d, %I:%M %p") if n.created_at else "Recently",
                "type": n.event_type or ("ATTENDANCE" if "absent" in n.message.lower() else "GENERAL"),
                "isRead": n.is_read or False,
                "priority": "HIGH" if "absent" in n.message.lower() else "MEDIUM"
            })

        return {
            "session_info": {
                "active_session_id": active_session_id,
                "available_sessions": available_sessions
            },
            "studentStatus": {
                "name": student_name,
                "roll_number": student_roll,
                "current_status": current_class_info.get("status", "FREE"),
                "current_subject": current_class_info.get("subject", "No active class"),
                "current_subject_code": current_class_info.get("subject_code", "--"),
                "current_faculty": current_class_info.get("faculty", "--"),
                "current_room": current_class_info.get("room", "--"),
                "branch": "Computer Science & Engineering",
                "semester": f"Section {section_name}",
                "today_summary": today_summary
            },
            "todaySummary": today_summary,
            "eventsBanner": events_banner,
            "quickStats": {
                "attendance_percentage": attendance_pct,
                "cgpa": cgpa,
                "credits_earned": credits,
                "total_classes": total_classes_overall,
                "attended_classes": attended_overall
            },
            "timeline": timeline,
            "academicPerformance": academic_performance,
            "subjectWiseAttendance": attendance_report,
            "dailyAttendanceLog": daily_attendance_log,
            "aiInsights": ai_insights,
            "notifications": notifications_list,
            "facultyComments": faculty_comments,
            "todayTimetable": today_timetable if today_timetable else [
                {"period": 1, "time": "All Day", "subject": "No academic periods scheduled today", "subject_code": "OFF", "status": "FREE"}
            ],
            "upcomingExams": [
                {"subject": "Computer Networks", "subject_code": "CN201", "date": "2026-08-10", "type": "Mid-Term Assessment"}
            ],
            "assignments": [
                {"subject": "Design & Analysis of Algorithms", "subject_code": "DAA301", "title": "Dynamic Programming Case Study", "due_date": "2026-08-05"}
            ],
            "studentAnalytics": {
                "internal_average": 86.5,
                "subjects_count": len(attendance_report),
                "assignments_pending": 1,
                "exam_countdown": 7
            }
        }
