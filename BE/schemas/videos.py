from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VideoBase(BaseModel):
    project_id: Optional[int] = None
    filename: Optional[str] = None
    storage_path: Optional[str] = None
    duration_seconds: Optional[float] = None
    fps: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    source: Optional[str] = None


# FE chỉ gửi filename + storage_path + project_id
class VideoCreate(VideoBase):
    filename: str
    storage_path: str


# BE trả về uploaded_by cho FE biết
class VideoResponse(VideoBase):
    video_id: int
    uploaded_by: int
    uploaded_at: datetime

    class Config:
        orm_mode = True
