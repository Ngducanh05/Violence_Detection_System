from sqlalchemy.orm import Session
from datetime import datetime
from models.db_models import ModelRuns
from schemas.model_runs import ModelRunCreate


def get_all_model_runs(db: Session):
    return db.query(ModelRuns).all()


def get_model_run_by_id(db: Session, run_id: int):
    return db.query(ModelRuns).filter(ModelRuns.run_id == run_id).first()


def create_model_run(db: Session, data: ModelRunCreate):
    run = ModelRuns(
        model_id=data.model_id,
        project_id=data.project_id,
        status="running",
        config=data.config
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def finish_model_run(db: Session, run_id: int):
    run = get_model_run_by_id(db, run_id)
    if not run:
        return None
    run.status = "finished"
    run.finished_at = datetime.utcnow()
    db.commit()
    db.refresh(run)
    return run
