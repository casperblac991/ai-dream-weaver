#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weaver (نَسَّاج) - منصة تفسير الأحلام بالذكاء الاصطناعي
النسخة المحدثة - تدعم التحديث اليومي للمدونة من مجلد blog/
"""

import subprocess
import sys

# آلية تثبيت تلقائي للمكتبات المفقودة (لحل مشكلة Render)
def _install_deps():
    try:
        import passlib
    except ImportError:
        print("Installing missing dependency: passlib")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "passlib[bcrypt]"])

_install_deps()

from fastapi import FastAPI, Request, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import secrets
import base64
import hashlib
import hmac
import time
from urllib.parse import quote
from xml.sax.saxutils import escape as escape_xml
from datetime import datetime
from pathlib import Path
import glob
import sqlite3

# تحديد مسار التطبيق (دعم Render و local)
APP_ROOT = Path(__file__).parent.parent.resolve()

# ========== التعديل الأساسي: استيراد جميع الدوال من database.py بدلاً من models.py ==========
from app.database import init_db
from app.auth import register_user, login_user
from app.database import (
    get_user_by_id, save_dream, get_user_dreams,
    get_dreams_used, increment_dreams_used,
    get_all_users, save_email_subscriber, get_all_subscribers,
    get_platform_stats, save_blog_post, get_all_blog_posts as get_db_blog_posts,
    get_public_dreams, like_dream, add_comment, get_dream_comments
)
from app.translations import get_text
from app.ai import interpret_dream, interpret_dream_local, generate_image_prompt, generate_blog_article, check_ollama_status, generate_customer_reply
from app.shop import router as shop_router

# تهيئة قاعدة البيانات (ستنشئ جميع الجداول المطلوبة)
init_db()

# إنشاء تطبيق FastAPI
app = FastAPI(
    title="Weaver | نَسَّاج",
    description="منصة تفسير الأحلام بالذكاء الاصطناعي",
    version="3.1.0"
)

# إضافة روتر المتجر
app.include_router(shop_router)

# CORS - إصلاح: allow_credentials مع origins محددة
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-dream-weaver.onrender.com",
        "https://aidreamweaver.store",
        "https://www.aidreamweaver.store",
        "http://aidreamweaver.store",
        "http://localhost:10000",
        "http://127.0.0.1:10000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
)

# القوالب - استخدام المسارات المطلقة لضمان عمل جميع الصفحات
templates = Jinja2Templates(directory=str(APP_ROOT / "templates"))

# Static files - إصلاح: دعم الملفات الثابتة
if (APP_ROOT / "css").exists():
    app.mount("/css", StaticFiles(directory=str(APP_ROOT / "css")), name="css")
if (APP_ROOT / "js").exists():
    app.mount("/js", StaticFiles(directory=str(APP_ROOT / "js")), name="js")
if (APP_ROOT / "images").exists():
    app.mount("/images", StaticFiles(directory=str(APP_ROOT / "images")), name="images")
if (APP_ROOT / "reports").exists():
    app.mount("/reports-assets", StaticFiles(directory=str(APP_ROOT / "reports")), name="reports-assets")
if (APP_ROOT / "articles").exists():
    app.mount("/articles", StaticFiles(directory=str(APP_ROOT / "articles")), name="articles")

# إدارة الجلسات
sessions: dict = {}
SESSION_SECRET = os.getenv("SESSION_SECRET", "change-this-session-secret-in-production").encode("utf-8")
SESSION_MAX_AGE = 86400 * 30

def get_current_user(request: Request):
    """Resolve the authenticated user from the cookie or the static frontend bearer token."""
    session_token = request.cookies.get("session_token", "")
    if not session_token:
        authorization = request.headers.get("authorization", "")
        if authorization.lower().startswith("bearer "):
            session_token = authorization[7:].strip()

    if not session_token:
        return None
    if session_token in sessions:
        return get_user_by_id(sessions[session_token])
    try:
        encoded_payload, signature = session_token.split(".", 1)
        encoded_payload += "=" * (-len(encoded_payload) % 4)
        payload = base64.urlsafe_b64decode(encoded_payload.encode("ascii"))
        expected = hmac.new(SESSION_SECRET, payload, hashlib.sha256).hexdigest()
        if hmac.compare_digest(signature, expected):
            user_id_text, created_text = payload.decode("utf-8").split(":", 1)
            if time.time() - int(created_text) <= SESSION_MAX_AGE:
                return get_user_by_id(int(user_id_text))
    except (ValueError, TypeError, OSError, UnicodeError):
        pass
    return None

def render_template(request: Request, template_name: str, context: dict = None):
    if context is None:
        context = {}
    lang = request.cookies.get("lang", "ar")
    user = get_current_user(request)
    
    # الأساسيات المطلوبة لكل قالب
    base_context = {
        "request": request,
        "user": user,
        "lang": lang,
        "t": lambda key: get_text(key, lang),
        "now": datetime.now()
    }
    
    # دمج السياق الإضافي
    base_context.update(context)
    return templates.TemplateResponse(request, template_name, base_context)

def create_session(user_id: int) -> str:
    payload = f"{user_id}:{int(time.time())}".encode("utf-8")
    encoded = base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")
    signature = hmac.new(SESSION_SECRET, payload, hashlib.sha256).hexdigest()
    token = f"{encoded}.{signature}"
    sessions[token] = user_id
    return token

def set_session_cookie(response, token: str):
    response.set_cookie(
        key="session_token", value=token, max_age=SESSION_MAX_AGE,
        httponly=True, samesite="lax",
        secure=os.getenv("COOKIE_SECURE", "false").lower() == "true"
    )
    return response

# ========== فهرسة المحتوى (المدونة + أرشيف المقالات) ==========
def get_blog_posts_from_folder(limit=1000):
    """تجلب المقالات من blog/ وarticles/ مع الاحتفاظ بالملفات القديمة."""
    import re
    posts = []
    for folder_name in ("blog", "articles"):
        folder = APP_ROOT / folder_name
        if not folder.exists():
            continue
        html_files = glob.glob(str(folder / "*.html"))
        for file_path in sorted(html_files, key=lambda x: os.path.getmtime(x), reverse=True):
            try:
                content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
                title_match = re.search(r"<title[^>]*>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
                title = title_match.group(1).strip() if title_match else Path(file_path).stem.replace("-", " ").replace("_", " ")
                title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", title))
                name_stem = Path(file_path).stem
                date_match = re.match(r"(20\d{2}-?\d{2}-?\d{2})", name_stem)
                if date_match:
                    raw_date = date_match.group(1).replace("-", "")
                    date_str = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
                else:
                    date_str = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d")
                text = re.sub(r"<[^>]+>", " ", content)
                text = re.sub(r"\s+", " ", text).strip()
                posts.append({
                    "title": title,
                    "slug": Path(file_path).stem,
                    "date": date_str,
                    "excerpt": text[:180] + "..." if len(text) > 180 else text,
                    "category": "أرشيف المدونة" if folder_name == "blog" else "التقارير والمقالات القديمة",
                    "author": "Weaver AI",
                    "source_folder": folder_name
                })
            except Exception as exc:
                print(f"خطأ في قراءة {file_path}: {exc}")
    posts.sort(key=lambda item: item.get("date", "2000-01-01"), reverse=True)
    return posts[:limit]

def get_all_blog_posts(limit=50):
    """تجمع سجلات قاعدة البيانات مع أرشيف blog/ وarticles/ دون فقد المحتوى القديم."""
    db_posts = get_db_blog_posts(limit=1000)
    folder_posts = get_blog_posts_from_folder(limit=1000)
    all_posts = {p["slug"]: p for p in db_posts}
    for p in folder_posts:
        if p["slug"] not in all_posts:
            all_posts[p["slug"]] = p
    posts_list = list(all_posts.values())
    posts_list.sort(key=lambda x: x.get("date", x.get("created_at", "2000-01-01")), reverse=True)
    return posts_list[:limit]

# ========== الصفحات الأساسية ==========
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    stats = get_platform_stats()
    return render_template(request, "index.html", {"stats": stats})

@app.get("/set-lang/{lang}")
async def set_lang(lang: str):
    response = RedirectResponse(url="/")
    response.set_cookie(key="lang", value=lang, max_age=31536000)
    return response

# Static HTML pages (served from root directory)
@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    return render_template(request, "about.html")

@app.get("/faq", response_class=HTMLResponse)
async def faq_page(request: Request):
    return render_template(request, "faq.html")

# دعم الروابط المرنة (بامتداد .html وبدونه)
@app.get("/app/personality-test", response_class=HTMLResponse)
async def personality_test_page(request: Request):
    return render_template(request, "personality-test.html")

@app.get("/app/lucid-dreaming", response_class=HTMLResponse)
async def lucid_dreaming_page(request: Request):
    return render_template(request, "lucid-dreaming.html")

@app.get("/app/offers", response_class=HTMLResponse)
async def offers_page(request: Request):
    return render_template(request, "offers.html")

@app.get("/app/global-map", response_class=HTMLResponse)
async def global_map_page(request: Request):
    return render_template(request, "global-map.html")

@app.get("/app/community", response_class=HTMLResponse)
async def community_page(request: Request):
    public_dreams = get_public_dreams(limit=20)
    return render_template(request, "community.html", {"dreams": public_dreams})

@app.post("/app/api/like-dream/{dream_id}")
async def api_like_dream(dream_id: int):
    like_dream(dream_id)
    return {"success": True}

@app.post("/app/api/comment")
async def api_add_comment(request: Request):
    user = get_current_user(request)
    if not user:
        return JSONResponse({"success": False, "message": "يجب تسجيل الدخول للتعليق"}, status_code=401)
    
    body = await request.json()
    dream_id = body.get("dream_id")
    text = body.get("text")
    
    add_comment(user["id"], dream_id, text)
    return {"success": True}

@app.get("/app/lucid-lab", response_class=HTMLResponse)
async def lucid_lab_page(request: Request):
    return render_template(request, "lucid-lab.html")

@app.get("/app/cosmic-dictionary", response_class=HTMLResponse)
async def cosmic_dictionary_page(request: Request):
    return render_template(request, "cosmic-dictionary.html")

@app.post("/api/generate-video")
async def api_generate_video(request: Request):
    body = await request.json()
    dream = body.get("dream", "")
    lang = body.get("language", "ar")
    from app.ai import generate_dream_video
    video_data = generate_dream_video(dream, lang)
    return video_data

# Placeholder pages for /store and /library
@app.get("/shop", response_class=HTMLResponse)
async def shop_page(request: Request):
    return render_template(request, "shop.html")

@app.get("/dream-interpreter", response_class=HTMLResponse)
async def dream_interpreter_page(request: Request):
    return render_template(request, "dream-interpreter.html")

@app.get("/dream-experience.html", response_class=HTMLResponse)
async def dream_experience_page(request: Request):
    return render_template(request, "dream-experience.html")

@app.get("/dream-experience", response_class=HTMLResponse)
async def dream_experience_redirect(request: Request):
    return render_template(request, "dream-experience.html")

@app.get("/store", response_class=HTMLResponse)
async def store_page(request: Request):
    return RedirectResponse("/shop")

@app.get("/library", response_class=HTMLResponse)
async def library_page(request: Request):
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Weaver Library - قريباً</title>
        <style>
            body { font-family: 'Tajawal', sans-serif; background: #050210; color: #e2d9f3; min-height: 100vh; display: flex; align-items: center; justify-content: center; margin: 0; }
            .container { text-align: center; padding: 2rem; }
            h1 { font-size: 2rem; color: #f0c060; margin-bottom: 1rem; }
            p { color: #a855f7; font-size: 1.2rem; }
            a { color: #7c3aed; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📚 المكتبة قريباً</h1>
            <p>نعمل على تجهيز مكتبة شاملة للأحلام والتراث. تابعنا!</p>
            <p><a href="/">العودة للرئيسية →</a></p>
        </div>
    </body>
    </html>
    """)

