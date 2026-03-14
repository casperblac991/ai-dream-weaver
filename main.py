from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "AI Dream Weaver platform running"}

@app.get("/api/status")
def status():
    return {"status": "server working"}

from pydantic import BaseModel
import os
import requests

class DreamRequest(BaseModel):
    dream: str


@app.post("/api/analyze-dream")
def analyze_dream(data: DreamRequest):

    dream_text = data.dream

    api_key = os.getenv("GEMINI_API_KEY")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"

    prompt = f"""
    Interpret this dream in a psychological and symbolic way:

    Dream:
    {dream_text}

    Provide meaning and possible emotional interpretation.
    """

    payload = {
        "contents":[
            {
                "parts":[
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(url, json=payload)

    result = response.json()

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
    except:
        text = "Dream interpretation unavailable."

    return {
        "dream": dream_text,
        "interpretation": text
    }
