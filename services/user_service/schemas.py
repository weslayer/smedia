from pydantic import BaseModel, EmailStr, validator, Field
from typing import Annotated, Optional
from datetime import datetime
import re

class UserBase(BaseModel):
    email: EmailStr
    username: Annotated[str, Field(min_length=3, max_length=50)]
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None

class UserCreate(UserBase):
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v

    @validator('full_name')
    def validate_full_name(cls, v):
        if v is not None:
            if len(v.strip()) < 2:
                raise ValueError('Full name must be at least 2 characters long')
            if not re.match(r'^[a-zA-Z\s-]+$', v):
                raise ValueError('Full name can only contain letters, spaces, and hyphens')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[Annotated[str, Field(min_length=3, max_length=50)]] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None

    @validator('password')
    def validate_password(cls, v):
        if v is not None:
            if len(v) < 8:
                raise ValueError('Password must be at least 8 characters long')
            if not re.search(r'[A-Z]', v):
                raise ValueError('Password must contain at least one uppercase letter')
            if not re.search(r'[a-z]', v):
                raise ValueError('Password must contain at least one lowercase letter')
            if not re.search(r'\d', v):
                raise ValueError('Password must contain at least one number')
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
                raise ValueError('Password must contain at least one special character')
        return v

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 