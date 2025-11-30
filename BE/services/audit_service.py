from sqlalchemy.orm import Session
from models.db_models import AuditLogs
from datetime import datetime


# Hàm ghi log — user_id luôn đến từ JWT, KHÔNG BAO GIỜ từ FE
def create_audit_log(db: Session, user_id: int, action: str, object_type: str = None, object_id: int = None):
    try:
        new_log = AuditLogs(
            user_id=user_id,
            action=action,
            object_type=object_type,
            object_id=object_id,
            created_at=datetime.now()
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        return new_log

    except Exception as e:
        print(f"Lỗi ghi log: {e}")
        return None


# Lấy log của riêng user (NOTIFICATION)
def get_user_notifications(db: Session, user_id: int, limit: int = 10):
    return (
        db.query(AuditLogs)
        .filter(AuditLogs.user_id == user_id)
        .order_by(AuditLogs.created_at.desc())
        .limit(limit)
        .all()
    )


# Lấy tất cả log – dành cho admin
def get_all_audit_logs(db: Session):
    return (
        db.query(AuditLogs)
        .order_by(AuditLogs.created_at.desc())
        .all()
    )
