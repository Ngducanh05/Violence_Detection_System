from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.deps import get_db
from services.users_service import get_user_by_email, verify_password
from services.auth_service import create_access_token
from models.db_models import AuditLogs
from datetime import datetime
from services.audit_service import create_audit_log
from services.auth_service import create_refresh_token
from services.auth_service import decode_token

router = APIRouter(prefix="/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(400, "Email không tồn tại")

    if not verify_password(data.password, user.password):
        raise HTTPException(400, "Mật khẩu không đúng")

    access_token = create_access_token({"sub": str(user.user_id)})
    refresh_token = create_refresh_token({"sub": str(user.user_id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "user_id": user.user_id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/refresh")
def refresh_token(data: RefreshRequest):
    payload = decode_token(data.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(401, "Refresh token không hợp lệ")

    user_id = payload.get("sub")

    new_access = create_access_token({"sub": user_id})
    new_refresh = create_refresh_token({"sub": user_id})

    return {
        "access_token": new_access,
        "refresh_token": new_refresh
    }
