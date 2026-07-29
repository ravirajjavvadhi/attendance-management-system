import json
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.models.attendance import (
    AttendanceRecord, AttendanceSummary, SubjectSummary, 
    FacultySummary, DepartmentSummary, InstitutionSummary, AttendanceStatusEnum
)
from app.models.academic import Section, Class, Department, AcademicSession
from app.models.erp_academic import Subject, Timetable
from app.models.profiles import StudentProfile, FacultyProfile
from app.services.subject_code_service import SubjectCodeService

class MaterializedSummaryEngine:
    """
    Hierarchical Materialized Reporting Engine.
    Event-driven engine that updates 5 tiers of summary tables without blocking or rescanning history on every read report request.
    """

    @staticmethod
    def process_attendance_submission(db: Session, tenant_id: int, section_id: int, subject_id: int, faculty_id: int, submission_date: date, student_ids: list[int]):
        """
        Main entrypoint called by /submit and /submit/smart endpoints after records are saved.
        Updates Tier 1 to Tier 5 summaries.
        """
        # Determine active academic session
        active_session = db.query(AcademicSession).filter(
            AcademicSession.tenant_id == tenant_id,
            AcademicSession.is_current == True
        ).first()
        session_id = active_session.id if active_session else None

        # ── TIER 1: STUDENT & SUBJECT LEVEL SUMMARY ──
        for std_id in student_ids:
            MaterializedSummaryEngine._update_student_summary(db, tenant_id, std_id, subject_id, session_id)

        # ── TIER 2: SUBJECT LEVEL SUMMARY ──
        if subject_id:
            MaterializedSummaryEngine._update_subject_summary(db, tenant_id, subject_id, section_id, session_id)

        # ── TIER 3: FACULTY LEVEL SUMMARY ──
        if faculty_id:
            MaterializedSummaryEngine._update_faculty_summary(db, tenant_id, faculty_id, session_id)

        # ── TIER 4 & 5: DEPARTMENT & INSTITUTION SUMMARIES ──
        section = db.query(Section).filter(Section.id == section_id).first()
        if section and section.class_id:
            cls_obj = db.query(Class).filter(Class.id == section.class_id).first()
            if cls_obj and cls_obj.department_id:
                MaterializedSummaryEngine._update_department_summary(db, tenant_id, cls_obj.department_id, session_id)

        MaterializedSummaryEngine._update_institution_summary(db, tenant_id, session_id, submission_date)

        try:
            db.commit()
        except Exception as e:
            db.rollback()

    @staticmethod
    def _update_student_summary(db: Session, tenant_id: int, student_id: int, subject_id: int, session_id: int):
        # 1. Update specific subject summary for student
        if subject_id:
            query = db.query(AttendanceRecord).filter(
                AttendanceRecord.tenant_id == tenant_id,
                AttendanceRecord.student_id == student_id,
                AttendanceRecord.subject_id == subject_id
            )
            if session_id:
                query = query.filter(AttendanceRecord.academic_session_id == session_id)
            records = query.all()

            total = len(records)
            attended = sum(1 for r in records if r.is_present or r.status == AttendanceStatusEnum.PRESENT.value or r.status == AttendanceStatusEnum.ON_DUTY.value)
            ml_count = sum(1 for r in records if r.status == AttendanceStatusEnum.MEDICAL_LEAVE.value)
            od_count = sum(1 for r in records if r.status == AttendanceStatusEnum.ON_DUTY.value)

            pct = round((attended / total) * 100.0, 2) if total > 0 else 100.0
            is_shortage = (pct < 75.0) if total > 0 else False
            shortage_pct = round(75.0 - pct, 2) if is_shortage else 0.0

            summary = db.query(AttendanceSummary).filter(
                AttendanceSummary.tenant_id == tenant_id,
                AttendanceSummary.student_id == student_id,
                AttendanceSummary.subject_id == subject_id,
                AttendanceSummary.academic_session_id == session_id,
                AttendanceSummary.month == None
            ).first()

            if not summary:
                summary = AttendanceSummary(
                    tenant_id=tenant_id,
                    student_id=student_id,
                    subject_id=subject_id,
                    academic_session_id=session_id,
                    month=None
                )
                db.add(summary)

            summary.total_classes = total
            summary.attended_classes = attended
            summary.percentage = pct
            summary.medical_leave_count = ml_count
            summary.od_count = od_count
            summary.is_shortage = is_shortage
            summary.shortage_percentage = shortage_pct
            db.flush()

        # 2. Update overall summary for student across all subjects in session
        ov_query = db.query(AttendanceRecord).filter(
            AttendanceRecord.tenant_id == tenant_id,
            AttendanceRecord.student_id == student_id
        )
        if session_id:
            ov_query = ov_query.filter(AttendanceRecord.academic_session_id == session_id)
        ov_records = ov_query.all()
        ov_total = len(ov_records)
        ov_attended = sum(1 for r in ov_records if r.is_present or r.status == AttendanceStatusEnum.PRESENT.value or r.status == AttendanceStatusEnum.ON_DUTY.value)
        ov_ml = sum(1 for r in ov_records if r.status == AttendanceStatusEnum.MEDICAL_LEAVE.value)
        ov_od = sum(1 for r in ov_records if r.status == AttendanceStatusEnum.ON_DUTY.value)
        ov_pct = round((ov_attended / ov_total) * 100.0, 2) if ov_total > 0 else 100.0
        ov_shortage = (ov_pct < 75.0) if ov_total > 0 else False
        ov_short_pct = round(75.0 - ov_pct, 2) if ov_shortage else 0.0

        ov_summary = db.query(AttendanceSummary).filter(
            AttendanceSummary.tenant_id == tenant_id,
            AttendanceSummary.student_id == student_id,
            AttendanceSummary.subject_id == None,
            AttendanceSummary.academic_session_id == session_id,
            AttendanceSummary.month == None
        ).first()

        if not ov_summary:
            ov_summary = AttendanceSummary(
                tenant_id=tenant_id,
                student_id=student_id,
                subject_id=None,
                academic_session_id=session_id,
                month=None
            )
            db.add(ov_summary)

        ov_summary.total_classes = ov_total
        ov_summary.attended_classes = ov_attended
        ov_summary.percentage = ov_pct
        ov_summary.medical_leave_count = ov_ml
        ov_summary.od_count = ov_od
        ov_summary.is_shortage = ov_shortage
        ov_summary.shortage_percentage = ov_short_pct
        db.flush()

    @staticmethod
    def _update_subject_summary(db: Session, tenant_id: int, subject_id: int, section_id: int, session_id: int):
        query = db.query(AttendanceSummary).filter(
            AttendanceSummary.tenant_id == tenant_id,
            AttendanceSummary.subject_id == subject_id,
            AttendanceSummary.academic_session_id == session_id
        )
        sums = query.all()
        if not sums:
            return

        total_sessions = max(s.total_classes for s in sums) if sums else 0
        total_std_attendances = sum(s.total_classes for s in sums)
        total_presents = sum(s.attended_classes for s in sums)
        avg_pct = round(sum(s.percentage for s in sums) / len(sums), 2) if sums else 0.0
        shortage_cnt = sum(1 for s in sums if s.is_shortage)

        sub_sum = db.query(SubjectSummary).filter(
            SubjectSummary.tenant_id == tenant_id,
            SubjectSummary.subject_id == subject_id,
            SubjectSummary.section_id == section_id,
            SubjectSummary.academic_session_id == session_id
        ).first()

        if not sub_sum:
            sub_sum = SubjectSummary(
                tenant_id=tenant_id,
                subject_id=subject_id,
                section_id=section_id,
                academic_session_id=session_id
            )
            db.add(sub_sum)

        sub_sum.total_sessions_conducted = total_sessions
        sub_sum.total_student_attendances = total_std_attendances
        sub_sum.total_presents = total_presents
        sub_sum.average_percentage = avg_pct
        sub_sum.shortage_student_count = shortage_cnt
        db.flush()

    @staticmethod
    def _update_faculty_summary(db: Session, tenant_id: int, faculty_user_id: int, session_id: int):
        assigned = db.query(Timetable).filter(
            Timetable.tenant_id == tenant_id,
            Timetable.faculty_user_id == faculty_user_id
        ).count() * 15 # Estimated semester periods per weekly slot

        completed = db.query(AttendanceRecord.session_id).filter(
            AttendanceRecord.tenant_id == tenant_id,
            AttendanceRecord.marked_by == faculty_user_id
        ).distinct().count()

        pending = max(0, assigned - completed) if assigned > 0 else 0
        rate = round(min(100.0, (completed / assigned) * 100.0), 2) if assigned > 0 else 100.0

        fac_sum = db.query(FacultySummary).filter(
            FacultySummary.tenant_id == tenant_id,
            FacultySummary.faculty_user_id == faculty_user_id,
            FacultySummary.academic_session_id == session_id
        ).first()

        if not fac_sum:
            fac_sum = FacultySummary(
                tenant_id=tenant_id,
                faculty_user_id=faculty_user_id,
                academic_session_id=session_id
            )
            db.add(fac_sum)

        fac_sum.total_assigned_periods = assigned
        fac_sum.periods_completed = completed
        fac_sum.pending_submissions = pending
        fac_sum.attendance_completion_rate = rate
        db.flush()

    @staticmethod
    def _update_department_summary(db: Session, tenant_id: int, department_id: int, session_id: int):
        classes = db.query(Class.id).filter(Class.department_id == department_id, Class.tenant_id == tenant_id).all()
        class_ids = [c[0] for c in classes]
        if not class_ids:
            return

        sections = db.query(Section).filter(Section.class_id.in_(class_ids), Section.tenant_id == tenant_id).all()
        sec_ids = [s.id for s in sections]
        if not sec_ids:
            return

        stds = db.query(StudentProfile).filter(StudentProfile.section_id.in_(sec_ids)).all()
        std_ids = [s.id for s in stds]
        if not std_ids:
            return

        sums = db.query(AttendanceSummary).filter(
            AttendanceSummary.tenant_id == tenant_id,
            AttendanceSummary.student_id.in_(std_ids),
            AttendanceSummary.subject_id == None,
            AttendanceSummary.academic_session_id == session_id
        ).all()

        avg_rate = round(sum(s.percentage for s in sums) / len(sums), 2) if sums else 100.0
        shortage_cnt = sum(1 for s in sums if s.is_shortage)

        dept_sum = db.query(DepartmentSummary).filter(
            DepartmentSummary.tenant_id == tenant_id,
            DepartmentSummary.department_id == department_id,
            DepartmentSummary.academic_session_id == session_id
        ).first()

        if not dept_sum:
            dept_sum = DepartmentSummary(
                tenant_id=tenant_id,
                department_id=department_id,
                academic_session_id=session_id
            )
            db.add(dept_sum)

        dept_sum.total_students = len(std_ids)
        dept_sum.average_attendance_rate = avg_rate
        dept_sum.shortage_student_count = shortage_cnt
        db.flush()

    @staticmethod
    def _update_institution_summary(db: Session, tenant_id: int, session_id: int, snap_date: date):
        stds = db.query(StudentProfile).count()
        today_recs = db.query(AttendanceRecord).filter(
            AttendanceRecord.tenant_id == tenant_id,
            AttendanceRecord.date == snap_date
        ).all()

        present_students = {r.student_id for r in today_recs if r.is_present or r.status in [AttendanceStatusEnum.PRESENT.value, AttendanceStatusEnum.ON_DUTY.value]}
        present_cnt = len(present_students)
        absent_cnt = stds - present_cnt if stds >= present_cnt else 0
        total_marked = stds
        rate = round((present_cnt / total_marked) * 100.0, 2) if total_marked > 0 else 100.0

        # Build departmental ranking JSON
        depts = db.query(DepartmentSummary).filter(DepartmentSummary.tenant_id == tenant_id, DepartmentSummary.academic_session_id == session_id).all()
        rankings = []
        for d in sorted(depts, key=lambda x: x.average_attendance_rate, reverse=True):
            d_obj = db.query(Department).filter(Department.id == d.department_id).first()
            rankings.append({
                "department_id": d.department_id,
                "name": d_obj.name if d_obj else f"Dept {d.department_id}",
                "rate": d.average_attendance_rate,
                "shortage": d.shortage_student_count
            })

        inst_sum = db.query(InstitutionSummary).filter(
            InstitutionSummary.tenant_id == tenant_id,
            InstitutionSummary.academic_session_id == session_id,
            InstitutionSummary.date == snap_date
        ).first()

        if not inst_sum:
            inst_sum = InstitutionSummary(
                tenant_id=tenant_id,
                academic_session_id=session_id,
                date=snap_date
            )
            db.add(inst_sum)

        inst_sum.total_students = stds
        inst_sum.present_today = present_cnt
        inst_sum.absent_today = absent_cnt
        inst_sum.attendance_rate = rate
        inst_sum.department_rankings_json = json.dumps(rankings)
        db.flush()

materialized_summary_engine = MaterializedSummaryEngine()
