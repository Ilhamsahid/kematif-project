from fastapi import FastAPI
from app.config import settings
from app.routers import all_router

app = FastAPI()

for r in all_router:
  app.include_router(r)

@app.get("/")
def HelloWorld():
  return {"message": "hello World"}