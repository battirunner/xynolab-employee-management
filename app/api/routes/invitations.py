from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_password_hash
from app.models.user import User, UserRole
from app.models.employee import Employee
from app.models.invitation import Invitation, InvitationStatus
from app.schemas.invitation import InvitationAccept, InvitationAcceptResponse

router = APIRouter()

@router.post("/accept", response_model=InvitationAcceptResponse)
async def accept_invitation(
    invitation_data: InvitationAccept,
    db: Session = Depends(get_db)
):
    # Find invitation by token
    invitation = db.query(Invitation).filter(Invitation.token == invitation_data.token).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Invalid invitation token")
    
    # Check if invitation is valid
    if not invitation.is_valid:
        raise HTTPException(status_code=400, detail="Invitation has expired or already been used")
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == invitation_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if user with invitation email already exists
    existing_user_email = db.query(User).filter(User.email == invitation.email).first()
    if existing_user_email:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    try:
        # Create user account
        hashed_password = get_password_hash(invitation_data.password)
        db_user = User(
            username=invitation_data.username,
            email=invitation.email,
            hashed_password=hashed_password,
            role=UserRole.EMPLOYEE
        )
        db.add(db_user)
        db.flush()  # Flush to get user ID
        
        # Create employee record with admin-provided data + employee-provided data
        db_employee = Employee(
            user_id=db_user.id,
            employee_id=invitation.employee_id,
            first_name=invitation_data.first_name,
            last_name=invitation_data.last_name,
            phone=invitation_data.phone,
            address=invitation_data.address,
            date_of_birth=invitation_data.date_of_birth,
            hire_date=invitation.hire_date,
            department=invitation.department,
            position=invitation.position,
            base_salary=invitation.base_salary
        )
        db.add(db_employee)
        
        # Mark invitation as accepted
        invitation.status = InvitationStatus.ACCEPTED
        
        db.commit()
        db.refresh(db_user)
        db.refresh(db_employee)
        
        return InvitationAcceptResponse(
            message="Invitation accepted successfully. Your account has been created.",
            user_id=db_user.id,
            employee_id=db_employee.id
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create account")

@router.get("/validate/{token}")
async def validate_invitation_token(
    token: str,
    db: Session = Depends(get_db)
):
    """Validate if an invitation token is valid and return basic invitation info"""
    invitation = db.query(Invitation).filter(Invitation.token == token).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Invalid invitation token")
    
    if not invitation.is_valid:
        raise HTTPException(status_code=400, detail="Invitation has expired or already been used")
    
    return {
        "email": invitation.email,
        "employee_id": invitation.employee_id,
        "position": invitation.position,
        "department": invitation.department,
        "hire_date": invitation.hire_date,
        "expires_at": invitation.expires_at
    }