from sqlalchemy import (
  Column, Integer, String, Text, DateTime, ForeignKey,
  CheckConstraint, Index, text, func 
)
from sqlalchemy.orm import relationship
from app.database import Base

class CalonAnggota(Base):
  __tablename__ = "calon_anggota"

  id = Column(Integer, primary_key=True)
  nama_lengkap = Column(String, nullable=False)
  nim = Column(String, nullable=False)
  prodi = Column(String, nullable=False)
  email = Column(String)
  no_hp = Column(String, nullable=False)
  alasan_bergabung = Column(Text)
  status = Column(String, nullable=False, default="pending")
  tanggal_daftar = Column(DateTime, nullable=False, server_default=func.now())
  diproses_oleh = Column(Integer, ForeignKey("users.id"), nullable=True)
  tanggal_diproses = Column(DateTime, nullable=True)
  catatan_penolakan = Column(Text, nullable=True)
  anggota_id = Column(Integer, ForeignKey("anggota.id"), nullable=True, unique=True)

  __table_args__ = (
    CheckConstraint(
      "status IN ('pending', 'diterima', 'ditolak')",
      name="ck_calon_anggota_status",
    ),
    Index(
      "ux_calon_nim_pending",
      "nim",
      unique=True,
      sqlite_where=text("status = 'pending'")
    ),
  )

  pemroses = relationship(
    "User",
    foreign_keys=[diproses_oleh],
    back_populates="calon_diproses",
  )
  anggota = relationship(
    "Anggota", 
    foreign_keys=[anggota_id], 
    back_populates="asal_pendaftaran",
  )