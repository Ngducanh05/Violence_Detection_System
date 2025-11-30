from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.deps import get_db
from schemas.users import UserCreate, UserUpdate, UserResponse
from services.users_service import (
    get_all_users,
    get_user_by_id,
    create_user,
    update_user,
    delete_user,
    get_user_by_email
)

from services.auth_dependency import get_current_user

# >>> ADD
from services.projects_service import create_project
from schemas.projects import ProjectCreate
# <<< ADD

router = APIRouter(prefix="/users", tags=["Users"])


# ============================
# REGISTER (public)
# ============================
@router.post("/register")
def register_user(data: UserCreate, db: Session = Depends(get_db)):

    existing_user = get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(400, "Email đã được sử dụng")

    new_user = create_user(db, data)

    # >>> ADD — auto create default project
    create_project(
        db,
        ProjectCreate(
            name="Default Project",
            description="Auto-created for new user"
        ),
        owner_id=new_user.user_id
    )
    # <<< ADD

    return {"message": "Tạo tài khoản thành công", "user_id": new_user.user_id}


# ============================
# LIST USERS (admin only)
# ============================
@router.get("/", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(403, "Chỉ admin được xem toàn bộ user")
    return get_all_users(db)


# ============================
# GET USER BY ID
# ============================
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if current_user.role != "admin" and current_user.user_id != user_id:
        raise HTTPException(403, "Bạn không có quyền xem user này")

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    return user


# ============================
# CREATE USER (admin only)
# ============================
@router.post("/", response_model=UserResponse)
def create_new_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(403, "Chỉ admin được tạo user")

    return create_user(db, data)


# ============================
# UPDATE USER
# ============================
@router.put("/{user_id}", response_model=UserResponse)
def update_user_info(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if current_user.role != "admin" and current_user.user_id != user_id:
        raise HTTPException(403, "Bạn không có quyền sửa user này")

    updated = update_user(db, user_id, data)
    if not updated:
        raise HTTPException(404, "User not found")

    return updated


# ============================
# DELETE USER (admin only)
# ============================
@router.delete("/{user_id}")
def remove_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if current_user.role != "admin":
        raise HTTPException(403, "Chỉ admin được xoá user")

    success = delete_user(db, user_id)
    if not success:
        raise HTTPException(404, "User not found")

    return {"message": "User deleted successfully"}
