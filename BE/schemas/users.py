from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = "annotator"

class UserCreate(UserBase):
    name: str
    email: EmailStr
    password: str  # <--- THÊM DÒNG NÀY VÀO
    role: Optional[str] = "annotator"

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None


class UserResponse(UserBase):
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True
