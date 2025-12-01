from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from app.schemas.user import UserResponse

class EmployeeBase(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    hire_date: date
    department: Optional[str] = None
    position: Optional[str] = None
    base_salary: Optional[Decimal] = None

class EmployeeCreate(EmployeeBase):
    user_id: int

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    department: Optional[str] = None
    position: Optional[str] = None
    base_salary: Optional[Decimal] = None

class EmployeeResponse(EmployeeBase):
    id: int
    user_id: int
    user: Optional[UserResponse] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True