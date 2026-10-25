from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from typing import Literal, Optional
from datetime import date, datetime

NIM_PATTERN = r"^[eE]\d{8}$"
HP_PATTERN = r"^(08|\+62)\d{8,13}$"

class AnggotaBase(BaseModel):
  model_config = ConfigDict(str_strip_whitespace=True)

  nama_lengkap: str = Field(min_length=3, max_length=100)
  nim: str = Field(..., pattern=NIM_PATTERN, description="Format: E41261340")
  prodi: Optional[str] = None
  email: Optional[EmailStr] = None
  no_hp: Optional[str] = Field(None, pattern=HP_PATTERN)

  @field_validator("nim")
  @classmethod
  def nim_huruf_besar(cls, v:str ) -> str:
    return v.upper()

class AnggotaCreate(AnggotaBase):
  pass

class AnggotaUpdate(BaseModel):
  model_config = ConfigDict(str_strip_whitespace=True)

  nama_lengkap: Optional[str] = None
  nim: Optional[str] = Field(None, pattern=NIM_PATTERN, description="Format: e41261340")
  prodi: Optional[str] = None
  email: Optional[EmailStr] = None
  no_hp: Optional[str] = Field(None, pattern=HP_PATTERN)

  status_keanggotaan: Optional[Literal["aktif", "tidak_aktif"]] = None

  @field_validator("nama_lengkap", "nim", "status_keanggotaan")
  @classmethod
  def tidak_boleh_null(cls, v):
    if v is None:
      raise ValueError("Field ini tidak boleh null")
    return v

  @field_validator("nim")
  @classmethod
  def nim_huruf_besar(cls, v:str ) -> str:
    return v.upper()

class AnggotaResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: int
  nama_lengkap: str
  nim: str
  prodi: Optional[str] = None
  email: Optional[str] = None
  no_hp: Optional[str] = None
  status_keanggotaan: Literal["aktif", "tidak_aktif"]
  tanggal_bergabung: date
  created_at: datetime
  updated_at: datetime