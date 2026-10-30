from datetime import datetime, timezone
from typing import Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Anggota, CalonAnggota
from app.schemas.anggota import AnggotaCreate, AnggotaResponse, AnggotaCreateResponse
from app.schemas.calon_anggota import (
  CalonAnggotaCreate, CalonAnggotaResponse, CalonAnggotaListResponse,
  PendaftaranBerhasil, TolakCalonAnggota
)
from app.security import require_role
from app.services.anggota_service import create_anggota_and_account

router = APIRouter(
  prefix="/pendaftaran",
  tags=["pendaftaran"]
)

def get_calon_pending(calon_id: int, db: Session) -> CalonAnggota:
  calon = db.query(CalonAnggota).filter(CalonAnggota.id == calon_id).first()
  if not calon:
    raise HTTPException(status.HTTP_404_NOT_FOUND, "Calon anggota tidak ditemukan")
  if calon.status != "pending":
    raise HTTPException(status.HTTP_409_CONFLICT, f"Pendaftaran sudah berstatus {calon.status}")
  return calon

@router.post('/create', response_model=PendaftaranBerhasil, status_code=status.HTTP_201_CREATED)
def daftar(data: CalonAnggotaCreate, db: Session = Depends(get_db)):
  if db.query(Anggota).filter(Anggota.nim == data.nim, Anggota.deleted_at.is_(None)).first():
    raise HTTPException(status.HTTP_409_CONFLICT, "NIM sudah terdaftar sebagai anggota")

  if db.query(CalonAnggota).filter(CalonAnggota.nim == data.nim, CalonAnggota.status == "pending").first():
    raise HTTPException(status.HTTP_409_CONFLICT, "Pendaftaran dengan nim ini sedang diproses")

  calon = CalonAnggota(**data.model_dump())
  db.add(calon)

  try:
    db.commit()
  except IntegrityError:
    db.rollback()
    raise HTTPException(status.HTTP_409_CONFLICT, "Pendaftaran dengan nim ini sedang diproses")

  db.refresh(calon)
  return {"detail":"Pendaftaran berhasil dikirim", "id": calon.id}

@router.get("/get", response_model=CalonAnggotaListResponse)
def daftar_calon(
  current_user = Depends(require_role(['pengurus'])),
  q: Optional[str] = None,
  status_calon: Literal["pending", "diterima", "ditolak"] = Query("pending", alias="status"),
  page: int = Query(1, ge=1),
  limit: int = Query(10, ge=1, le=100),
  db: Session = Depends(get_db),
):
  query = db.query(CalonAnggota).filter(CalonAnggota.status == status_calon)
  if q:
    like = f"%{q}%"
    query = query.filter(or_(CalonAnggota.nama_lengkap.ilike(like), CalonAnggota.nim.ilike(like)))

  total = query.count()
  items = query.order_by(
    CalonAnggota.tanggal_daftar.desc()
  ).offset((page - 1) * limit).limit(limit).all()

  return {"items": items, "total": total, "page": page,"limit": limit}

@router.post("/tolak/{calon_id}", response_model=CalonAnggotaResponse)
def tolak_calon(
  calon_id: int,
  body: TolakCalonAnggota,
  current_user = Depends(require_role(['pengurus'])),
  db: Session = Depends(get_db)
):
  calon = get_calon_pending(calon_id, db)
  calon.status = "ditolak"
  calon.catatan_penolakan = body.catatan_penolakan
  calon.diproses_oleh = current_user.id
  calon.tanggal_diproses = datetime.now(timezone.utc)
  db.commit()
  db.refresh(calon)
  return calon

@router.post("/terima/{calon_id}", response_model=AnggotaCreateResponse)
def terima(
  calon_id: int,
  current_user = Depends(require_role(['pengurus'])),
  db: Session = Depends(get_db)
):
  calon = get_calon_pending(calon_id, db)

  if db.query(Anggota).filter(Anggota.nim == calon.nim, Anggota.deleted_at.is_(None)).first():
    raise HTTPException(status.HTTP_409_CONFLICT, "NIM sudah terdaftar sebagai anggota")

  data = AnggotaCreate(
    nama_lengkap=calon.nama_lengkap, nim=calon.nim, prodi=calon.prodi,
    email=calon.email, no_hp=calon.no_hp
  )

  try:
    hasil = create_anggota_and_account(db=db, anggota=data)
    calon.status = "diterima"
    calon.diproses_oleh = current_user.id
    calon.tanggal_diproses = datetime.now(timezone.utc)
    calon.anggota_id = hasil['anggota'].id
    db.commit()
  except IntegrityError:
    db.rollback()
    raise HTTPException(status.HTTP_409_CONFLICT, "Data bentrok, mungkin sudah diproses pengurus lain")

  db.refresh(hasil['anggota'])
  respons = AnggotaResponse.model_validate(hasil['anggota']).model_dump()
  respons['password_awal'] = hasil['raw_password']
  return respons