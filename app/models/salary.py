from sqlalchemy import Column, Integer, DateTime, Date, ForeignKey, Enum, Numeric, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class SalaryStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"

class SalaryRecord(Base):
    __tablename__ = "salary_records"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    base_amount = Column(Numeric(10, 2), nullable=False)
    overtime_amount = Column(Numeric(10, 2), default=0)
    deductions = Column(Numeric(10, 2), default=0)
    bonus = Column(Numeric(10, 2), default=0)
    net_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(SalaryStatus), default=SalaryStatus.PENDING)
    payment_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    employee = relationship("Employee", back_populates="salary_records")