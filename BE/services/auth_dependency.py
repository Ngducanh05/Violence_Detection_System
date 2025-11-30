from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database.deps import get_db
from services.auth_service import decode_token
from services.users_service import get_user_by_id

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    payload = decode_token(token)
    if not payload:
        raise HTTPException(401, "Token không hợp lệ hoặc đã hết hạn")

    # Chặn refresh token dùng như access
    if payload.get("type") == "refresh":
        raise HTTPException(401, "Refresh token không dùng để truy cập API")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(401, "Token không hợp lệ")

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(404, "User không tồn tại")

    return user
