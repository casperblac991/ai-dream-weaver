from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "AI Dream Weaver platform running"}

@app.get("/api/status")
def status():
    return {"status": "server working"}
