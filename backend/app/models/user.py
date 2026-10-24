from sqlalchemy import (
  Column, Integer, String, DateTime,
  CheckConstraint, func, ForeignKey
)
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key=True)
  anggota_id = Column(Integer, ForeignKey("anggota.id"), unique=True, nullable=False)
  username = Column(String, nullable=False)
  password_hash = Column(String, nullable=False)
  role = Column(String, nullable=False, default="anggota")
  is_active = Column(Integer, nullable=False, default=1)
  last_login_at = Column(DateTime)
  created_at = Column(DateTime, nullable=False, server_default=func.now())
  updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

  __table_args__ = (
    CheckConstraint(
      "role IN ('pengurus', 'bendahara', 'anggota')",
      name="ck_user_role",
    ),
    CheckConstraint(
      "is_active IN (0, 1)",
      name="ck_user_is_active"
    )
  )

  anggota = relationship(
    "Anggota",
    foreign_keys=[anggota_id],
    back_populates="user",
  )
  calon_diproses = relationship(
    "CalonAnggota",
    foreign_keys="CalonAnggota.diproses_oleh",
    back_populates="pemroses", 
  )
  pembayaran_dicatat = relationship(
    "PembayaranKas",
    foreign_keys="PembayaranKas.dicatat_oleh",
    back_populates="pencatat"
  )
  dokumen_diunggah = relationship(
    "Dokumen",
    foreign_keys="Dokumen.diunggah_oleh",
    back_populates="pengunggah"
  )