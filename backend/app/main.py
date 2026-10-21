from fastapi import FastAPI
from config import settings

app = FastAPI()

@app.get("/")
def HelloWorld():
  return {"message": "hello World"}
