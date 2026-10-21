from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def HelloWorld():
  return {"message": "hello World"}
