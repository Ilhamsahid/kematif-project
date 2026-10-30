from app.routers import auth, anggota, calon_anggota

all_router = [
  auth.router,
  anggota.router,
  calon_anggota.router
]