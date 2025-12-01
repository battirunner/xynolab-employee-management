from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text, Numeric, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum
from datetime import datetime, timedelta, timezone
import secrets

class InvitationStatus(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"

class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    status = Column(Enum(InvitationStatus), default=InvitationStatus.PENDING)
    
    # Employee data that admin wants to set
    employee_id = Column(String, unique=True, index=True, nullable=False)
    hire_date = Column(Date, nullable=False)
    department = Column(String)
    position = Column(String)
    base_salary = Column(Numeric(10, 2))
    
    # Timestamps
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = datetime.now(timezone.utc) + timedelta(days=7)  # 7 days expiry

    @property
    def is_expired(self):
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_valid(self):
        return self.status == InvitationStatus.PENDING and not self.is_expired