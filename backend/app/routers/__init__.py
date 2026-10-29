from app.routers import auth, anggota

all_router = [
  auth.router,
  anggota.router,
]