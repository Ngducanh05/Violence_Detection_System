from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EventBase(BaseModel):
    video_id: int
    segment_id: Optional[int] = None
    detected_by_run: Optional[int] = None
    severity: Optional[int] = 1
    description: Optional[str] = None


class EventCreate(EventBase):
    pass  # FE không gửi created_by


class EventResponse(EventBase):
    event_id: int
    created_by: int   # thêm dòng này
    created_at: datetime

    class Config:
        orm_mode = True
