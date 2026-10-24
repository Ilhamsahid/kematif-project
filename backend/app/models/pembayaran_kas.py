from sqlalchemy import (
  Column, Integer, String, Date, DateTime, ForeignKey,
  CheckConstraint, UniqueConstraint, func
)
from sqlalchemy.orm import relationship
from datetime import date
from app.database import Base

class PembayaranKas(Base):
  __tablename__ = "pembayaran_kas"

  id = Column(Integer, primary_key=True)
  anggota_id = Column(Integer, ForeignKey("anggota.id"), nullable=False)
  tanggal_bayar = Column(Date, nullable=False, default=date.today)
  periode = Column(String(7), nullable=False, index=True)
  nominal = Column(Integer, nullable=False)
  keterangan = Column(String)
  dicatat_oleh = Column(Integer, ForeignKey("users.id"), nullable=False)
  created_at = Column(DateTime, nullable=False, server_default=func.now())

  __table_args__ = (
    CheckConstraint(
      "nominal > 0",
      name="ck_pembayaran_kas_nominal"
    ),
    CheckConstraint(
      "periode GLOB '[0-9][0-9][0-9][0-9]-[0-1][0-9]'",
      name="ck_pembayaran_kas_periode"
    ),
    UniqueConstraint("anggota_id", "periode", name="ux_kas_anggota_periode"),
  )

  anggota = relationship("Anggota", back_populates="pembayaran_kas")
  pencatat = relationship("User", back_populates="pembayaran_dicatat")