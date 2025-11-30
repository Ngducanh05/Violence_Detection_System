from sqlalchemy.orm import Session
from models.db_models import Results
from schemas.results import ResultCreate


def get_results_by_video(db: Session, video_id: int):
    return db.query(Results).filter(Results.video_id == video_id).all()


def get_results_by_segment(db: Session, segment_id: int):
    return db.query(Results).filter(Results.segment_id == segment_id).all()


def get_results_by_run(db: Session, run_id: int):
    return db.query(Results).filter(Results.run_id == run_id).all()


def create_result(db: Session, data: dict):
    result = Results(
        run_id=data["run_id"],
        video_id=data["video_id"],
        segment_id=data["segment_id"],
        detected_label=data["detected_label"],
        confidence=data["confidence"],
        frame_index=data["frame_index"],
        bbox=data.get("bbox")
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result
