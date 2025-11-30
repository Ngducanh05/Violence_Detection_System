from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class AnnotationBase(BaseModel):
    segment_id: int
    frame_index: int
    bbox: Dict[str, Any]
    class_name: Optional[str] = None
    confidence: Optional[float] = None


# FE không được gửi annotated_by
class AnnotationCreate(AnnotationBase):
    pass


class AnnotationUpdate(BaseModel):
    bbox: Optional[Dict[str, Any]] = None
    class_name: Optional[str] = None
    confidence: Optional[float] = None


class AnnotationResponse(AnnotationBase):
    annotation_id: int
    annotated_by: int
    created_at: datetime

    class Config:
        orm_mode = True
