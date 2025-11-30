from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# CHỈ dùng cho field chung (không chứa owner_id nữa)
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


# FE chỉ gửi name + description
# KHÔNG được gửi owner_id
class ProjectCreate(ProjectBase):
    pass


# Update cũng chỉ cho sửa name, description
class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# Response trả về cho FE
# Có owner_id vì đây là dữ liệu BE gửi ra, không phải FE gửi lên
class ProjectResponse(ProjectBase):
    project_id: int
    owner_id: int
    created_at: datetime

    class Config:
        orm_mode = True
