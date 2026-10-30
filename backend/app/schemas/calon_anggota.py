from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Literal, Optional
from datetime import datetime
from app.schemas.anggota import NIM_PATTERN, HP_PATTERN

class CalonAnggotaCreate(BaseModel):
  model_config = ConfigDict(str_strip_whitespace=True)

  nama_lengkap: str = Field(min_length=3, max_length=100)
  nim: str = Field(pattern=NIM_PATTERN)
  prodi: str = Field(min_length=2, max_length=100)
  email: Optional[EmailStr] = None
  no_hp: str = Field(pattern=HP_PATTERN)
  alasan_bergabung: str = Field(min_length=1, max_length=300)

  @field_validator("nim")
  @classmethod
  def nim_huruf_besar(cls, v: str) -> str:
    return v.upper()

class PendaftaranBerhasil(BaseModel):
  detail: str
  id: int

class TolakCalonAnggota(BaseModel):
  catatan_penolakan: Optional[str] = Field(None, max_length=300)

class CalonAnggotaResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: int
  nama_lengkap: str
  nim: str
  prodi: str
  email: Optional[str] = None
  no_hp: str
  alasan_bergabung: Optional[str] = None
  status: Literal['pending', 'diterima', 'ditolak']
  tanggal_daftar: datetime
  diproses_oleh: Optional[int] = None
  tanggal_diproses: Optional[datetime] = None
  catatan_penolakan: Optional[str] = None
  anggota_id: Optional[int] = None

class CalonAnggotaListResponse(BaseModel):
  items: list[CalonAnggotaResponse]
  total: int
  page: int
  limit: int