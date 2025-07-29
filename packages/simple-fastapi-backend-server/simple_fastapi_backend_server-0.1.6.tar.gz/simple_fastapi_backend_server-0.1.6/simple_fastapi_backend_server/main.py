import sys
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is running"}

@app.post("/register")
def register(user: dict):
    return {"message": "User registered", "user": user}

@app.post("/login")
def login(user: dict):
    return {"message": "User logged in", "user": user}

def start():
    if "--help" in sys.argv:
        print("Usage: simple-fastapi-backend-server")
        sys.exit(0)  # 🔥 This line is critical

    uvicorn.run("simple_fastapi_backend_server.main:app", host="0.0.0.0", port=8000)
