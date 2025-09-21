"""
Authentication routes for user management and JWT tokens
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from datetime import timedelta

from ...core.security import security_manager
from ...core.config import settings

router = APIRouter()


class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str
    expires_in: int


class UserCreate(BaseModel):
    """User creation model"""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    """User response model"""
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool


# Placeholder user database - replace with actual database
fake_users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@wakanda.africa",
        "full_name": "System Administrator",
        "hashed_password": security_manager.hash_password("wakanda2024"),
        "is_active": True,
    }
}


def authenticate_user(username: str, password: str):
    """Authenticate user credentials"""
    user = fake_users_db.get(username)
    if not user:
        return False
    if not security_manager.verify_password(password, user["hashed_password"]):
        return False
    return user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint to get access token"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.security.access_token_expire_minutes)
    access_token = security_manager.create_access_token(
        data={"sub": user["username"], "scopes": ["read", "write"]},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.security.access_token_expire_minutes * 60
    }


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register new user"""
    if user_data.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = security_manager.hash_password(user_data.password)
    
    fake_users_db[user_data.username] = {
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "hashed_password": hashed_password,
        "is_active": True,
    }
    
    return UserResponse(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        is_active=True
    )


@router.post("/refresh")
async def refresh_token():
    """Refresh access token"""
    # TODO: Implement refresh token logic
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Refresh token not implemented yet"
    )


@router.post("/logout")
async def logout():
    """Logout endpoint"""
    # TODO: Implement token blacklisting
    return {"message": "Successfully logged out"}