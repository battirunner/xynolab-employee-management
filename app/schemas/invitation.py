from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from app.models.invitation import InvitationStatus

class InvitationCreate(BaseModel):
    email: EmailStr
    employee_id: str
    hire_date: date
    department: Optional[str] = None
    position: Optional[str] = None
    base_salary: Optional[Decimal] = None

class InvitationResponse(BaseModel):
    id: int
    email: EmailStr
    employee_id: str
    status: InvitationStatus
    hire_date: date
    department: Optional[str] = None
    position: Optional[str] = None
    base_salary: Optional[Decimal] = None
    expires_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class InvitationAccept(BaseModel):
    token: str
    # User data that employee sets themselves
    username: str
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None

class InvitationAcceptResponse(BaseModel):
    message: str
    user_id: int
    employee_id: int