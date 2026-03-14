#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════╗
║       🧵 Weaver | نَسَّاج — Telegram Dream Bot v3.1           ║
║  بوت تفسير الأحلام بالذكاء الاصطناعي — نسخة محدّثة كاملة    ║
╠══════════════════════════════════════════════════════════════╣
║  التحديثات الجديدة:                                           ║
║  ✅ نظام 5 مزودين مجانيين للصور (felo.ai, Pollinations, etc.) ║
║  ✅ التبديل التلقائي عند فشل أي مزود                         ║
║  ✅ إحصائيات أداء المزودين                                     ║
║  ✅ معالجة أخطاء Imagen 3                                      ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import json
import time
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)
from telegram.constants import ParseMode, ChatAction

# ============================================================
# ✅ تم التعديل هنا: استيراد النظام المتعدد من الملف الصحيح (مع حرف s)
# ============================================================
try:
    from images_generators import ImageGenerator, generate_image
    IMAGE_SYSTEM_AVAILABLE = True
    print("✅ نظام الصور المتعدد جاهز (5 مزودين مجانيين)")
except ImportError as e:
    IMAGE_SYSTEM_AVAILABLE = False
    print(f"⚠️ نظام الصور المتعدد غير موجود. استخدم images_generators.py. تفاصيل: {e}")

# ─────────────────────────────────────────────────
# ⚙️ الإعدادات
# ─────────────────────────────────────────────────

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
SILICONFLOW_API_KEY = os.environ.get("SILICONFLOW_API_KEY", "")
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", "6790340715"))

if not TELEGRAM_TOKEN:
    print("❌ خطأ فادح: TELEGRAM_TOKEN غير موجود!")
    exit(1)

# إنشاء كائن توليد الصور
if IMAGE_SYSTEM_AVAILABLE:
    image_generator = ImageGenerator(
        gemini_api_key=GEMINI_API_KEY,
        siliconflow_api_key=SILICONFLOW_API_KEY
    )
else:
    image_generator = None

# ─────────────────────────────────────────────────
# 📋 التسجيل
# ─────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("weaver.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────
# 💾 إدارة البيانات (leads.json)
# ─────────────────────────────────────────────────

LEADS_FILE = "leads.json"

def load_leads() -> dict:
    default = {
        "total_users": 0, "users": [],
        "dreams": 0, "images": 0, "articles": 0,
    }
    try:
        p = Path(LEADS_FILE)
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        log.error(f"load_leads: {e}")
    return default

def save_leads(data: dict) -> None:
    try:
        Path(LEADS_FILE).write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    except Exception as e:
        log.error(f"save_leads: {e}")

def get_user(user_id: int) -> dict | None:
    for u in load_leads()["users"]:
        if int(u["id"]) == user_id:
            return u
    return None

def upsert_user(tg_user) -> dict:
    data = load_leads()
    today = datetime.now().date().isoformat()

    for u in data["users"]:
        if int(u["id"]) == int(tg_user.id):
            u["id"] = int(tg_user.id)
            u["last_seen"] = datetime.now().isoformat()
            u["username"] = tg_user.username or u.get("username", "")
            u["name"] = tg_user.full_name or u.get("name", "")
            u["interactions"] = u.get("interactions", 0) + 1
            
            if tg_user.id == ADMIN_USER_ID:
                u["plan"] = "admin"
            
            if u.get("last_reset") != today:
                u["dreams_today"] = 0
                u["images_today"] = 0
                u["last_reset"] = today
            
            save_leads(data)
            return u

    # مستخدم جديد
    is_admin = (tg_user.id == ADMIN_USER_ID)
    new_u = {
        "id": int(tg_user.id),
        "username": tg_user.username or "",
        "name": tg_user.full_name or "",
        "joined": datetime.now().isoformat(),
        "last_seen": datetime.now().isoformat(),
        "last_reset": today,
        "interactions": 1,
        "plan": "admin" if is_admin else "free",
        "dreams_today": 0,
        "images_today": 0,
        "total_dreams": 0,
        "total_images": 0,
    }
    data["users"].append(new_u)
    data["total_users"] = len(data["users"])
    save_leads(data)
    log.info(f"👤 مستخدم جديد: {tg_user.id} @{tg_user.username}")
    return new_u

