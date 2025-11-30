from sqlalchemy.orm import Session
from models.db_models import Users
from schemas.users import UserCreate, UserUpdate
import bcrypt  # <--- Thay đổi ở đây

# --- HÀM MỚI DÙNG BCRYPT ---
def hash_password(password: str):
    # Chuyển password thành bytes, hash nó, rồi decode về string để lưu DB
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain: str, hashed: str):
    # Kiểm tra mật khẩu nhập vào với hash trong DB
    pwd_bytes = plain.encode('utf-8')
    hashed_bytes = hashed.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)
# ---------------------------

def get_all_users(db: Session):
    return db.query(Users).all()

def get_user_by_id(db: Session, user_id: int):
    return db.query(Users).filter(Users.user_id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(Users).filter(Users.email == email).first()

def create_user(db: Session, data: UserCreate):
    # Lấy password người dùng nhập, nếu không có thì mặc định "123456"
    # Quan trọng: Phải dùng password thật từ biến data, đừng fix cứng "123456" nữa
    pwd_to_hash = data.password if hasattr(data, 'password') and data.password else "123456"
    
    new_user = Users(
        name=data.name,
        email=data.email,
        role=data.role,
        password=hash_password(pwd_to_hash) # Hash password thật
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_user(db: Session, user_id: int, data: UserUpdate):
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    if data.name:
        user.name = data.name
    if data.role:
        user.role = data.role

    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True