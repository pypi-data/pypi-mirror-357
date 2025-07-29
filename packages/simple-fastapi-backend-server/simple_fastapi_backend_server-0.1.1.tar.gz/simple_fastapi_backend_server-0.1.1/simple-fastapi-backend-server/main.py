from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API is running"}

@app.post("/register")
def register_user(user: dict):
    return {"message": "User registered successfully", "user": user}

@app.post("/login")
def login_user(user: dict):
    return {"message": "User logged in successfully", "user": user}

def start():
    uvicorn.run("fastapi_wrapper.main:app", host="0.0.0.0", port=8000, reload=False)
