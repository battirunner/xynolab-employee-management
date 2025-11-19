from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import require_admin, get_password_hash
from app.models.user import User
from app.models.employee import Employee
from app.models.salary import SalaryRecord, SalaryStatus
from app.schemas.user import UserCreate, UserResponse
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.schemas.salary import SalaryRecordUpdate, SalaryRecordResponse
from app.services.email_service import send_salary_update_notification

router = APIRouter()

@router.post("/users", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    db_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    users = db.query(User).all()
    return users

@router.get("/employees", response_model=List[EmployeeResponse])
async def get_all_employees(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    employees = db.query(Employee).all()
    return employees

@router.post("/employees", response_model=EmployeeResponse)
async def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == employee.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing_employee = db.query(Employee).filter(Employee.user_id == employee.user_id).first()
    if existing_employee:
        raise HTTPException(status_code=400, detail="Employee already exists for this user")
    
    db_employee = Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@router.put("/employees/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    employee_update: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    update_data = employee_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_employee, field, value)
    
    db.commit()
    db.refresh(db_employee)
    return db_employee

@router.put("/salary-records/{salary_id}", response_model=SalaryRecordResponse)
async def update_salary_record(
    salary_id: int,
    salary_update: SalaryRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    db_salary = db.query(SalaryRecord).filter(SalaryRecord.id == salary_id).first()
    if not db_salary:
        raise HTTPException(status_code=404, detail="Salary record not found")
    
    old_status = db_salary.status
    update_data = salary_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_salary, field, value)
    
    db.commit()
    db.refresh(db_salary)
    
    if old_status != db_salary.status and db_salary.status == SalaryStatus.PAID:
        employee = db.query(Employee).filter(Employee.id == db_salary.employee_id).first()
        user = db.query(User).filter(User.id == employee.user_id).first()
        await send_salary_update_notification(user.email, employee, db_salary)
    
    return db_salary

@router.get("/employees/{employee_id}/salary-records", response_model=List[SalaryRecordResponse])
async def get_employee_salary_records(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    salary_records = db.query(SalaryRecord).filter(SalaryRecord.employee_id == employee_id).all()
    return salary_records