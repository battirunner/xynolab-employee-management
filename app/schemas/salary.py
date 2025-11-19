from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal
from app.models.salary import SalaryStatus

class SalaryRecordBase(BaseModel):
    month: int
    year: int
    base_amount: Decimal
    overtime_amount: Decimal = 0
    deductions: Decimal = 0
    bonus: Decimal = 0
    net_amount: Decimal

class SalaryRecordCreate(SalaryRecordBase):
    employee_id: int

class SalaryRecordUpdate(BaseModel):
    base_amount: Optional[Decimal] = None
    overtime_amount: Optional[Decimal] = None
    deductions: Optional[Decimal] = None
    bonus: Optional[Decimal] = None
    net_amount: Optional[Decimal] = None
    status: Optional[SalaryStatus] = None
    payment_date: Optional[date] = None

class SalaryRecordResponse(SalaryRecordBase):
    id: int
    employee_id: int
    status: SalaryStatus
    payment_date: Optional[date]

    class Config:
        from_attributes = True