from fastapi import FastAPI

app = FastAPI(tile="WhistelDrop")

@app.get("/")
def home():
    return{"message":"WhistelDrop API is running"}