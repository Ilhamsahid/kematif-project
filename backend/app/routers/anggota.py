from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from typing import Optional
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Anggota, User
from app.schemas.anggota import (
    AnggotaCreate, AnggotaUpdate, AnggotaResponse,
    AnggotaCreateResponse, AnggotaListResponse,
)
from app.schemas.auth import UserRoleUpdate
from app.security import require_role
from app.services.anggota_service import create_anggota_and_account

router = APIRouter(
  prefix="/anggota",
  tags=["anggota"]
)

def get_anggota404(
  id: int,
  db: Session
):
  anggota = db.query(Anggota).filter(Anggota.id == id, Anggota.deleted_at.is_(None)).first()

  if anggota:
    return anggota

  raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Data tidak ditemukan"
  )

@router.post('/create', response_model=AnggotaCreateResponse, status_code=status.HTTP_201_CREATED)
def create_anggota(
  anggota: AnggotaCreate,
  current_user = Depends(require_role(['pengurus'])),
  db: Session = Depends(get_db),
):
  existing_anggota = db.query(Anggota).filter(
    Anggota.nim == anggota.nim,
    Anggota.deleted_at.is_(None)
  ).first()

  if existing_anggota:
    raise HTTPException(
      status_code=status.HTTP_409_CONFLICT,
      detail=f"NIM {anggota.nim} sudah terdaftar dan masih aktif."
    )

  try:
    result = create_anggota_and_account(db=db, anggota=anggota)

    db.commit();

    db.refresh(result["anggota"]);

    return {
      **result["anggota"].__dict__,
      "password_awal" : result["raw_password"],
    }
  except IntegrityError:
    db.rollback()
    raise HTTPException(
      status_code=status.HTTP_409_CONFLICT,
      detail="Terjadi konflik data pada database. Silakan coba lagi."
    )

@router.get('/get-anggota', response_model=AnggotaListResponse)
def get_anggota(
  current_user = Depends(require_role(['pengurus', 'bendahara'])),
  q: Optional[str] = None,         # Kolom pencarian teks
  status: Optional[str] = None,    # Kolom filter status
  page: int = 1,
  limit: int = 10,
  db: Session = Depends(get_db)
):
  if limit > 100:
    limit = 100

  items_query = db.query(Anggota).filter(Anggota.deleted_at.is_(None))

  if q:
    teks_cari = f"%{q}%"
    items_query = items_query.filter(
      or_(
        Anggota.nama_lengkap.ilike(teks_cari),
        Anggota.nim.ilike(teks_cari)
      )
    )

  if status:
    items_query = items_query.filter(Anggota.status_keanggotaan == status)

  total_data = items_query.count()

  offset = (page - 1) * limit

  items = items_query.order_by(Anggota.id.desc()).offset(offset).limit(limit).all()

  return {
    "items": items,
    "total": total_data,
    "page": page,
    "limit": limit
  }

@router.get('/get/{anggota_id}', response_model=AnggotaResponse)
def get_anggota_first(
  anggota_id: int,
  current_user = Depends(require_role(['pengurus'])),
  db: Session = Depends(get_db)
):
  return get_anggota404(id=anggota_id, db=db)

@router.patch('/update/{anggota_id}', response_model=AnggotaResponse)
def update_anggota(
  anggota_id: int,
  anggota_update: AnggotaUpdate,
  current_user = Depends(require_role(['pengurus'])),
  db: Session = Depends(get_db)
):
  anggota = get_anggota404(anggota_id, db)

  anggota_update = anggota_update.model_dump(exclude_unset=True)

  if not anggota_update:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Tidak ada data yang diperbarui"
    )

  if "nim" in anggota_update and not anggota_update["nim"]:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Nim tidak boleh dikosongkan"
    )

  if "nama_lengkap" in anggota_update and not anggota_update["nama_lengkap"]:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Nama Lengkap tidak boleh dikosongkan"
    )

  for key, value in anggota_update.items():
    setattr(anggota, key, value)

  db.commit()
  db.refresh(anggota)

  return anggota

@router.delete('/delete/{anggota_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_anggota(
  anggota_id: int,
  current_user = Depends(require_role(['pengurus'])),
  db: Session = Depends(get_db),
):
  anggota = get_anggota404(anggota_id, db)

  if current_user.anggota and current_user.anggota.id == anggota.id:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Anda tidak dapat menghapus akun Anda sendiri!"
    )

  anggota.deleted_at = datetime.now(timezone.utc)

  if anggota.user:
    anggota.user.is_active = 0
    anggota.user.username = f"deleted_{anggota_id}.{anggota.user.username}"

  db.commit()
  return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.patch('/update/{anggota_id}/role', response_model=AnggotaResponse)
def update_role(
  anggota_id: int,
  role_data: UserRoleUpdate,
  current_user = Depends(require_role(['pengurus'])),
  db: Session = Depends(get_db),
):
  anggota = get_anggota404(anggota_id, db)

  if current_user.anggota and current_user.anggota.id == anggota.id:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Akun tidak bisa diubah perannya"
    )

  if not anggota.user:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Akun dengan anggota ini tidak ditemukan"
    )

  anggota.user.role = role_data.role

  db.commit()
  db.refresh(anggota)
  return anggota

@router.patch('/restore/{anggota_id}', status_code=status.HTTP_204_NO_CONTENT)
def restore(
  anggota_id: int,
  current_user = Depends(require_role(['pengurus'])),
  db: Session = Depends(get_db),
):
  anggota = db.query(Anggota).filter(Anggota.id == anggota_id, Anggota.deleted_at.is_not(None)).first()

  if not anggota:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Data anggota tidak ditemukan atau tidak berstatus terhapus"
    )

  if anggota.user:
    anggota.user.is_active = 1

    prefix = f"deleted_{anggota.id}.{anggota.user.username}"
    if anggota.user.username.startswith(prefix):
      original_username = anggota.user.username.replace(prefix, "", 1)

      username_exist = db.query(User).filter(
        User.username == original_username,
        User.id != anggota.user.id
      )

      if username_exist:
        raise HTTPException(
          status_code=status.HTTP_400_BAD_REQUEST,
          detail="Gagal memulihkan! Username '{original_username}' sudah digunakan oleh akun lain."
        )

      anggota.user.username = original_username

  anggota.deleted_at = None
  anggota.user.is_active = 1

  db.commit()
  db.refresh(anggota)

  return Response(status_code=status.HTTP_204_NO_CONTENT)