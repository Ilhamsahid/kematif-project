from sqlalchemy import (
  Column, Integer, String, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from app.database import Base

class KategoriDokumen(Base):
  __tablename__ = "kategori_dokumen"

  id = Column(Integer, primary_key=True)
  nama = Column(String, nullable=False, unique=True)

  dokumen = relationship("Dokumen", back_populates="kategori")

class Dokumen(Base):
  __tablename__ = "dokumen"

  id = Column(Integer, primary_key=True)
  judul = Column(String, nullable=False)
  kategori_id = Column(Integer, ForeignKey("kategori_dokumen.id"), nullable=False, index=True)
  nama_file = Column(String, nullable=False)
  path_file = Column(String, nullable=False)
  diunggah_oleh = Column(Integer, ForeignKey("users.id"), nullable=False)
  deleted_at = Column(DateTime, nullable=True)
  created_at = Column(DateTime, nullable=False, server_default=func.now())
  updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

  kategori = relationship("KategoriDokumen", back_populates="dokumen")
  pengunggah = relationship("User", back_populates="dokumen_diunggah")