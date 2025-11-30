from sqlalchemy.orm import Session
from models.db_models import Videos
from schemas.videos import VideoCreate


# Trả về video của đúng user
def get_all_videos(db: Session, owner_id: int):
    return db.query(Videos).filter(Videos.uploaded_by == owner_id).all()


def get_video_by_id(db: Session, video_id: int):
    return db.query(Videos).filter(Videos.video_id == video_id).first()


def get_videos_by_project(db: Session, project_id: int, owner_id: int):
    return (
        db.query(Videos)
        .filter(Videos.project_id == project_id, Videos.uploaded_by == owner_id)
        .all()
    )


# CREATE VIDEO – uploaded_by là do route truyền vào
def create_video_record(db: Session, data, uploaded_by):
    video = Videos(
        project_id=data["project_id"],
        filename=data["filename"],
        storage_path=data["storage_path"],
        uploaded_by=uploaded_by
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return video



def delete_video_record(db: Session, video_id: int):
    video = get_video_by_id(db, video_id)
    if not video:
        return False

    db.delete(video)
    db.commit()
    return True