def check_limit(user_id: int, field: str) -> tuple[bool, int, int]:
    data = load_leads()
    today = datetime.now().date().isoformat()
    user = None

    for u in data["users"]:
        if int(u["id"]) == user_id:
            user = u
            break

    if not user:
        return True, 0, 5

    if user.get("last_reset") != today:
        user["dreams_today"] = 0
        user["images_today"] = 0
        user["last_reset"] = today
        save_leads(data)

    used = user.get(field, 0)
    plan_name = user.get("plan", "free")
    
    # خطط الاشتراك
    PLANS = {
        "free": {"daily_dreams": 5, "daily_images": 2},
        "basic": {"daily_dreams": 5, "daily_images": 3},
        "pro": {"daily_dreams": 9999, "daily_images": 9999},
        "team": {"daily_dreams": 9999, "daily_images": 9999},
        "admin": {"daily_dreams": 9999, "daily_images": 9999},
    }
    
    limit = PLANS.get(plan_name, PLANS["free"])
    if field == "dreams_today":
        return used < limit["daily_dreams"], used, limit["daily_dreams"]
    else:
        return used < limit["daily_images"], used, limit["daily_images"]

def inc_field(user_id: int, user_field: str, global_field: str) -> None:
    data = load_leads()
    for u in data["users"]:
        if int(u["id"]) == user_id:
            u[user_field] = u.get(user_field, 0) + 1
            if "dream" in user_field:
                u["total_dreams"] = u.get("total_dreams", 0) + 1
            else:
                u["total_images"] = u.get("total_images", 0) + 1
            break
    data[global_field] = data.get(global_field, 0) + 1
    save_leads(data)

# ─────────────────────────────────────────────────
# 🤖 Gemini — تفسير الأحلام
# ─────────────────────────────────────────────────

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

def call_gemini(prompt: str, temperature: float = 0.75) -> str:
    if not GEMINI_API_KEY:
        return "❌ مفتاح Gemini غير موجود"
    try:
        import requests
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 1600,
                "topP": 0.92,
            },
        }
        r = requests.post(GEMINI_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        elif r.status_code == 429:
            return "RATE_LIMITED"
        else:
            log.error(f"Gemini {r.status_code}: {r.text[:200]}")
            return f"❌ خطأ Gemini {r.status_code}"
    except Exception as e:
        log.error(f"call_gemini: {e}")
        return f"❌ خطأ: {str(e)[:100]}"

def build_dream_prompt(dream: str) -> str:
    return f"""أنت نظام تفسير أحلام متخصص يجمع منهجية الإمام ابن سيرين مع الذكاء الاصطناعي.

قواعدك:
- فرّق بين الرؤيا الصادقة والحلم العادي
- راعِ رمزية القرآن الكريم واللغة العربية
- قدّم تفسيراً عملياً ومتكاملاً يراعي السياق
- أشر دائماً أن التفسير للاستئناس وليس فتوى

الحلم: {dream}

اكتب تفسيراً منظماً:
1. 🌙 **المقدمة** — الانطباع العام
2. 🔮 **الرموز** — أبرز الرموز ومعانيها
3. ✨ **التفسير** — الرسالة الكاملة
4. 💡 **التوجيه** — نصيحة عملية للحالم
5. 📿 **الختام** — ملاحظة دينية أو روحية خفيفة"""

def translate_for_image(arabic: str) -> str:
    prompt = f"Translate this Arabic dream to vivid English for AI image generation. Make it atmospheric and visual. Max 100 words. Output ONLY the English.\n\nArabic: {arabic}"
    result = call_gemini(prompt, temperature=0.5)
    if result.startswith("❌") or result == "RATE_LIMITED":
        return "a mystical dream scene with surreal elements, glowing atmosphere, ethereal light"
    return result

# ─────────────────────────────────────────────────
# 🎨 دالة توليد الصور (تستخدم النظام المتعدد)
# ─────────────────────────────────────────────────

async def generate_dream_image(prompt: str) -> bytes | None:
    if not image_generator:
        log.error("نظام الصور غير متاح")
        return None
    
    try:
        loop = asyncio.get_event_loop()
        img_bytes = await loop.run_in_executor(
            None, 
            lambda: image_generator.generate(prompt)
        )
        return img_bytes
    except Exception as e:
        log.error(f"generate_dream_image: {e}")
        return None

# ============================================================
# هنا بقية الكود (لوحات المفاتيح، أوامر المستخدم، معالج الأزرار، أوامر المسؤول، التشغيل)
# ============================================================
# (لاختصار الرد، لم أكرر بقية الكود لأنه لم يتغير. 
#  تأكد من أن الكود الكامل الموجود عندك يبدأ من هنا فصاعداً.
#  إذا احتجت الملف كاملاً من جديد، فأخبرني.)
