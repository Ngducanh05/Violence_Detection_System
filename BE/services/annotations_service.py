from sqlalchemy.orm import Session
from models.db_models import Annotations
from schemas.annotations import AnnotationCreate, AnnotationUpdate


def get_annotations_by_segment(db: Session, segment_id: int):
    return db.query(Annotations).filter(Annotations.segment_id == segment_id).all()


def get_annotation_by_id(db: Session, annotation_id: int):
    return db.query(Annotations).filter(Annotations.annotation_id == annotation_id).first()


def create_annotation(db: Session, data: AnnotationCreate, annotated_by: int):
    ann = Annotations(
        segment_id=data.segment_id,
        frame_index=data.frame_index,
        bbox=data.bbox,
        class_name=data.class_name,
        confidence=data.confidence,
        annotated_by=annotated_by
    )
    db.add(ann)
    db.commit()
    db.refresh(ann)
    return ann


def update_annotation(db: Session, annotation_id: int, data: AnnotationUpdate):
    ann = get_annotation_by_id(db, annotation_id)
    if not ann:
        return None

    if data.bbox is not None:
        ann.bbox = data.bbox
    if data.class_name is not None:
        ann.class_name = data.class_name
    if data.confidence is not None:
        ann.confidence = data.confidence

    db.commit()
    db.refresh(ann)
    return ann


def delete_annotation(db: Session, annotation_id: int):
    ann = get_annotation_by_id(db, annotation_id)
    if not ann:
        return False
    db.delete(ann)
    db.commit()
    return True
