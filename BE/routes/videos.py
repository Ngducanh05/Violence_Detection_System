from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import shutil
import os

from services.results_service import get_results_by_video
from services.video_render_service import render_video_with_overlay
from database.deps import get_db
from schemas.videos import VideoCreate, VideoResponse
from services.videos_service import (
    get_all_videos,
    get_video_by_id,
    get_videos_by_project,
    create_video_record,
    delete_video_record
)

# 🔥 AUTH
from services.auth_dependency import get_current_user

router = APIRouter(prefix="/videos", tags=["Videos"])

UPLOAD_DIR = "uploads/videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ======================================================
# GET ALL VIDEOS – chỉ video của user đang login
# ======================================================
@router.get("/", response_model=list[VideoResponse])
def list_videos(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_all_videos(db, owner_id=current_user.user_id)


# ======================================================
# GET VIDEO BY ID – chỉ lấy của user đang login
# ======================================================
@router.get("/{video_id}", response_model=VideoResponse)
def fetch_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    video = get_video_by_id(db, video_id)

    if not video or video.uploaded_by != current_user.user_id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem video này")

    return video


# ======================================================
# LIST VIDEOS BY PROJECT – chỉ project user đang login
# ======================================================
@router.get("/project/{project_id}", response_model=list[VideoResponse])
def list_videos_by_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_videos_by_project(db, project_id, owner_id=current_user.user_id)


# ======================================================
# UPLOAD VIDEO – uploaded_by = current_user.user_id
# ======================================================
@router.post("/upload", response_model=VideoResponse)
async def upload_video(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Lưu file
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Tạo record trong DB
    data = VideoCreate(
        project_id=project_id,
        filename=file.filename,
        storage_path=file_location
    )

    video = create_video_record(db, data, uploaded_by=current_user.user_id)
    return video


# ======================================================
# DELETE VIDEO – chỉ chủ video được xoá
# ======================================================
@router.delete("/{video_id}")
def delete_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    video = get_video_by_id(db, video_id)

    if not video or video.uploaded_by != current_user.user_id:
        raise HTTPException(403, "Bạn không có quyền xoá video này")

    delete_video_record(db, video_id)
    return {"message": "Video deleted successfully"}
 #======================================================
# EXPORT VIDEO WITH OVERLAY — chỉ owner được xem
@router.get("/{video_id}/render")
def export_video_overlay(
    video_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    video = get_video_by_id(db, video_id)

    if not video or video.uploaded_by != current_user.user_id:
        raise HTTPException(403, "Bạn không có quyền xử lý video này")

    timeline = [
        {"frame": r.frame_index, "score": r.confidence}
        for r in get_results_by_video(db, video_id)
    ]

    input_path = video.storage_path
    output_path = f"rendered/{video.filename}"

    os.makedirs("rendered", exist_ok=True)

    render_video_with_overlay(input_path, output_path, timeline)

    return {"download_url": f"/static/{output_path}"}
