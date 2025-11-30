from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SegmentBase(BaseModel):
    video_id: int
    start_time: float
    end_time: float
    label: Optional[str] = None


# FE không gửi created_by
class SegmentCreate(SegmentBase):
    pass


class SegmentUpdate(BaseModel):
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    label: Optional[str] = None


class SegmentResponse(SegmentBase):
    segment_id: int
    created_by: int
    created_at: datetime

    class Config:
        orm_mode = True
