from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.schemas.auth import UserCreate, UserResponse
from app.api.deps import require_super_admin

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_admin_user(
    user_in: UserCreate,
    current_super_admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    """
    Super Admin endpoint to create new Admin and Super Admin accounts.
    Only accessible by users with SUPER_ADMIN role.
    """
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        role=user_in.role,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("", response_model=List[UserResponse])
def list_users(
    current_super_admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    """
    Super Admin endpoint to list all platform users and their roles.
    """
    return db.query(User).order_by(User.id.asc()).all()
