from fastapi import FastAPI
from app.config import settings

app = FastAPI()

@app.get("/")
def HelloWorld():
  return {"message": "hello World"}
