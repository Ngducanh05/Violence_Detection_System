from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.deps import get_db
from schemas.annotations import AnnotationCreate, AnnotationUpdate, AnnotationResponse
from services.annotations_service import (
    get_annotations_by_segment,
    get_annotation_by_id,
    create_annotation,
    update_annotation,
    delete_annotation,
)

from services.auth_dependency import get_current_user

router = APIRouter(prefix="/annotations", tags=["Annotations"])


# =============================
# LIST ANNOTATIONS (user only)
# =============================
@router.get("/segment/{segment_id}", response_model=list[AnnotationResponse])
def list_annotations(
    segment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    anns = get_annotations_by_segment(db, segment_id)

    # Lọc theo user
    return [a for a in anns if a.annotated_by == current_user.user_id]


# =============================
# GET ONE ANNOTATION
# =============================
@router.get("/{annotation_id}", response_model=AnnotationResponse)
def fetch_annotation(
    annotation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    ann = get_annotation_by_id(db, annotation_id)

    if not ann or ann.annotated_by != current_user.user_id:
        raise HTTPException(403, "Bạn không có quyền xem annotation này")

    return ann


# =============================
# CREATE
# =============================
@router.post("/", response_model=AnnotationResponse)
def create_new_annotation(
    data: AnnotationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return create_annotation(db, data, annotated_by=current_user.user_id)


# =============================
# UPDATE
# =============================
@router.put("/{annotation_id}", response_model=AnnotationResponse)
def update_annotation_item(
    annotation_id: int,
    data: AnnotationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    ann = get_annotation_by_id(db, annotation_id)

    if not ann or ann.annotated_by != current_user.user_id:
        raise HTTPException(403, "Bạn không có quyền sửa annotation này")

    return update_annotation(db, annotation_id, data)


# =============================
# DELETE
# =============================
@router.delete("/{annotation_id}")
def delete_annotation_item(
    annotation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    ann = get_annotation_by_id(db, annotation_id)

    if not ann or ann.annotated_by != current_user.user_id:
        raise HTTPException(403, "Bạn không có quyền xoá annotation này")

    delete_annotation(db, annotation_id)
    return {"message": "Annotation deleted successfully"}
