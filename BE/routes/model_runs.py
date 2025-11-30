from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.deps import get_db
from schemas.model_runs import ModelRunCreate, ModelRunResponse
from services.model_runs_service import (
    get_all_model_runs,
    get_model_run_by_id,
    create_model_run,
    finish_model_run
)
from services.projects_service import get_project_by_id
from services.auth_dependency import get_current_user

router = APIRouter(prefix="/model_runs", tags=["Model Runs"])


# ======================================================
# LIST MODEL RUNS — chỉ run thuộc project của user
# ======================================================
@router.get("/", response_model=list[ModelRunResponse])
def list_runs(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    runs = get_all_model_runs(db)
    filtered = []

    for r in runs:
        project = get_project_by_id(db, r.project_id)
        if project and project.owner_id == current_user.user_id:
            filtered.append(r)

    return filtered


# ======================================================
# GET ONE RUN — chỉ owner được xem
# ======================================================
@router.get("/{run_id}", response_model=ModelRunResponse)
def get_run(
    run_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    run = get_model_run_by_id(db, run_id)
    if not run:
        raise HTTPException(404, "Run không tồn tại")

    project = get_project_by_id(db, run.project_id)

    if not project or project.owner_id != current_user.user_id:
        raise HTTPException(403, "Bạn không có quyền xem run này")

    return run


# ======================================================
# CREATE RUN — user chỉ tạo run cho project của họ
# ======================================================
@router.post("/", response_model=ModelRunResponse)
def create_run(
    data: ModelRunCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    project = get_project_by_id(db, data.project_id)

    if not project or project.owner_id != current_user.user_id:
        raise HTTPException(403, "Bạn không thể tạo run cho project của người khác")

    return create_model_run(db, data)


# ======================================================
# FINISH RUN — chỉ owner được finish
# ======================================================
@router.post("/{run_id}/finish", response_model=ModelRunResponse)
def finish_run_route(
    run_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    run = get_model_run_by_id(db, run_id)
    if not run:
        raise HTTPException(404, "Run không tồn tại")

    project = get_project_by_id(db, run.project_id)

    if not project or project.owner_id != current_user.user_id:
        raise HTTPException(403, "Bạn không thể cập nhật run của người khác")

    return finish_model_run(db, run_id)
