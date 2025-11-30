from sqlalchemy.orm import Session
from models.db_models import Events
from schemas.events import EventCreate


def get_events_by_video(db: Session, video_id: int):
    return db.query(Events).filter(Events.video_id == video_id).all()


def get_event_by_id(db: Session, event_id: int):
    return db.query(Events).filter(Events.event_id == event_id).first()


def create_event(db: Session, data: dict, created_by: int):
    ev = Events(
        video_id=data.get("video_id"),
        segment_id=data.get("segment_id"),
        detected_by_run=data.get("detected_by_run"),   # nullable
        severity=data.get("severity", 1),              # default severity
        description=data.get("description", "violence detected"),
        created_by=created_by
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev




def delete_event(db: Session, event_id: int):
    ev = get_event_by_id(db, event_id)
    if not ev:
        return False
    db.delete(ev)
    db.commit()
    return True
