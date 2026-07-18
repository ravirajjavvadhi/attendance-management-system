from app.models.tenant import Institution, InstitutionModules
from app.models.user import User
from app.models.academic import AcademicYear, Department, Course, Class, Section
from app.models.profiles import StudentProfile, FacultyProfile, ParentProfile, ParentStudentLink
from app.models.attendance import AttendanceRecord
from app.models.notification import NotificationLog, SMSTemplate
from app.models.erp_academic import Branch, Semester, Subject, Period, Timetable
from app.models.calendar import SemesterTerm, CalendarDay
from app.models.examination import Exam, ExamResult
from app.models.assignment import Assignment, AssignmentSubmission
from app.models.communication import CampusNotice, TimelineEvent
