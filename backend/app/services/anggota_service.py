from sqlalchemy.orm import Session
from app.models import Anggota, User
from app.schemas.anggota import AnggotaCreate
from app.security import get_password_hash, get_random_pwd

def create_anggota_and_account(
  db: Session,
  anggota: AnggotaCreate,
):
  anggota_created = Anggota(
    nama_lengkap = anggota.nama_lengkap,
    nim = anggota.nim,
    prodi = anggota.prodi,
    email = anggota.email,
    no_hp = anggota.no_hp,
  )

  db.add(anggota_created)
  db.flush()

  raw_password = get_random_pwd()
  hashed_password = get_password_hash(raw_password)

  user_created = User(
    anggota_id = anggota_created.id,
    username = anggota.nim,
    password_hash = hashed_password,
  )

  db.add(user_created)

  return {
    "anggota": anggota_created,
    "raw_password": raw_password
  }