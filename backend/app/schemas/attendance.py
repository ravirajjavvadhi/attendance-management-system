from pydantic import BaseModel
from typing import List
from datetime import date

class AttendanceRecordBase(BaseModel):
    student_id: int
    is_present: bool

class AttendanceSubmit(BaseModel):
    section_id: int
    date: date
    records: List[AttendanceRecordBase]

class SmartAttendanceSubmit(BaseModel):
    section_id: int
    date: date
    absent_student_ids: List[int]
