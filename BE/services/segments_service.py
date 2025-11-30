from sqlalchemy.orm import Session
from models.db_models import Segments
from schemas.segments import SegmentCreate, SegmentUpdate


def get_segments_by_video(db: Session, video_id: int):
    return db.query(Segments).filter(Segments.video_id == video_id).all()


def get_segment_by_id(db: Session, segment_id: int):
    return db.query(Segments).filter(Segments.segment_id == segment_id).first()


def create_segment(db: Session, data: dict, created_by: int):
    seg = Segments(
        video_id=data.get("video_id"),
        start_time=data.get("start_time"),
        end_time=data.get("end_time"),
        label=data.get("label", "violence"),
        created_by=created_by
    )
    db.add(seg)
    db.commit()
    db.refresh(seg)
    return seg




def update_segment(db: Session, segment_id: int, data: SegmentUpdate):
    seg = get_segment_by_id(db, segment_id)
    
    if not seg:
        return None

    if data.start_time is not None:
        seg.start_time = data.start_time
    if data.end_time is not None:
        seg.end_time = data.end_time
    if data.label is not None:
        seg.label = data.label
        

    db.commit()
    db.refresh(seg)
    return seg


def delete_segment(db: Session, segment_id: int):
    seg = get_segment_by_id(db, segment_id)
    if not seg:
        return False
    db.delete(seg)
    db.commit()
    return True
