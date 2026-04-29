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

# --- أنظمة الربح والنمو ---
from app.subscriptions import get_user_subscription, upgrade_subscription, create_subscription_tables, get_revenue_stats
from app.payment import PaymentProcessor, get_payment_analytics
from app.seo_generator import get_seo_page, get_seo_stats, generate_all_seo_pages
from app.viral_sharing import ViralShareGenerator, ReferralSystem, ViralMetrics

# تهيئة جداول الاشتراكات
create_subscription_tables()

# --- صفحات الرموز (SEO) ---
@app.get("/dream/{slug}", response_class=HTMLResponse)
async def dream_symbol_page(request: Request, slug: str):
    """صفحة تفسير الرمز (مُحسّنة للـ SEO)"""
    page = get_seo_page(slug)
    if not page:
        raise HTTPException(status_code=404, detail="الرمز غير موجود")
    
    user = get_current_user(request)
    return templates.TemplateResponse(request, "dream_symbol.html", {
        "page": page,
        "user": user
    })

# --- صفحة الترقية ---
@app.get("/app/upgrade", response_class=HTMLResponse)
async def upgrade_page(request: Request):
    """صفحة الترقية إلى خطط مدفوعة"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/app/login")
    
    subscription = get_user_subscription(user["id"])
    return templates.TemplateResponse(request, "upgrade.html", {
        "user": user,
        "subscription": subscription,
        "plans": {
            "pro": {"price": 9.99, "features": ["تفسير متقدم", "صور الأحلام", "تحليل نفسي"]},
            "business": {"price": 29.99, "features": ["تفسير غير محدود", "صور 4K", "API"]}
        }
    })

# --- معالجة الدفع ---
@app.post("/api/checkout")
async def checkout(request: Request):
    """إنشاء جلسة دفع"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({"error": "يجب تسجيل الدخول أولاً"}, status_code=401)
    
    body = await request.json()
    plan = body.get("plan", "pro")
    
    # إنشاء جلسة Stripe
    session = PaymentProcessor.create_stripe_checkout(user["id"], plan, 9.99)
    return JSONResponse(session)

# --- المشاركة الفيروسية ---
@app.get("/share/{symbol}")
async def share_dream(request: Request, symbol: str):
    """صفحة المشاركة الفيروسية"""
    generator = ViralShareGenerator()
    share_data = generator.generate_share_card(f"تفسير حلم {symbol}", symbol)
    
    return templates.TemplateResponse(request, "share.html", {
        "symbol": symbol,
        "share_data": share_data
    })

# --- الإحالة ---
@app.get("/api/referral/{user_id}")
async def get_referral_link(user_id: int):
    """الحصول على رابط الإحالة"""
    referral = ReferralSystem.generate_referral_link(user_id)
    return JSONResponse(referral)

# --- إحصائيات الربح ---
@app.get("/api/revenue-stats")
async def revenue_stats(request: Request):
    """إحصائيات الإيرادات"""
    user = get_current_user(request)
    if not user or user.get("role") != "admin":
        return JSONResponse({"error": "غير مصرح"}, status_code=403)
    
    stats = get_revenue_stats()
    payment_stats = get_payment_analytics()
    seo_stats = get_seo_stats()
    viral_metrics = ViralMetrics.get_viral_metrics()
    
    return JSONResponse({
        "revenue": stats,
        "payments": payment_stats,
        "seo": seo_stats,
        "viral": viral_metrics
    })

# --- توليد صفحات SEO ---
@app.post("/admin/generate-seo")
async def admin_generate_seo(request: Request):
    """توليد جميع صفحات SEO"""
    user = get_current_user(request)
    if not user or user.get("role") != "admin":
        return JSONResponse({"error": "غير مصرح"}, status_code=403)
    
    result = generate_all_seo_pages()
    return JSONResponse(result)


# --- صفحة المدونة ---
@app.get("/blog", response_class=HTMLResponse)
async def blog_page(request: Request):
    """صفحة المدونة الرئيسية مع نموذج جمع الإيميلات"""
    user = get_current_user(request)
    return templates.TemplateResponse(request, "blog.html", {
        "user": user,
        "posts": []
    })

# --- نموذج جمع الإيميلات ---
@app.post("/api/subscribe")
async def subscribe_newsletter(request: Request):
    """جمع الإيميلات من النشرة البريدية"""
    try:
        body = await request.json()
        email = body.get("email")
        
        if not email:
            return JSONResponse({"error": "البريد الإلكتروني مطلوب"}, status_code=400)
        
        # حفظ الإيميل في قاعدة البيانات
        conn = sqlite3.connect("app/weaver.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR IGNORE INTO newsletter_subscribers (email, subscribed_at)
            VALUES (?, CURRENT_TIMESTAMP)
        """)
        
        conn.commit()
        conn.close()
        
        return JSONResponse({
            "success": True,
            "message": "تم الاشتراك بنجاح! شكراً لك 🌙"
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# --- جدول المشتركين ---
def create_newsletter_table():
    """إنشاء جدول المشتركين في النشرة البريدية"""
    conn = sqlite3.connect("app/weaver.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS newsletter_subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
    """)
    
    conn.commit()
    conn.close()

# تهيئة جدول المشتركين عند بدء التطبيق
create_newsletter_table()

# --- الحصول على قائمة الإيميلات للتسويق ---
@app.get("/api/emails-for-marketing")
async def get_emails_for_marketing(request: Request):
    """الحصول على قائمة الإيميلات للحملات التسويقية"""
    user = get_current_user(request)
    if not user or user.get("role") != "admin":
        return JSONResponse({"error": "غير مصرح"}, status_code=403)
    
    conn = sqlite3.connect("app/weaver.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT email, subscribed_at FROM newsletter_subscribers
        WHERE status = 'active'
        ORDER BY subscribed_at DESC
    """)
    
    emails = [{"email": row[0], "subscribed_at": row[1]} for row in cursor.fetchall()]
    conn.close()
    
    return JSONResponse({
        "total_emails": len(emails),
        "emails": emails
    })

