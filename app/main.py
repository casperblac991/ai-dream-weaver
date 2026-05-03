#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weaver (نَسَّاج) - منصة تفسير الأحلام بالذكاء الاصطناعي
النسخة المحدثة - تدعم التحديث اليومي للمدونة من مجلد blog/
"""

from fastapi import FastAPI, Request, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import secrets
from datetime import datetime
from pathlib import Path
import glob
import sqlite3

# ========== التعديل الأساسي: استيراد جميع الدوال من database.py بدلاً من models.py ==========
from app.database import init_db
from app.auth import register_user, login_user
from app.database import (
    get_user_by_id, save_dream, get_user_dreams,
    get_dreams_used, increment_dreams_used,
    get_all_users, save_email_subscriber, get_all_subscribers,
    get_platform_stats, save_blog_post, get_blog_posts
)
from app.ai import interpret_dream, generate_image_prompt, generate_blog_article

# تهيئة قاعدة البيانات (ستنشئ جميع الجداول المطلوبة)
init_db()

# إنشاء تطبيق FastAPI
app = FastAPI(
    title="Weaver | نَسَّاج",
    description="منصة تفسير الأحلام بالذكاء الاصطناعي",
    version="3.1.0"
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
templates = Jinja2Templates(directory="templates")
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

# ========== دالة لقراءة المقالات من مجلد blog/ (للتحديث اليومي) ==========
def get_blog_posts_from_folder(limit=50):
    """تجلب المقالات من ملفات HTML الموجودة في مجلد blog/"""
    blog_dir = Path("blog")
    posts = []
    if blog_dir.exists():
        html_files = glob.glob(str(blog_dir / "*.html"))
        for file_path in sorted(html_files, key=lambda x: os.path.getmtime(x), reverse=True):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                import re
                title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                if title_match:
                    title = title_match.group(1)
                else:
                    name = Path(file_path).stem
                    title = name.replace('-', ' ').replace('_', ' ')
                
                name_stem = Path(file_path).stem
                parts = name_stem.split('-')
                if len(parts) >= 3 and parts[0].isdigit() and parts[1].isdigit() and parts[2].isdigit():
                    date_str = f"{parts[0]}-{parts[1]}-{parts[2]}"
                else:
                    date_str = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d")
                
                text = re.sub(r'<[^>]+>', '', content)
                excerpt = text[:150] + "..." if len(text) > 150 else text
                
                posts.append({
                    "title": title,
                    "slug": Path(file_path).stem,
                    "date": date_str,
                    "excerpt": excerpt,
                    "category": "تفسير أحلام",
                    "author": "Weaver AI"
                })
            except Exception as e:
                print(f"خطأ في قراءة {file_path}: {e}")
    return posts[:limit]

def get_all_blog_posts(limit=50):
    """تجلب المقالات من قاعدة البيانات (الأساسية) ومن مجلد blog/ (التوليد اليومي)"""
    db_posts = get_blog_posts(limit=100)
    folder_posts = get_blog_posts_from_folder(limit=100)
    all_posts = {p["slug"]: p for p in db_posts}
    for p in folder_posts:
        if p["slug"] not in all_posts:
            all_posts[p["slug"]] = p
    posts_list = list(all_posts.values())
    posts_list.sort(key=lambda x: x.get("date", "2000-01-01"), reverse=True)
    return posts_list[:limit]

# ========== الصفحات الأساسية ==========
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

# ========== JSON API Endpoints ==========

@app.post("/api/login")
async def api_login(request: Request):
    """تسجيل الدخول via JSON"""
    try:
        body = await request.json()
        email = body.get("email", "").strip()
        password = body.get("password", "")
        
        if not email or not password:
            return JSONResponse({"error": "البريد الإلكتروني وكلمة المرور مطلوبان"}, status_code=400)
        
        user = login_user(email, password)
        if user:
            token = create_session(user["id"])
            return JSONResponse({
                "success": True,
                "user_id": user["id"],
                "username": user["username"],
                "token": token
            })
        return JSONResponse({"error": "البريد الإلكتروني أو كلمة المرور غير صحيحة"}, status_code=401)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/register")
async def api_register(request: Request):
    """التسجيل via JSON"""
    try:
        body = await request.json()
        username = body.get("username", "").strip()
        email = body.get("email", "").strip()
        password = body.get("password", "")
        
        result = register_user(username, email, password)
        if result.get("success"):
            token = create_session(result["user_id"])
            return JSONResponse({
                "success": True,
                "user_id": result["user_id"],
                "username": username,
                "token": token
            })
        return JSONResponse({"error": result.get("message", "خطأ في التسجيل")}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

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

# المدونة (تدعم التحديث اليومي)
@app.get("/blog", response_class=HTMLResponse)
async def blog_page(request: Request):
    user = get_current_user(request)
    posts = get_all_blog_posts(limit=30)
    return templates.TemplateResponse(request, "blog.html", {
        "user": user, "posts": posts
    })

@app.get("/blog/{slug}", response_class=HTMLResponse)
async def blog_post_page(request: Request, slug: str):
    user = get_current_user(request)
    # حاول أولاً من مجلد blog/
    file_path = Path(f"blog/{slug}.html")
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content)
    # ثم من قاعدة البيانات
    posts = get_all_blog_posts(limit=200)
    post = next((p for p in posts if p.get("slug") == slug), None)
    if post:
        return templates.TemplateResponse(request, "blog_post.html", {
            "user": user, "post": post
        })
    raise HTTPException(status_code=404, detail="المقال غير موجود")

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
    posts = get_all_blog_posts(limit=50)
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

# ========== الأجزاء الاختيارية (معلقة) ==========
# from app.subscriptions import get_user_subscription, upgrade_subscription, create_subscription_tables, get_revenue_stats
# from app.payment import PaymentProcessor, get_payment_analytics
# from app.seo_generator import get_seo_page, get_seo_stats, generate_all_seo_pages
# from app.viral_sharing import ViralShareGenerator, ReferralSystem, ViralMetrics
# create_subscription_tables()
#
# @app.get("/dream/{slug}")
# async def dream_symbol_page(...): ...
# @app.get("/app/upgrade") ...
# @app.post("/api/checkout") ...
# @app.get("/share/{symbol}") ...
# @app.get("/api/referral/{user_id}") ...
# @app.get("/api/revenue-stats") ...
# @app.post("/admin/generate-seo") ...

# ========== نقطة الصحة (لـ Render) ==========
@app.get("/health")
def health_check():
    return {"status": "ok"}

# ========== نظام حماية المسارات ==========

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Middleware لفرض تسجيل الدخول على المسارات المحمية"""
    
    # المسارات العامة التي لا تتطلب تسجيل دخول
    public_routes = [
        "/",
        "/app/login",
        "/app/register",
        "/api/login",
        "/api/register",
        "/api/subscribe",
        "/blog",
        "/static/",
        "/docs",
        "/openapi.json"
    ]
    
    # التحقق من ما إذا كان المسار عام
    is_public = False
    for route in public_routes:
        if route.endswith("/"):
            if request.url.path.startswith(route):
                is_public = True
                break
        else:
            if request.url.path == route:
                is_public = True
                break
    
    # إذا كان المسار عام، السماح بالوصول
    if is_public:
        response = await call_next(request)
        return response
    
    # إذا كان المسار خاص، التحقق من تسجيل الدخول
    user = get_current_user(request)
    if not user:
        # إعادة التوجيه لصفحة تسجيل الدخول
        return RedirectResponse(url="/app/login", status_code=302)
    
    response = await call_next(request)
    return response

