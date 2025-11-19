#!/usr/bin/env python3

import asyncio
from app.core.database import SessionLocal, get_db
from app.core.auth import get_password_hash
from app.models.user import User, UserRole

def create_admin_user():
    db = SessionLocal()
    try:
        # Check if admin already exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            print("Admin user already exists!")
            return

        # Create admin user
        password = "admin123"
        hashed_password = get_password_hash(password)
        admin_user = User(
            username="admin",
            email="admin@company.com",
            hashed_password=hashed_password,
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Admin user created successfully!")
        print(f"Username: admin")
        print(f"Password: admin123")
        print(f"Email: admin@company.com")
        print("\n⚠️  Please change the password after first login!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()