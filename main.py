from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse

from services.dream_ai import analyze_dream_with_ai
from database import init_db, save_dream, get_all_dreams

app = FastAPI()

# تشغيل قاعدة البيانات
init_db()


class DreamRequest(BaseModel):
    dream: str


# الصفحة الرئيسية
@app.get("/")
def home():
    return FileResponse("templates/dream.html")


# فحص حالة السيرفر
@app.get("/api/status")
def status():
    return {"status": "server working"}


# تحليل حلم
@app.post("/api/analyze-dream")
def analyze_dream(data: DreamRequest):

    dream_text = data.dream

    interpretation = analyze_dream_with_ai(dream_text)

    save_dream(dream_text, interpretation)

    return {
        "dream": dream_text,
        "interpretation": interpretation
    }


# عرض جميع الأحلام
@app.get("/api/dreams")
def list_dreams():

    dreams = get_all_dreams()

    result = []

    for d in dreams:
        result.append({
            "id": d[0],
            "dream": d[1],
            "interpretation": d[2]
        })

    return {"dreams": result}


# صفحة تاريخ الأحلام
@app.get("/history")
def history_page():
    return FileResponse("templates/history.html")
