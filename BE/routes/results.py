from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from database.deps import get_db
from schemas.results import ResultCreate, ResultResponse
from services.results_service import (
    get_results_by_video,
    get_results_by_segment,
    get_results_by_run,
    create_result,
)

from services.videos_service import get_video_by_id
from services.segments_service import get_segment_by_id
from services.model_runs_service import get_model_run_by_id
from services.projects_service import get_project_by_id

from models.db_models import Results, Videos
from services.auth_dependency import get_current_user

router = APIRouter(prefix="/results", tags=["Results"])


# ======================================================
# 1. SUMMARY RESULTS BY VIDEO – dùng cho trang Audit
# ======================================================
@router.get("/my")
def get_my_results_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user_id = current_user.user_id

    rows = (
        db.query(
            Results.video_id.label("video_id"),
            func.max(Results.created_at).label("last_time"),
            func.count().label("total_frames"),
            func.sum(
                case((Results.detected_label == "violent", 1), else_=0)
            ).label("violent_frames"),
            func.avg(Results.confidence).label("avg_confidence"),
        )
        .join(Videos, Results.video_id == Videos.video_id)
        .filter(Videos.uploaded_by == user_id)
        .group_by(Results.video_id)
        .order_by(func.max(Results.created_at).desc())
        .all()
    )

    return [
        {
            "video_id": r.video_id,
            "last_time": r.last_time,
            "total_frames": r.total_frames,
            "violent_frames": r.violent_frames,
            "avg_confidence": float(r.avg_confidence or 0),
            "is_violent": r.violent_frames > 0
        }
        for r in rows
    ]


# ======================================================
# 2. GET RESULTS BY VIDEO — chỉ owner được xem
# ======================================================
@router.get("/video/{video_id}", response_model=list[ResultResponse])
def list_results_for_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    video = get_video_by_id(db, video_id)

    if not video or video.uploaded_by != current_user.user_id:
        raise HTTPException(403, "Bạn không có quyền xem kết quả video này")

    return get_results_by_video(db, video_id)


# ======================================================
# 3. GET RESULTS BY SEGMENT — chỉ owner được xem
# ======================================================
@router.get("/segment/{segment_id}", response_model=list[ResultResponse])
def list_results_for_segment(
    segment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    segment = get_segment_by_id(db, segment_id)

    if not segment or segment.created_by != current_user.user_id:
        raise HTTPException(403, "Bạn không có quyền xem kết quả của segment này")

    return get_results_by_segment(db, segment_id)


# ======================================================
# 4. GET RESULTS BY RUN — chỉ owner được xem
# ======================================================
@router.get("/run/{run_id}", response_model=list[ResultResponse])
def list_results_for_run(
    run_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    run = get_model_run_by_id(db, run_id)

    if not run:
        raise HTTPException(404, "Run không tồn tại")

    project = get_project_by_id(db, run.project_id)

    if not project or project.owner_id != current_user.user_id:
        raise HTTPException(403, "Bạn không có quyền xem kết quả của run này")

    return get_results_by_run(db, run_id)


# ======================================================
# 5. CREATE RESULT — dùng nội bộ pipeline
# ======================================================
@router.post("/", response_model=ResultResponse)
def create_new_result(
    data: ResultCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return create_result(db, data)
