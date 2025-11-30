from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import shutil
import os

from database.deps import get_db
from services.auth_dependency import get_current_user

from services.videos_service import create_video_record
from services.results_service import get_results_by_run
from services.segments_service import get_segment_by_id
from services.events_service import get_event_by_id
from services.detect_service import run_violence_pipeline

router = APIRouter(prefix="/detect", tags=["Detect"])

UPLOAD_DIR = "uploaded_videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/video")
async def detect_video(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    # 1. Lưu file video
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb+") as out:
        shutil.copyfileobj(file.file, out)

    # Reset pointer để process_video có thể đọc file lại
    file.file.seek(0)

    # 2. Tạo record video trong DB
    video = create_video_record(
    db,
    data={
        "project_id": project_id,
        "filename": file.filename,
        "storage_path": file_path,
    },
    uploaded_by=current_user.user_id
)

    # 3. Chạy pipeline AI
    pipeline = await run_violence_pipeline(
        db=db,
        file=file,
        project_id=project_id,
        user_id=current_user.user_id
    )

    run_id = pipeline["run_id"]

    # 4. Gán video_id cho Results
    results = get_results_by_run(db, run_id)
    for r in results:
        r.video_id = video.video_id
    db.commit()

    # 5. Gán video_id cho Segments
    for s in pipeline["segments"]:
        seg = get_segment_by_id(db, s["id"])
        if seg:
            seg.video_id = video.video_id
    db.commit()

    # 6. Gán video_id cho Events
    for e in pipeline["events"]:
        ev = get_event_by_id(db, e["id"])
        if ev:
            ev.video_id = video.video_id
    db.commit()

    # 7. Trả kết quả chuẩn FE
    return {
        "video_id": video.video_id,
        "run_id": run_id,
        "timeline": pipeline["timeline"],
        "segments": pipeline["segments"],
        "events": pipeline["events"],
    }
