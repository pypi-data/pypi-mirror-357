from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import Optional, List, Dict
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    roles: List[str] = Field(default_factory=lambda: ["user"])
    email_verified: bool = False
    phone_verified: bool = False
    profile_picture: Optional[HttpUrl] = None
    social_ids: Optional[Dict[str, str]] = Field(default_factory=dict)

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=128)
    profile_picture: Optional[HttpUrl] = None
    roles: Optional[List[str]] = None
    is_active: Optional[bool] = None

    class Config:
        orm_mode = True


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime


class UserInDB(UserRead):
    hashed_password: str
