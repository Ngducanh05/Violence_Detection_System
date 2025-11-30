from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.deps import get_db
from schemas.events import EventCreate, EventResponse
from services.events_service import (
    get_events_by_video,
    get_event_by_id,
    create_event,
    delete_event,
)

from services.auth_dependency import get_current_user

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/video/{video_id}", response_model=list[EventResponse])
def list_events(
    video_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    events = get_events_by_video(db, video_id)
    return [e for e in events if e.created_by == current_user.user_id]


@router.get("/{event_id}", response_model=EventResponse)
def fetch_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    event = get_event_by_id(db, event_id)
    if not event or event.created_by != current_user.user_id:
        raise HTTPException(403, "Không có quyền xem event này")
    return event


@router.post("/", response_model=EventResponse)
def create_new_event(
    data: EventCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return create_event(db, data, created_by=current_user.user_id)


@router.delete("/{event_id}")
def delete_event_item(
    event_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    event = get_event_by_id(db, event_id)
    if not event or event.created_by != current_user.user_id:
        raise HTTPException(403, "Không có quyền xoá event này")

    delete_event(db, event_id)
    return {"message": "Event deleted successfully"}
