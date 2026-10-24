from sqlalchemy import (
  Column, Integer, String, Date, DateTime,
  CheckConstraint, Index, text, func
)
from sqlalchemy.orm import relationship
from datetime import date
from app.database import Base

class Anggota(Base):
  __tablename__ = "anggota"

  id = Column(Integer, primary_key=True)
  nama_lengkap = Column(String, nullable=False)
  nim = Column(String, nullable=False)
  prodi = Column(String)
  email = Column(String)
  no_hp = Column(String)
  status_keanggotaan = Column(String, nullable=False, index=True, default="aktif")
  tanggal_bergabung = Column(Date, nullable=False, default=date.today)
  deleted_at = Column(DateTime, nullable=True)
  created_at = Column(DateTime, nullable=False, server_default=func.now())
  updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

  __table_args__ = (
    CheckConstraint(
      "status_keanggotaan IN ('aktif', 'tidak_aktif')",
      name="ck_anggota_status",
    ),
    Index(
      "ux_anggota_nim_aktif",
      "nim",
      unique=True,
      sqlite_where=text("deleted_at IS NULL")
    )
  )

  user = relationship(
    "User",
    foreign_keys="User.anggota_id",
    back_populates="anggota",
    uselist=False
  )
  asal_pendaftaran = relationship(
    "CalonAnggota",
    foreign_keys="CalonAnggota.anggota_id",
    back_populates="anggota",
    uselist=False
  )
  pembayaran_kas = relationship(
    "PembayaranKas",
    foreign_keys="PembayaranKas.anggota_id",
    back_populates="anggota",
  )