from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import requests
import os

app = FastAPI()

# تشغيل مجلد static للصور والملفات
app.mount("/static", StaticFiles(directory="static"), name="static")

# مفتاح Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


# الصفحة الرئيسية
@app.get("/")
def home():
    return FileResponse("templates/index.html")


# صفحة المدونة
@app.get("/blog")
def blog():
    return FileResponse("templates/blog/index.html")


# المقالات
@app.get("/blog/ancient-egypt-dreams")
def egypt():
    return FileResponse("templates/blog/ancient-egypt-dreams.html")


@app.get("/blog/babylonian-dreams")
def babylon():
    return FileResponse("templates/blog/babylonian-dreams.html")


@app.get("/blog/greek-dream-interpretation")
def greek():
    return FileResponse("templates/blog/greek-dream-interpretation.html")


@app.get("/blog/islamic-dream-interpretation")
def islamic():
    return FileResponse("templates/blog/islamic-dream-interpretation.html")


@app.get("/blog/snake-dream-meaning")
def snake():
    return FileResponse("templates/blog/snake-dream-meaning.html")


@app.get("/blog/flying-dream-meaning")
def flying():
    return FileResponse("templates/blog/flying-dream-meaning.html")


# صفحة تحليل الأحلام
@app.get("/analyze-dream")
def analyze_page():
    return FileResponse("templates/analyze.html")


# API تحليل الحلم
@app.post("/analyze")
async def analyze(request: Request):

    data = await request.json()
    dream = data["dream"]

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

    prompt = f"""
You are a professional dream interpreter.

Interpret this dream clearly:

Dream:
{dream}

Give:
- General meaning
- Symbol explanation
- Advice
"""

    response = requests.post(url, json={
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    })

    result = response.json()

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
    except:
        text = "Error analyzing dream"

    return {"result": text}
