from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.deps import get_db
from schemas.projects import ProjectCreate, ProjectUpdate, ProjectResponse
from services.projects_service import (
    get_all_projects,
    get_project_by_id,
    create_project,
    update_project,
    delete_project,
)

# AUTH
from services.auth_dependency import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])


# ======================================================
# LIST PROJECTS – chỉ liệt kê project của user đang login
# ======================================================
@router.get("/", response_model=list[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_all_projects(db, owner_id=current_user.user_id)


# ======================================================
# GET PROJECT BY ID – user chỉ xem project của mình
# ======================================================
@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
    
):
    project = get_project_by_id(db, project_id)

    # CHẶN XEM PROJECT CỦA NGƯỜI KHÁC
    if not project or project.owner_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem project này")

    return project


# ======================================================
# CREATE PROJECT – owner_id = user_id (tự động)
# ======================================================
@router.post("/", response_model=ProjectResponse)
def create_new_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return create_project(db, data, owner_id=current_user.user_id)


# ======================================================
# UPDATE PROJECT – chỉ owner được phép sửa
# ======================================================
@router.put("/{project_id}", response_model=ProjectResponse)
def update_project_info(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    project = get_project_by_id(db, project_id)

    if not project or project.owner_id != current_user.user_id:
        raise HTTPException(403, "Bạn không có quyền sửa project này")

    return update_project(db, project_id, data)


# ======================================================
# DELETE PROJECT – chỉ owner được phép xoá
# ======================================================
@router.delete("/{project_id}")
def delete_project_item(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    project = get_project_by_id(db, project_id)

    if not project or project.owner_id != current_user.user_id:
        raise HTTPException(403, "Bạn không được phép xoá project này")

    delete_project(db, project_id)
    return {"message": "Project deleted successfully"}
