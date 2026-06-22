from pydantic import BaseModel
from typing import Optional

class StudentProfileBase(BaseModel):
    roll_number: str
    admission_number: str
    section_id: int
    parent_name: Optional[str] = None
    parent_mobile: Optional[str] = None
    parent_email: Optional[str] = None
    address: Optional[str] = None

class StudentProfileCreate(StudentProfileBase):
    pass

class StudentProfileOut(StudentProfileBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

class FacultyProfileBase(BaseModel):
    employee_id: str
    department_id: int

class FacultyProfileCreate(FacultyProfileBase):
    pass

class FacultyProfileOut(FacultyProfileBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True
