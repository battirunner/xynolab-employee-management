from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.employee import Employee
from app.models.salary import SalaryRecord
from app.schemas.employee import EmployeeResponse
from app.schemas.salary import SalaryRecordResponse

router = APIRouter()

@router.get("/me", response_model=EmployeeResponse)
async def get_my_employee_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee record not found")
    return employee

@router.get("/me/salary-records", response_model=List[SalaryRecordResponse])
async def get_my_salary_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee record not found")
    
    salary_records = db.query(SalaryRecord).filter(SalaryRecord.employee_id == employee.id).all()
    return salary_records