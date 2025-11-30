from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ModelRunBase(BaseModel):
    model_id: int
    project_id: Optional[int] = None
    status: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class ModelRunCreate(ModelRunBase):
    model_id: int


class ModelRunResponse(ModelRunBase):
    run_id: int
    started_at: datetime
    finished_at: Optional[datetime] = None

    class Config:
        orm_mode = True
