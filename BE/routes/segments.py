from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.deps import get_db
from schemas.segments import SegmentCreate, SegmentUpdate, SegmentResponse
from services.segments_service import (
    get_segments_by_video,
    get_segment_by_id,
    create_segment,
    update_segment,
    delete_segment,
)

from services.auth_dependency import get_current_user

router = APIRouter(prefix="/segments", tags=["Segments"])


@router.get("/video/{video_id}", response_model=list[SegmentResponse])
def list_segments_for_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_segments_by_video(db, video_id, owner_id=current_user.user_id)


@router.get("/{segment_id}", response_model=SegmentResponse)
def get_segment(
    segment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    seg = get_segment_by_id(db, segment_id)

    if not seg or seg.created_by != current_user.user_id:
        raise HTTPException(403, "Bạn không có quyền xem segment này")

    return seg


@router.post("/", response_model=SegmentResponse)
def create_new_segment(
    data: SegmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return create_segment(db, data, created_by=current_user.user_id)


@router.put("/{segment_id}", response_model=SegmentResponse)
def update_segment_info(
    segment_id: int,
    data: SegmentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    seg = get_segment_by_id(db, segment_id)

    if not seg or seg.created_by != current_user.user_id:
        raise HTTPException(403, "Bạn không có quyền sửa segment này")

    return update_segment(db, segment_id, data)


@router.delete("/{segment_id}")
def delete_segment_item(
    segment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    seg = get_segment_by_id(db, segment_id)

    if not seg or seg.created_by != current_user.user_id:
        raise HTTPException(403, "Bạn không có quyền xoá segment này")

    delete_segment(db, segment_id)
    return {"message": "Segment deleted successfully"}
