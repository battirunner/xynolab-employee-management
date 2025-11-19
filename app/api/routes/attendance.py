from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_active_user, require_admin
from app.models.user import User
from app.models.employee import Employee
from app.models.attendance import Attendance, AttendanceStatus
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate, AttendanceResponse

router = APIRouter()

@router.post("/check-in")
async def check_in(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee record not found")
    
    today = date.today()
    existing_attendance = db.query(Attendance).filter(
        Attendance.employee_id == employee.id,
        Attendance.date == today
    ).first()
    
    if existing_attendance:
        if existing_attendance.check_in_time:
            raise HTTPException(status_code=400, detail="Already checked in today")
        existing_attendance.check_in_time = datetime.now()
        existing_attendance.status = AttendanceStatus.PRESENT
    else:
        attendance = Attendance(
            employee_id=employee.id,
            date=today,
            check_in_time=datetime.now(),
            status=AttendanceStatus.PRESENT
        )
        db.add(attendance)
    
    db.commit()
    return {"message": "Checked in successfully", "time": datetime.now()}

@router.post("/check-out")
async def check_out(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee record not found")
    
    today = date.today()
    attendance = db.query(Attendance).filter(
        Attendance.employee_id == employee.id,
        Attendance.date == today
    ).first()
    
    if not attendance or not attendance.check_in_time:
        raise HTTPException(status_code=400, detail="Must check in first")
    
    if attendance.check_out_time:
        raise HTTPException(status_code=400, detail="Already checked out today")
    
    attendance.check_out_time = datetime.now()
    db.commit()
    return {"message": "Checked out successfully", "time": datetime.now()}

@router.post("/", response_model=AttendanceResponse)
async def submit_attendance(
    attendance: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee record not found")
    
    existing_attendance = db.query(Attendance).filter(
        Attendance.employee_id == employee.id,
        Attendance.date == attendance.date
    ).first()
    
    if existing_attendance:
        raise HTTPException(status_code=400, detail="Attendance already submitted for this date")
    
    db_attendance = Attendance(
        employee_id=employee.id,
        **attendance.dict()
    )
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

@router.get("/my-attendance", response_model=List[AttendanceResponse])
async def get_my_attendance(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee record not found")
    
    query = db.query(Attendance).filter(Attendance.employee_id == employee.id)
    
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    
    attendance_records = query.order_by(Attendance.date.desc()).all()
    return attendance_records

@router.get("/employee/{employee_id}", response_model=List[AttendanceResponse])
async def get_employee_attendance(
    employee_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    query = db.query(Attendance).filter(Attendance.employee_id == employee_id)
    
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    
    attendance_records = query.order_by(Attendance.date.desc()).all()
    return attendance_records

@router.put("/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance(
    attendance_id: int,
    attendance_update: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    db_attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not db_attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    update_data = attendance_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_attendance, field, value)
    
    db.commit()
    db.refresh(db_attendance)
    return db_attendance