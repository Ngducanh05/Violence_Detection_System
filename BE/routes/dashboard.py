from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from database.deps import get_db
from models.db_models import Videos, Results
from services.auth_dependency import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    user_id = current_user.user_id

    # ===========================================================
    # 1. Chỉ thống kê VIDEO của user đang login
    # ===========================================================
    total_videos = (
        db.query(Videos)
        .filter(Videos.uploaded_by == user_id)
        .count()
    )

    # ===========================================================
    # 2. Thống kê tất cả RESULTS thuộc video của user
    #    Results không tự chứa owner_id nên phải JOIN
    # ===========================================================
    violent_count = (
        db.query(Results)
        .join(Videos, Results.video_id == Videos.video_id)
        .filter(Videos.uploaded_by == user_id)
        .filter(Results.detected_label == "violent")
        .count()
    )

    avg_confidence = (
        db.query(func.avg(Results.confidence))
        .join(Videos, Results.video_id == Videos.video_id)
        .filter(Videos.uploaded_by == user_id)
        .scalar() or 0
    )
    avg_confidence = round(avg_confidence * 100, 1)

    # ===========================================================
    # 3. Recent activities của user (limit 5)
    # ===========================================================
    recent_activities = (
        db.query(Results)
        .join(Videos, Results.video_id == Videos.video_id)
        .filter(Videos.uploaded_by == user_id)
        .order_by(Results.created_at.desc())
        .limit(5)
        .all()
    )

    recent_list = []
    for item in recent_activities:
        video = db.query(Videos).filter(Videos.video_id == item.video_id).first()
        recent_list.append({
            "id": item.result_id,
            "label": item.detected_label,
            "confidence": item.confidence,
            "time": item.created_at.strftime("%H:%M %d/%m"),
            "video_name": video.filename if video else "Unknown"
        })

    # ===========================================================
    # 4. Chart 7 ngày gần nhất (theo video user)
    # ===========================================================
    chart_data = []
    today = datetime.now().date()

    for i in range(6, -1, -1):
        current = today - timedelta(days=i)
        day_label = current.strftime("%d/%m")

        safe_count = (
            db.query(Results)
            .join(Videos)
            .filter(Videos.uploaded_by == user_id)
            .filter(Results.detected_label != "violent")
            .filter(func.date(Results.created_at) == current)
            .count()
        )

        violent_day_count = (
            db.query(Results)
            .join(Videos)
            .filter(Videos.uploaded_by == user_id)
            .filter(Results.detected_label == "violent")
            .filter(func.date(Results.created_at) == current)
            .count()
        )

        chart_data.append({
            "name": day_label,
            "safe": safe_count,
            "violent": violent_day_count
        })

    return {
        "total_videos": total_videos,
        "total_violence": violent_count,
        "avg_confidence": avg_confidence,
        "recent_activities": recent_list,
        "chart_data": chart_data
    }
