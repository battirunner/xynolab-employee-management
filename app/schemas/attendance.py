from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from app.models.attendance import AttendanceStatus

class AttendanceBase(BaseModel):
    date: date
    status: AttendanceStatus
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    notes: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    status: Optional[AttendanceStatus] = None
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    notes: Optional[str] = None

class AttendanceResponse(AttendanceBase):
    id: int
    employee_id: int

    class Config:
        from_attributes = True