from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse

from services.dream_ai import analyze_dream_with_ai
from database import (
    init_db,
    create_user,
    save_dream,
    get_user_dreams,
    get_public_dreams,
    like_dream,
    add_comment,
    get_comments,
    search_dreams
    get_user_profile
    get_dream_by_id
)
    init_db,
    create_user,
    save_dream,
    get_user_dreams,
    get_public_dreams,
    like_dream,
    add_comment,
    get_comments
)

import sqlite3

app = FastAPI()

init_db()


class DreamRequest(BaseModel):
    user_id: int
    dream: str
    public: int = 0


class UserRequest(BaseModel):
    username: str
    password: str


class CommentRequest(BaseModel):
    dream_id: int
    username: str
    comment: str


# الصفحة الرئيسية
@app.get("/")
def home():
    return FileResponse("templates/home.html")


# التسجيل
@app.get("/register")
def register_page():
    return FileResponse("templates/register.html")


# تسجيل الدخول
@app.get("/login")
def login_page():
    return FileResponse("templates/login.html")


# لوحة التحكم
@app.get("/dashboard")
def dashboard_page():
    return FileResponse("templates/dashboard.html")


# Dream Feed
@app.get("/dream-feed")
def dream_feed():
    return FileResponse("templates/dream_feed.html")


# Trending
@app.get("/trending")
def trending_page():
    return FileResponse("templates/trending.html")


# Explore
@app.get("/explore")
def explore_page():
    return FileResponse("templates/explore.html")
    
    @app.get("/profile")
def profile_page():
    return FileResponse("templates/profile.html")
    
@app.get("/dream/{dream_id}")
def dream_page(dream_id: int):
    return FileResponse("templates/dream.html")
    
@app.get("/search")
def search_page():
    return FileResponse("templates/search.html")
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

    save_dream(data.user_id, data.dream, interpretation, data.public)

    return {
        "dream": data.dream,
        "interpretation": interpretation
    }


# أحلام المستخدم
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


# الأحلام العامة
@app.get("/api/public-dreams")
def public_dreams():

    dreams = get_public_dreams()

    result = []

    for d in dreams:
        result.append({
            "id": d[0],
            "dream": d[1],
            "interpretation": d[2],
            "likes": d[3]
        })

    return {"dreams": result}


# الإعجاب بالحلم
@app.post("/api/like-dream/{dream_id}")
def like_dream_api(dream_id: int):

    like_dream(dream_id)

    return {"message": "Dream liked"}


# إضافة تعليق
@app.post("/api/add-comment")
def add_comment_api(data: CommentRequest):

    add_comment(data.dream_id, data.username, data.comment)

    return {"message": "Comment added"}


# جلب التعليقات
@app.get("/api/comments/{dream_id}")
def get_comments_api(dream_id: int):

    comments = get_comments(dream_id)

    result = []

    for c in comments:
        result.append({
            "username": c[0],
            "comment": c[1]
        })

    return {"comments": result}
    @app.get("/api/search")
def search(keyword: str):

    dreams = search_dreams(keyword)

    result = []

    for d in dreams:
        result.append({
            "dream": d[0],
            "interpretation": d[1]
        })

    return {"results": result}
    @app.get("/api/profile/{username}")
def profile_api(username: str):

    dreams = get_user_profile(username)

    result = []

    for d in dreams:
        result.append({
            "dream": d[0],
            "interpretation": d[1]
        })

    return {"dreams": result}
    @app.get("/api/dream/{dream_id}")
def get_dream(dream_id: int):

    dream = get_dream_by_id(dream_id)

    if not dream:
        return {"error": "Dream not found"}

    return {
        "dream": dream[0],
        "interpretation": dream[1]
        }