@app.get("/app", response_class=HTMLResponse)
async def app_home(request: Request):
    stats = get_platform_stats()
    return render_template(request, "index.html", {"stats": stats})

@app.get("/privacy", response_class=HTMLResponse)
async def privacy_page(request: Request):
    return render_template(request, "privacy.html")

@app.get("/terms", response_class=HTMLResponse)
async def terms_page(request: Request):
    return render_template(request, "terms.html")

# التسجيل
@app.get("/app/register", response_class=HTMLResponse)
async def register_page(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse("/app/dashboard")
    return render_template(request, "register.html")

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
        return set_session_cookie(response, token)
    return render_template(request, "register.html", {"error": result.get("message", "خطأ في التسجيل")})

# تسجيل الدخول
@app.get("/app/login", response_class=HTMLResponse)
async def login_page(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse("/app/dashboard")
    return render_template(request, "login.html")

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
        return set_session_cookie(response, token)
    return render_template(request, "login.html", {"error": "خطأ في البريد الإلكتروني أو كلمة المرور"})

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

@app.get("/api/me")
async def api_me(request: Request):
    user = get_current_user(request)
    if not user:
        return JSONResponse({"authenticated": False}, status_code=401)
    return JSONResponse({
        "authenticated": True,
        "user_id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "plan": user.get("plan", "free")
    })

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
            response = JSONResponse({
                "success": True,
                "user_id": user["id"],
                "username": user["username"],
                "authenticated": True,
                "session_token": token
            })
            return set_session_cookie(response, token)
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
            response = JSONResponse({
                "success": True,
                "user_id": result["user_id"],
                "username": username,
                "authenticated": True,
                "session_token": token
            })
            return set_session_cookie(response, token)
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
    lang = request.cookies.get("lang", "ar")
    return render_template(request, "dashboard.html", {"dreams": dreams, "stats": stats})

# تفسير الأحلام
@app.get("/app/analyze", response_class=HTMLResponse)
async def analyze_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/app/login")
    return render_template(request, "analyze.html")

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
        return render_template(request, "analyze.html", {
            "error": "لقد استنفدت حد التفسيرات اليومي. يرجى الترقية للاستمرار.",
            "upgrade": True
        })

    interpretation = interpret_dream(dream, style=style, language=language)
    image_prompt = generate_image_prompt(dream)
    save_dream(user["id"], dream, interpretation, image_prompt)
    increment_dreams_used(user["id"])

    return render_template(request, "analyze.html", {
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
        
        # محاولة استخدام Ollama المحلي أولاً
        status = check_ollama_status()
        
        if status["status"] == "connected":
            result = interpret_dream_local(dream_text, style=style, language=language)
        else:
            # Fallback إلى API التقليدية
            result = interpret_dream(dream_text, style=style, language=language)
        
        return JSONResponse({"interpretation": result, "status": "success", "source": "ollama" if status["status"] == "connected" else "api"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# API: حالة Ollama
@app.get("/api/ollama-status")
async def ollama_status():
    from app.ai import check_ollama_status
    return JSONResponse(check_ollama_status())

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
    posts = get_all_blog_posts(limit=30)
    return render_template(request, "blog.html", {"posts": posts})

@app.get("/community", response_class=HTMLResponse)
async def community_alias(request: Request):
    return await community_page(request)

@app.get("/offers", response_class=HTMLResponse)
async def offers_alias(request: Request):
    return await offers_page(request)

@app.get("/app/dream/{dream_id}", response_class=HTMLResponse)
async def dream_detail_page(request: Request, dream_id: int):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/app/login")
    dream = next((item for item in get_user_dreams(user["id"]) if item.get("id") == dream_id), None)
    if not dream:
        raise HTTPException(status_code=404, detail="الحلم غير موجود")
    return render_template(request, "dream.html", {"dream": dream})

@app.post("/api/customer-reply")
async def api_customer_reply(request: Request):
    body = await request.json()
    message = str(body.get("message", "")).strip()
    language = body.get("language", "ar")
    if not message:
        return JSONResponse({"error": "message required"}, status_code=400)
    return JSONResponse({"reply": generate_customer_reply(message, language), "status": "success"})

@app.get("/api/public-dreams")
async def api_public_dreams():
    return JSONResponse({"dreams": get_public_dreams(limit=50)})

@app.get("/api/dreams")
async def api_user_dreams(request: Request):
    user = get_current_user(request)
    if not user:
        return JSONResponse({"error": "يجب تسجيل الدخول"}, status_code=401)
    dreams = get_user_dreams(user["id"])
    for dream in dreams:
        dream.setdefault("dream", dream.get("dream_text", ""))
    return JSONResponse({"dreams": dreams})

@app.get("/api/dream/{dream_id}")
async def api_dream(dream_id: int, request: Request):
    user = get_current_user(request)
    if not user:
        return JSONResponse({"error": "يجب تسجيل الدخول"}, status_code=401)
    dream = next((item for item in get_user_dreams(user["id"]) if item.get("id") == dream_id), None)
    if not dream:
        return JSONResponse({"error": "الحلم غير موجود"}, status_code=404)
    dream.setdefault("dream", dream.get("dream_text", ""))
    return JSONResponse(dream)

@app.get("/api/profile/{username}")
async def api_profile(username: str):
    users = [item for item in get_all_users(limit=1000) if item.get("username") == username]
    if not users:
        return JSONResponse({"error": "المستخدم غير موجود"}, status_code=404)
    user = users[0]
    dreams = get_user_dreams(user["id"])
    return JSONResponse({"username": user["username"], "dreams": dreams})

@app.get("/api/search")
async def api_search(keyword: str = ""):
    query = keyword.strip().lower()
    dreams = get_public_dreams(limit=100)
    results = [item for item in dreams if not query or query in str(item.get("dream_text", item.get("dream", ""))).lower()]
    return JSONResponse({"results": results})

@app.get("/api/trending")
async def api_trending():
    dreams = sorted(get_public_dreams(limit=100), key=lambda item: (item.get("likes", 0), item.get("views", 0)), reverse=True)
    return JSONResponse({"dreams": dreams[:30]})

@app.post("/api/analyze-dream")
async def api_analyze_dream(request: Request):
    user = get_current_user(request)
    if not user:
        return JSONResponse({"error": "يجب تسجيل الدخول أولاً"}, status_code=401)
    body = await request.json()
    dream_text = str(body.get("dream", "")).strip()
    if not dream_text:
        return JSONResponse({"error": "نص الحلم مطلوب"}, status_code=400)
    language = body.get("language", "ar")
    style = body.get("style", "islamic")
    interpretation = interpret_dream(dream_text, style=style, language=language)
    dream_id = save_dream(
        user["id"], dream_text, interpretation,
        style=style, language=language, is_public=body.get("public", 0)
    )
    increment_dreams_used(user["id"])
    return JSONResponse({"success": True, "dream_id": dream_id, "dream": dream_text, "interpretation": interpretation})

@app.get("/login")
async def login_alias():
    return RedirectResponse("/app/login")

@app.get("/register")
async def register_alias():
    return RedirectResponse("/app/register")

@app.get("/signup")
async def signup_alias():
    return RedirectResponse("/app/register")

@app.get("/dashboard")
async def dashboard_alias(request: Request):
    return await dashboard(request)

@app.get("/cart")
async def cart_alias():
    return RedirectResponse("/shop")

@app.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    return render_template(request, "contact.html")

@app.get("/creators", response_class=HTMLResponse)
async def creators_page(request: Request):
    return render_template(request, "explore.html")

@app.get("/dream-feed", response_class=HTMLResponse)
async def dream_feed_page(request: Request):
    return render_template(request, "dream-feed.html")

@app.get("/prompt-lab", response_class=HTMLResponse)
async def prompt_lab_page(request: Request):
    return render_template(request, "dream-interpreter.html")

@app.get("/trending", response_class=HTMLResponse)
async def trending_page(request: Request):
    return render_template(request, "trending.html")

@app.get("/feed.xml", response_class=HTMLResponse)
async def feed_xml(request: Request):
    posts = get_all_blog_posts(limit=30)
    items = []
    for post in posts:
        slug = str(post.get("slug", ""))
        title = str(post.get("title", "تقرير أحلام"))
        date = str(post.get("date", post.get("created_at", "")))
        items.append(
            "<item>"
            f"<title>{escape_xml(title)}</title>"
            f"<link>https://aidreamweaver.store/blog/{quote(slug)}</link>"
            f"<guid>https://aidreamweaver.store/blog/{quote(slug)}</guid>"
            f"<pubDate>{escape_xml(date)}</pubDate>"
            "</item>"
        )
    xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
        "<rss version=\"2.0\"><channel>" \
        "<title>Weaver Dream Feed</title>" \
        "<link>https://aidreamweaver.store/blog</link>" \
        "<description>أحدث مقالات وتقارير منصة نَسَّاج</description>" \
        + "".join(items) + "</channel></rss>"
    return HTMLResponse(content=xml, media_type="application/rss+xml")

@app.get("/reports", response_class=HTMLResponse)
@app.get("/reports/", response_class=HTMLResponse)
async def reports_page(request: Request):
    return render_template(request, "reports.html")

@app.get("/reports/{report_file:path}")
async def report_file(report_file: str):
    safe_name = Path(report_file).name
    if safe_name != report_file or safe_name in {"", ".", ".."}:
        raise HTTPException(status_code=403, detail="غير مصرح")
    candidate = None
    for folder in (APP_ROOT / "reports", APP_ROOT / "blog", APP_ROOT / "articles"):
        possible = folder / safe_name
        if possible.is_file():
            candidate = possible
            break
    if candidate is None:
        raise HTTPException(status_code=404, detail="التقرير غير موجود")
    return FileResponse(str(candidate))

@app.get("/{page_name}.html", response_class=HTMLResponse)
async def html_template_page(request: Request, page_name: str):
    template_name = f"{page_name}.html"
    if not (APP_ROOT / "templates" / template_name).is_file():
        raise HTTPException(status_code=404, detail="الصفحة غير موجودة")
    return render_template(request, template_name)

@app.get("/blog/{slug}", response_class=HTMLResponse)
async def blog_post_page(request: Request, slug: str):
    # إزالة .html إذا كانت موجودة في الـ slug لتجنب التكرار
    clean_slug = slug.replace(".html", "")
    
    # 1. حاول أولاً من مجلد templates/ (تقارير الحضارات الكلاسيكية المصممة بعناية)
    template_path = APP_ROOT / "templates" / f"{clean_slug}.html"
    if template_path.exists():
        # التأكد من أنه ليس أحد القوالب الأساسية المحمية
        protected_templates = ["index.html", "login.html", "register.html", "dashboard.html", "admin.html", "analyze.html", "blog.html", "blog_post.html"]
        if f"{clean_slug}.html" not in protected_templates:
            return render_template(request, f"{clean_slug}.html")

    # 2. حاول من أرشيف blog/ أو articles/ قبل الرجوع إلى قاعدة البيانات.
    for folder_name in ("blog", "articles"):
        file_path = APP_ROOT / folder_name / f"{clean_slug}.html"
        if file_path.exists():
            return HTMLResponse(content=file_path.read_text(encoding="utf-8", errors="ignore"))
            
    # 3. ثم من قاعدة البيانات
    posts = get_all_blog_posts(limit=200)
    post = next((p for p in posts if p.get("slug") == clean_slug or p.get("slug") == slug), None)
    if post:
        return render_template(request, "blog_post.html", {"post": post})
        
    raise HTTPException(status_code=404, detail="المقال غير موجود")

# إحصائيات المنصة
@app.get("/api/stats")
async def get_stats():
    stats = get_platform_stats()
    return JSONResponse(stats)

@app.get("/api/health")
async def health_check():
    import os
    files = os.listdir("templates") if os.path.exists("templates") else []
    return {
        "status": "ok",
        "version": "3.2.0",
        "templates_found": len(files),
        "files": files[:10]
    }

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
    return render_template(request, "admin.html", {
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
@app.head("/health")
def health_check():
    return {"status": "ok"}

# ========== نظام حماية المسارات ==========

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Middleware لفرض تسجيل الدخول على المسارات المحمية وإدارة الروابط"""
    
    # احتفظ بالصفحات ذات الامتداد .html إذا كان القالب موجوداً، وإلا استخدم الرابط النظيف.
    path = request.url.path
    if path.endswith(".html") and not path.startswith("/static/"):
        page_name = path.rsplit("/", 1)[-1]
        template_path = APP_ROOT / "templates" / page_name
        if template_path.is_file() or path.startswith("/reports/") or path.startswith("/articles/"):
            pass
        else:
            clean_path = path[:-5]
            if clean_path == "/blog":
                return RedirectResponse(url="/blog", status_code=301)
            return RedirectResponse(url=clean_path, status_code=301)
    
    # المسارات العامة التي لا تتطلب تسجيل دخول
    public_routes = [
        "/",
        "/app/login",
        "/app/register",
        "/api/login",
        "/api/register",
        "/api/me",
        "/api/interpret",
        "/api/ollama-status",
        "/api/customer-reply",
        "/api/subscribe",
        "/login",
        "/register",
        "/signup",
        "/contact",
        "/creators",
        "/dream-feed",
        "/prompt-lab",
        "/trending",
        "/feed.xml",
        "/cart",
        "/api/stats",
        "/api/health",
        "/health",
        "/blog",
        "/app/community",
        "/community",
        "/offers",
        "/reports",
        "/articles/",
        "/app/lucid-lab",
        "/app/cosmic-dictionary",
        "/app/global-map",
        "/app/personality-test",
        "/app/offers",
        "/about",
        "/faq",
        "/dream-interpreter",
        "/shop",
        "/dream-experience",
        "/static/",
        "/docs",
        "/openapi.json"
    ]
    
    # التحقق من ما إذا كان المسار عام
    is_public = False
    if path.endswith(".html") and ((APP_ROOT / "templates" / path.rsplit("/", 1)[-1]).is_file() or path.startswith("/articles/") or path.startswith("/reports/")):
        is_public = True
    for route in public_routes:
        if route.endswith("/"):
            if request.url.path.startswith(route):
                is_public = True
                break
        else:
            if request.url.path == route or request.url.path.startswith("/blog/"):
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

# ========== بوت تيليجرام عبر Webhook (sync version) ==========
@app.post("/webhook")
async def telegram_webhook(request: Request):
    """استقبال التحديثات من تيليجرام - synchronous"""
    import os
    import urllib.request
    import urllib.parse
    import json
    
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
    
    if not TELEGRAM_TOKEN:
        return JSONResponse({"error": "No token"}, status_code=500)
    
    try:
        # قراءة الـ body بشكل صحيح
        body_bytes = await request.body()  # direct access to body bytes
        if not body_bytes:
            return JSONResponse({"ok": True})
        
        data = json.loads(body_bytes)
        
        message = data.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")
        
        if not chat_id or not text:
            return JSONResponse({"ok": True})
        
        # دالة الإرسال
        def send_msg(msg_text):
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = json.dumps({"chat_id": chat_id, "text": msg_text, "parse_mode": "Markdown"})
            req = urllib.request.Request(url, data=payload.encode(), headers={"Content-Type": "application/json"})
            try:
                urllib.request.urlopen(req, timeout=10)
            except Exception as e:
                print(f"Send error: {e}")
        
        # معالجة الأوامر
        if text == "/start":
            send_msg("🌙 *مرحباً بك في نَسَّاج*\n\n🔮 /dream حلمك\n📊 /stats\n❓ /help")
        elif text == "/help":
            send_msg("🔮 /dream <نص> - فسّر\n/stats - إحصائيات")
        elif text == "/stats":
            try:
                with urllib.request.urlopen("https://aidreamweaver.store/api/stats", timeout=10) as r:
                    s = json.loads(r.read())
                    send_msg(f"📊 {s.get('users',0)} مستخدم\n🌙 {s.get('dreams',0)} حلم")
            except:
                send_msg("⚠️ تعذر")
        elif text.lower().startswith('/dream '):
            dream = text[7:]
            send_msg("🔮 جاري...")
            try:
                payload = json.dumps({"dream": dream, "style": "islamic", "language": "ar"}).encode()
                req = urllib.request.Request("https://aidreamweaver.store/api/interpret", data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    result = json.loads(r.read())
                    interp = result.get("interpretation","")[:4000]
                    if interp:
                        send_msg(interp)
            except Exception as e:
                send_msg(f"⚠️ {str(e)[:50]}")
        elif text and not text.startswith('/'):
            send_msg("🔮 جاري...")
            try:
                payload = json.dumps({"dream": text, "style": "islamic", "language": "ar"}).encode()
                req = urllib.request.Request("https://aidreamweaver.store/api/interpret", data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    result = json.loads(r.read())
                    interp = result.get("interpretation","")[:4000]
                    if interp:
                        send_msg(interp)
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


# ========== Static Files Fallback & Error Handlers ==========

# Handler للملفات الثابتة من المستوى الأعلى
@app.get("/favicon.ico")
async def favicon():
    favicon_path = APP_ROOT / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(str(favicon_path))
    return JSONResponse({"error": "Not found"}, status_code=404)

@app.get("/robots.txt")
async def robots():
    robots_path = APP_ROOT / "robots.txt"
    if robots_path.exists():
        return FileResponse(str(robots_path))
    return JSONResponse({"error": "Not found"}, status_code=404)

@app.get("/sitemap.xml")
async def sitemap():
    sitemap_path = APP_ROOT / "sitemap.xml"
    if sitemap_path.exists():
        return FileResponse(str(sitemap_path))
    return JSONResponse({"error": "Not found"}, status_code=404)

# Error handlers
@app.exception_handler(404)
async def not_found(request: Request, exc):
    return HTMLResponse(
        content="""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - الصفحة غير موجودة</title>
    <style>
        body { font-family: 'Tajawal', sans-serif; background: #050210; color: #e2d9f3; min-height: 100vh; display: flex; align-items: center; justify-content: center; margin: 0; }
        .container { text-align: center; padding: 2rem; }
        h1 { font-size: 4rem; color: #f0c060; margin-bottom: 1rem; }
        p { color: #a855f7; font-size: 1.2rem; }
        a { color: #7c3aed; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔮 404</h1>
        <p>الصفحة التي تبحث عنها غير موجودة</p>
        <p><a href="/">العودة للرئيسية →</a></p>
    </div>
</body>
</html>""",
        status_code=404
    )

@app.exception_handler(500)
async def server_error(request: Request, exc):
    return HTMLResponse(
        content="""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>500 - خطأ في الخادم</title>
    <style>
        body { font-family: 'Tajawal', sans-serif; background: #050210; color: #e2d9f3; min-height: 100vh; display: flex; align-items: center; justify-content: center; margin: 0; }
        .container { text-align: center; padding: 2rem; }
        h1 { font-size: 4rem; color: #ff6b6b; margin-bottom: 1rem; }
        p { color: #a855f7; font-size: 1.2rem; }
        a { color: #7c3aed; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚠️ 500</h1>
        <p>حدث خطأ في الخادم. نعمل على إصلاحه.</p>
        <p><a href="/">العودة للرئيسية →</a></p>
    </div>
</body>
</html>""",
        status_code=500
    )


# ========== Production Entry Point ==========
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)

