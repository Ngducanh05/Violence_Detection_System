from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.deps import get_db
from services.audit_service import get_user_notifications, get_all_audit_logs
from services.auth_dependency import get_current_user

router = APIRouter(prefix="/audit", tags=["Audit"])


# ======================================================
# 1. Lấy toàn bộ Audit Logs — CHỈ ADMIN mới xem được
# ======================================================
@router.get("/", tags=["Audit"])
def get_all_logs(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if current_user.role == "admin":
     return get_all_audit_logs(db)

    return get_user_notifications(db, current_user.user_id)



# ======================================================
# 2. Lấy NOTIFICATIONS riêng của user đang login
# ======================================================
@router.get("/my-notifications")
def my_notifications(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_user_notifications(db, current_user.user_id)
