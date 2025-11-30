from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ResultBase(BaseModel):
    run_id: Optional[int] = None
    video_id: Optional[int] = None
    segment_id: Optional[int] = None
    detected_label: Optional[str] = None
    confidence: Optional[float] = None
    frame_index: Optional[int] = None
    bbox: Optional[Dict[str, Any]] = None


class ResultCreate(ResultBase):
    pass


class ResultResponse(ResultBase):
    result_id: int
    created_at: datetime

    class Config:
        orm_mode = True
