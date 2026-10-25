from datetime import datetime, timedelta, timezone
import secrets, bcrypt, string, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import User

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRED = settings.ACCESS_TOKEN_EXPIRE

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_password_hash(password: str) -> str:
  password_bytes = password.encode('utf-8')

  if len(password_bytes) > 72:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Password terlalu panjang! Maksimal 72 byte."
    )

  salt = bcrypt.gensalt()
  hashed_bytes = bcrypt.hashpw(password_bytes, salt)

  return hashed_bytes.decode('utf-8') 

def verify_password(typed_pass, saved_hash):
  if isinstance(typed_pass, str):
    typed_pass = typed_pass.encode('utf-8')
  if isinstance(saved_hash, str):
    saved_hash = saved_hash.encode('utf-8')

  return bcrypt.checkpw(typed_pass, saved_hash)

def get_random_pwd():
  lower = "" . join([c for c in string.ascii_lowercase if c not in 'ol'])
  upper = "" . join([c for c in string.ascii_uppercase if c not in 'OI'])
  num = "" . join([c for c in string.digits if c not in '01'])

  strings = lower + upper + num

  length_strings = secrets.choice([10, 11, 12])

  random_pwd = "".join(secrets.choice(strings) for _ in range(length_strings))

  return random_pwd

def create_access_token(user_id):
  time_now = datetime.now(timezone.utc)
  time_exp = time_now + timedelta(minutes=ACCESS_TOKEN_EXPIRED)

  payload = {
    "sub" : str(user_id),
    "exp" : time_exp
  }

  token_teks = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

  return token_teks

def get_current_user(
  token: str = Depends(oauth2_scheme),
  db: Session = Depends(get_db),
):
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Tidak dapat memvalidasi kredensial",
    headers={"WWW-Authenticate" : "Bearer"}
  )

  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    sub = payload.get("sub")
    if sub is None:
      raise credentials_exception
    user_id = int(sub)

  except (jwt.PyJWTError, ValueError):
    raise credentials_exception

  user = db.query(User).filter(User.id == user_id).first()
  if user is None:
    raise credentials_exception

  if not user.is_active:
    raise credentials_exception

  if user.anggota and user.anggota.deleted_at is not None:
    raise credentials_exception

  return user

def require_role(
  list_role: list[str]
):
  def verify_role(user = Depends(get_current_user)):
    if user.role not in list_role:
      raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Anda tidak memiliki akses!"
      )
    return user

  return verify_role