from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse

from services.dream_ai import analyze_dream_with_ai
from database import init_db, create_user, save_dream, get_user_dreams

import sqlite3

app = FastAPI()

init_db()


class DreamRequest(BaseModel):
    user_id: int
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


# تسجيل مستخدم
@app.post("/api/register")
def register(user: UserRequest):

    create_user(user.username, user.password)

    return {"message": "User registered successfully"}


# تسجيل الدخول
@app.post("/api/login")
def login(user: UserRequest):

    conn = sqlite3.connect("dreams.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE username=? AND password=?",
        (user.username, user.password)
    )

    result = cursor.fetchone()

    conn.close()

    if result:
        return {
            "message": "Login successful",
            "user_id": result[0]
        }
    else:
        return {"message": "Invalid username or password"}


# تحليل حلم
@app.post("/api/analyze-dream")
def analyze_dream(data: DreamRequest):

    interpretation = analyze_dream_with_ai(data.dream)

    save_dream(data.user_id, data.dream, interpretation)

    return {
        "dream": data.dream,
        "interpretation": interpretation
    }


# عرض أحلام المستخدم
@app.get("/api/dreams/{user_id}")
def user_dreams(user_id: int):

    dreams = get_user_dreams(user_id)

    result = []

    for d in dreams:
        result.append({
            "dream": d[0],
            "interpretation": d[1]
        })

    return {"dreams": result}