# ========== بوت تيليجرام عبر Webhook (بسيط 100%) ==========
@app.post("/webhook")
async def telegram_webhook(request: Request):
    """استقبال التحديثات من تيليجرام"""
    import os
    import requests
    
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
    
    if not TELEGRAM_TOKEN:
        return JSONResponse({"error": "No token"}, status_code=500)
    
    try:
        body = await request.json()
        message = body.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")
        
        if not chat_id or not text:
            return JSONResponse({"ok": True})
        
        # معالجة الأوامر
        if text == "/start":
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": "🌙 *مرحباً بك في نَسَّاج*\n\n🔮 /dream <حلمك>\n📊 /stats\n❓ /help", "parse_mode": "Markdown"},
                timeout=10
            )
        elif text == "/help":
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": "🔮 /dream <نص> - فسّر\n/stats - إحصائيات", "parse_mode": "Markdown"},
                timeout=10
            )
        elif text == "/stats":
            try:
                r = requests.get("https://aidreamweaver.store/api/stats", timeout=10)
                if r.ok:
                    s = r.json()
                    requests.post(
                        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                        json={"chat_id": chat_id, "text": f"📊 {s.get('users',0)} مستخدم\n🌙 {s.get('dreams',0)} حلم"},
                        timeout=10
                    )
            except:
                pass
        elif text.lower().startswith('/dream '):
            dream = text[7:]
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": "🔮 جاري التفسير..."},
                timeout=10
            )
            try:
                r = requests.post("https://aidreamweaver.store/api/interpret",
                    json={"dream": dream, "style": "islamic", "language": "ar"},
                    timeout=60
                )
                if r.ok:
                    interp = r.json().get("interpretation", "")[:4000]
                    if interp:
                        requests.post(
                            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                            json={"chat_id": chat_id, "text": interp, "parse_mode": "Markdown"},
                            timeout=10
                        )
            except:
                pass
        elif text and not text.startswith('/'):
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": "🔮 جاري التفسير..."},
                timeout=10
            )
            try:
                r = requests.post("https://aidreamweaver.store/api/interpret",
                    json={"dream": text, "style": "islamic", "language": "ar"},
                    timeout=60
                )
                if r.ok:
                    interp = r.json().get("interpretation", "")[:4000]
                    if interp:
                        requests.post(
                            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                            json={"chat_id": chat_id, "text": interp, "parse_mode": "Markdown"},
                            timeout=10
                        )
            except:
                pass
        
        return JSONResponse({"ok": True})
    except Exception as e:
        print(f"Webhook error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

# ========== إعداد Webhook ==========
@app.get("/setwebhook")
async def set_webhook(request: Request):
    """ضبط Webhook"""
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
    if not TELEGRAM_TOKEN:
        return JSONResponse({"error": "No token"}, status_code=400)
    
    webhook_url = f"https://{request.url.hostname}/webhook"
    import requests
    r = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook",
        json={"url": webhook_url}
    )
    return JSONResponse(r.json())

@app.get("/getwebhookinfo")
async def get_webhook_info():
    """معلومات Webhook"""
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
    if not TELEGRAM_TOKEN:
        return JSONResponse({"error": "No token"}, status_code=400)
    
    import requests
    r = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getWebhookInfo")
    return JSONResponse(r.json())

