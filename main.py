from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
from services.dream_ai import analyze_dream_with_ai

app = FastAPI()


class DreamRequest(BaseModel):
    dream: str


@app.get("/")
def home():
    return FileResponse("dream.html")


@app.get("/api/status")
def status():
    return {"status": "server working"}


@app.post("/api/analyze-dream")
def analyze_dream(data: DreamRequest):

    dream_text = data.dream

    interpretation = analyze_dream_with_ai(dream_text)

    return {
        "dream": dream_text,
        "interpretation": interpretation
    }
