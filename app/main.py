from fastapi import FastAPI
from app.database import engine

app = FastAPI(title="WhistleDrop")

@app.get("/")
def home():
    return {"message": "WhistleDrop API is running"}