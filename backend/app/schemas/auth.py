from pydantic import BaseModel, ConfigDict, Field
from typing import Literal
from datetime import datetime

class Token(BaseModel):
  access_token: str
  token_type: str = "bearer"

class UserResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: int
  username: str
  role: Literal["pengurus", "bendahara", "anggota"]
  is_active: bool 
  anggota_id: int
  last_login_at: datetime | None = None

class PasswordChange(BaseModel):
  password_lama: str
  password_baru: str = Field(min_length=8, max_length=72)

class UserRoleUpdate(BaseModel):
  role: Literal["pengurus", "bendahara", "anggota"]