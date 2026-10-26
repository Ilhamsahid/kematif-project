from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime,timezone
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas.auth import Token, UserResponse, PasswordChange
from app.security import verify_password, get_password_hash, create_access_token, get_current_user

router = APIRouter(
  prefix="/auth",
  tags=["auth"]
)

@router.post("/login", response_model=Token)
def login(
  form_data: OAuth2PasswordRequestForm = Depends(),
  db: Session = Depends(get_db),
):
  username = form_data.username.strip().upper()
  user = db.query(User).filter(func.upper(User.username) == username).first()

  if not user or not verify_password(form_data.password, user.password_hash):
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Username atau Password salah",
      headers={"WWW-Authenticate": "Bearer"},
    )

  if not user.is_active or (user.anggota and user.anggota.deleted_at is not None):
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="Akun tidak aktif",
    )

  user.last_login_at = datetime.now(timezone.utc)
  db.commit()
  token = create_access_token(user.id)

  return {
    "access_token": token,
    "token_type": "bearer"
  }

@router.get('/me', response_model=UserResponse)
def get_me(user = Depends(get_current_user)):
  return user

@router.post('/change-password')
def change_password(
  pwd: PasswordChange,
  user = Depends(get_current_user),
  db: Session = Depends(get_db),
):
  cekpassword_lama = verify_password(pwd.password_lama, user.password_hash)
  cekpassword_baru = verify_password(pwd.password_baru, user.password_hash)

  if not cekpassword_lama or cekpassword_baru:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Password lama salah" if not cekpassword_lama else "Password baru sama dengan password lama",
    )

  pwd_baru = get_password_hash(pwd.password_baru)
  user.password_hash = pwd_baru
  db.commit()

  return {
    "detail": "Password berhasil diubah"
  }
