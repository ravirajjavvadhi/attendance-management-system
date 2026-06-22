from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.token import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_superadmin(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != UserRole.SUPERADMIN.value or current_user.email not in ["ravirajjavvadhi@gmail.com", "ravirajjavvadi@gmail.com"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only SuperAdmin can perform this action"
        )
    return current_user

def get_current_management(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != UserRole.MANAGEMENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only Management can perform this action"
        )
    return current_user

def get_current_admin(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role not in [UserRole.MANAGEMENT.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only Management or Admin can perform this action"
        )
    return current_user

def get_current_faculty(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != UserRole.FACULTY.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only Faculty can perform this action"
        )
    return current_user

def get_current_management_or_faculty(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role not in [UserRole.MANAGEMENT.value, UserRole.FACULTY.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only Management or Faculty can perform this action"
        )
    return current_user
