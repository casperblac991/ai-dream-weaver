#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weaver (نَسَّاج) - منصة تفسير الأحلام بالذكاء الاصطناعي
النسخة الكاملة المحدّثة v3.0
"""

from fastapi import FastAPI, Request, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import secrets
from datetime import datetime

from app.database import init_db
from app.auth import register_user, login_user
from app.models import (
    get_user_by_id, save_dream, get_user_dreams,
    get_dreams_used, increment_dreams_used,
    get_all_users, save_email_subscriber, get_all_subscribers,
    get_platform_stats, save_blog_post, get_blog_posts
)
from app.ai import interpret_dream, generate_image_prompt, generate_blog_article

# تهيئة قاعدة البيانات
init_db()

# إنشاء تطبيق FastAPI
app = FastAPI(
    title="Weaver | نَسَّاج",
    description="منصة تفسير الأحلام بالذكاء الاصطناعي",
    version="3.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# القوالب
templates = Jinja2Templates(directory="app/templates")

# إدارة الجلسات
sessions: dict = {}

def get_current_user(request: Request):
    session_token = request.cookies.get("session_token")
    if session_token and session_token in sessions:
        user_id = sessions[session_token]
        return get_user_by_id(user_id)
    return None

def create_session(user_id: int) -> str:
    token = secrets.token_hex(32)
    sessions[token] = user_id
    return token

# الصفحة الرئيسية
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    user = get_current_user(request)
    stats = get_platform_stats()
    return templates.TemplateResponse(request, "index.html", {
        "user": user, "stats": stats
    })

@app.get("/app", response_class=HTMLResponse)
async def app_home(request: Request):
    user = get_current_user(request)
    stats = get_platform_stats()
    return templates.TemplateResponse(request, "index.html", {
        "user": user, "stats": stats
    })

# التسجيل
@app.get("/app/register", response_class=HTMLResponse)
async def register_page(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse("/app/dashboard")
    return templates.TemplateResponse(request, "register.html")

@app.post("/app/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    result = register_user(username, email, password)
    if result.get("success"):
        token = create_session(result["user_id"])
        response = RedirectResponse("/app/dashboard", status_code=302)
        response.set_cookie("session_token", token, max_age=86400 * 30, httponly=True)
        return response
    return templates.TemplateResponse(request, "register.html", {
        "error": result.get("message", "خطأ في التسجيل")
    })

# تسجيل الدخول
@app.get("/app/login", response_class=HTMLResponse)
async def login_page(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse("/app/dashboard")
    return templates.TemplateResponse(request, "login.html")

@app.post("/app/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    user = login_user(email, password)
    if user:
        token = create_session(user["id"])
        response = RedirectResponse("/app/dashboard", status_code=302)
        response.set_cookie("session_token", token, max_age=86400 * 30, httponly=True)
        return response
    return templates.TemplateResponse(request, "login.html", {
        "error": "خطأ في البريد الإلكتروني أو كلمة المرور"
    })

# تسجيل الخروج
@app.get("/app/logout")
async def logout(request: Request):
    session_token = request.cookies.get("session_token")
    if session_token and session_token in sessions:
        del sessions[session_token]
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("session_token")
    return response

# لوحة التحكم
@app.get("/app/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/app/login")
    dreams = get_user_dreams(user["id"])
    stats = get_platform_stats()
    return templates.TemplateResponse(request, "dashboard.html", {
        "user": user, "dreams": dreams, "stats": stats
    })

# تفسير الأحلام
@app.get("/app/analyze", response_class=HTMLResponse)
async def analyze_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/app/login")
    return templates.TemplateResponse(request, "analyze.html", {"user": user})

@app.post("/app/analyze")
async def analyze(
    request: Request,
    dream: str = Form(...),
    language: str = Form(default="ar"),
    style: str = Form(default="islamic")
):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/app/login")

    used = get_dreams_used(user["id"])
    limits = {"free": 5, "basic": 10, "pro": 999, "team": 999}
    limit = limits.get(user.get("plan", "free"), 5)

    if used >= limit:
        return templates.TemplateResponse(request, "analyze.html", {
            "user": user,
            "error": "لقد استنفدت حد التفسيرات اليومي. يرجى الترقية للاستمرار.",
            "upgrade": True
        })

    interpretation = interpret_dream(dream, style=style, language=language)
    image_prompt = generate_image_prompt(dream)
    save_dream(user["id"], dream, interpretation, image_prompt)
    increment_dreams_used(user["id"])

    return templates.TemplateResponse(request, "analyze.html", {
        "user": user,
        "dream": dream, "interpretation": interpretation,
        "image_prompt": image_prompt
    })

# API: تفسير سريع
@app.post("/api/interpret")
async def api_interpret(request: Request):
    try:
        body = await request.json()
        dream_text = body.get("dream", "")
        style = body.get("style", "islamic")
        language = body.get("language", "ar")
        if not dream_text:
            return JSONResponse({"error": "dream text required"}, status_code=400)
        result = interpret_dream(dream_text, style=style, language=language)
        return JSONResponse({"interpretation": result, "status": "success"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# الاشتراك في النشرة البريدية
@app.post("/api/subscribe")
async def subscribe_email(request: Request):
    try:
        body = await request.json()
        email = body.get("email", "").strip()
        name = body.get("name", "").strip()
        if not email or "@" not in email:
            return JSONResponse({"error": "بريد إلكتروني غير صالح"}, status_code=400)
        save_email_subscriber(email, name)
        return JSONResponse({"message": "تم الاشتراك بنجاح! ستصلك أحلى المقالات.", "status": "success"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# المدونة
@app.get("/blog", response_class=HTMLResponse)
async def blog_page(request: Request):
    user = get_current_user(request)
    posts = get_blog_posts(limit=20)
    return templates.TemplateResponse(request, "blog.html", {
        "user": user, "posts": posts
    })

@app.get("/blog/{slug}", response_class=HTMLResponse)
async def blog_post_page(request: Request, slug: str):
    user = get_current_user(request)
    posts = get_blog_posts(limit=200)
    post = next((p for p in posts if p.get("slug") == slug), None)
    if not post:
        raise HTTPException(status_code=404, detail="المقال غير موجود")
    return templates.TemplateResponse(request, "blog_post.html", {
        "user": user, "post": post
    })

# إحصائيات المنصة
@app.get("/api/stats")
async def get_stats():
    stats = get_platform_stats()
    return JSONResponse(stats)

# لوحة الإدارة
@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    user = get_current_user(request)
    if not user or user.get("role") != "admin":
        return RedirectResponse("/app/login")
    users = get_all_users()
    subscribers = get_all_subscribers()
    stats = get_platform_stats()
    posts = get_blog_posts(limit=50)
    return templates.TemplateResponse(request, "admin.html", {
        "user": user,
        "users": users, "subscribers": subscribers,
        "stats": stats, "posts": posts
    })

# توليد مقال يدوي
@app.post("/admin/generate-blog")
async def admin_generate_blog(request: Request, background_tasks: BackgroundTasks):
    user = get_current_user(request)
    if not user or user.get("role") != "admin":
        return JSONResponse({"error": "غير مصرح"}, status_code=403)
    background_tasks.add_task(generate_and_save_blog)
    return JSONResponse({"message": "جاري توليد المقال في الخلفية..."})

async def generate_and_save_blog():
    import random
    topics = [
        "تفسير حلم الطيران في الإسلام والحضارات القديمة",
        "الثعبان في المنام - دلالاته عبر الثقافات",
        "البحر والماء في الأحلام - رمزية عميقة",
        "رؤية الميت في المنام - ماذا تعني؟",
        "أحلام الحمل والولادة - تفسيرات متعددة",
        "الأسنان في المنام - من ابن سيرين إلى فرويد"
    ]
    topic = random.choice(topics)
    content = generate_blog_article(topic)
    slug = topic.replace(" ", "-").replace("،", "").replace("؟", "")[:50]
    save_blog_post(
        title=topic, content=content, slug=slug,
        category="تفسير الأحلام", author="نَسَّاج AI"
    )

# تشغيل السيرفر
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
