from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse

from services.dream_ai import analyze_dream_with_ai
from database import init_db, save_dream, get_all_dreams, create_user
import sqlite3

app = FastAPI()

init_db()


class DreamRequest(BaseModel):
    dream: str


class UserRequest(BaseModel):
    username: str
    password: str


# الصفحة الرئيسية
@app.get("/")
def home():
    return FileResponse("templates/dream.html")


# صفحة التسجيل
@app.get("/register")
def register_page():
    return FileResponse("templates/register.html")


# صفحة تسجيل الدخول
@app.get("/login")
def login_page():
    return FileResponse("templates/login.html")


# فحص السيرفر
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


# عرض الأحلام
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


# صفحة التاريخ
@app.get("/history")
def history_page():
    return FileResponse("templates/history.html")


# تسجيل مستخدم
@app.post("/api/register")
def register(user: UserRequest):

    create_user(user.username, user.password)

    return {
        "message": "User registered successfully"
    }


# تسجيل الدخول
@app.post("/api/login")
def login(user: UserRequest):

    conn = sqlite3.connect("dreams.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (user.username, user.password)
    )

    result = cursor.fetchone()

    conn.close()

    if result:
        return {"message": "Login successful"}
    else:
        return {"message": "Invalid username or password"}
