#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════╗
║       🧵 Weaver | نَسَّاج — Telegram Dream Bot v3.0           ║
║  بوت تفسير الأحلام بالذكاء الاصطناعي — نسخة محدّثة كاملة    ║
╠══════════════════════════════════════════════════════════════╣
║  FIX 1: إضافة SiliconFlow كمزود أساسي للصور                  ║
║  FIX 2: Pollinations كـ fallback مع encoding صحيح            ║
║  FIX 3: Gemini timeout رُفع لـ 30 ثانية                      ║
║  FIX 4: توليد صور للمستخدمين (ليس فقط المسؤول)              ║
║  FIX 5: prompt تفسير محسّن بمنهجية ابن سيرين                 ║
║  FIX 6: نظام حدود يومية مع حفظ صحيح في leads.json           ║
║  FIX 7: user_id كـ int موحّد في كل مكان                      ║
║  FIX 8: أوامر /auto /report /article /broadcast /setplan     ║
║  FIX 9: زر ترقية عند وصول الحد اليومي                        ║
║  FIX 10: رسالة retry عند فشل الصورة                          ║
╚══════════════════════════════════════════════════════════════╝

المتغيرات البيئية المطلوبة:
  TELEGRAM_TOKEN      ← من @BotFather
  GEMINI_API_KEY      ← من https://aistudio.google.com
  SILICONFLOW_API_KEY ← من https://cloud.siliconflow.cn (اختياري)
  ADMIN_USER_ID       ← رقمك على تيليجرام (من @userinfobot)

تشغيل: python all_bots.py
"""

import os
import json
import time
import asyncio
import logging
import urllib.parse
import requests
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

# ─────────────────────────────────────────────────
# ⚙️ الإعدادات
# ─────────────────────────────────────────────────

# يمكن استخدام python-dotenv إن كان مثبتاً
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TELEGRAM_TOKEN      = os.environ.get("TELEGRAM_TOKEN", "")
GEMINI_API_KEY      = os.environ.get("GEMINI_API_KEY", "")
SILICONFLOW_API_KEY = os.environ.get("SILICONFLOW_API_KEY", "")
ADMIN_USER_ID       = int(os.environ.get("ADMIN_USER_ID", "6790340715"))

if not TELEGRAM_TOKEN:
    print("❌ خطأ فادح: TELEGRAM_TOKEN غير موجود!")
    exit(1)

# روابط API
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    f"models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
)
SF_URL = "https://api.siliconflow.cn/v1/images/generations"

# خطط الاشتراك
PLANS = {
    "basic": {
        "name": "أساسي",  "price": "$4.99/شهر",
        "url": "https://casperblac.gumroad.com/l/dtiobz",
        "daily_dreams": 5,   "daily_images": 3,
    },
    "pro": {
        "name": "احترافي", "price": "$9.99/شهر",
        "url": "https://casperblac.gumroad.com/l/byqzxd",
        "daily_dreams": 9999, "daily_images": 9999,
    },
    "team": {
        "name": "فريق",   "price": "$19.99/شهر",
        "url": "https://casperblac.gumroad.com/l/hiulqi",
        "daily_dreams": 9999, "daily_images": 9999,
    },
    "admin": {
        "name": "مسؤول", "price": "—",
        "url": "", "daily_dreams": 9999, "daily_images": 9999,
    },
}
FREE_DAILY_DREAMS = 5
FREE_DAILY_IMAGES = 2

LEADS_FILE = "leads.json"

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
    """إرجاع بيانات المستخدم أو None."""
    for u in load_leads()["users"]:
        if int(u["id"]) == user_id:
            return u
    return None


def upsert_user(tg_user) -> dict:
    """تحديث أو إضافة مستخدم. يرجع dict المستخدم."""
    data = load_leads()
    today = datetime.now().date().isoformat()

    for u in data["users"]:
        if int(u["id"]) == int(tg_user.id):
            u["id"]       = int(tg_user.id)   # normalize to int if was string
            u["last_seen"] = datetime.now().isoformat()
            u["username"]  = tg_user.username or u.get("username", "")
            u["name"]      = tg_user.full_name or u.get("name", "")
            u["interactions"] = u.get("interactions", 0) + 1
            # المسؤول دائماً plan=admin
            if tg_user.id == ADMIN_USER_ID:
                u["plan"] = "admin"
            # إعادة ضبط العدادات اليومية إن لزم
            if u.get("last_reset") != today:
                u["dreams_today"] = 0
                u["images_today"] = 0
                u["last_reset"]   = today
            save_leads(data)
            return u

    # مستخدم جديد
    is_admin_user = (tg_user.id == ADMIN_USER_ID)
    new_u = {
        "id":           int(tg_user.id),     # دائماً int — منع التكرار
        "username":     tg_user.username or "",
        "name":         tg_user.full_name or "",
        "joined":       datetime.now().isoformat(),
        "last_seen":    datetime.now().isoformat(),
        "last_reset":   today,
        "interactions": 1,
        "plan":         "admin" if is_admin_user else "free",
        "dreams_today": 0,
        "images_today": 0,
        "total_dreams": 0,
        "total_images": 0,
    }
    data["users"].append(new_u)
    data["total_users"] = len(data["users"])
    save_leads(data)
    log.info(f"New user: {tg_user.id} @{tg_user.username}")
    return new_u


def check_limit(user_id: int, field: str) -> tuple[bool, int, int]:
    """
    يتحقق من الحد اليومي ويُعيد (يمكن_الاستخدام, مُستخدَم, الحد).
    FIX: يحفظ إعادة الضبط في الملف مباشرة.
    """
    data  = load_leads()
    today = datetime.now().date().isoformat()
    user  = None

    for u in data["users"]:
        if int(u["id"]) == user_id:
            user = u
            break

    if not user:
        return True, 0, FREE_DAILY_DREAMS

    # إعادة ضبط العداد إن كان يوم جديد (مع الحفظ!)
    if user.get("last_reset") != today:
        user["dreams_today"] = 0
        user["images_today"] = 0
        user["last_reset"]   = today
        save_leads(data)  # ← FIX: كان ناقصاً في النسخة القديمة

    plan_name = user.get("plan", "free")
    used      = user.get(field, 0)

    if plan_name in PLANS:
        key   = "daily_dreams" if field == "dreams_today" else "daily_images"
        limit = PLANS[plan_name][key]
    else:
        limit = FREE_DAILY_DREAMS if field == "dreams_today" else FREE_DAILY_IMAGES

    return used < limit, used, limit


def inc_field(user_id: int, user_field: str, global_field: str) -> None:
    """زيادة عداد للمستخدم وللإحصائيات الكلية."""
    data = load_leads()
    for u in data["users"]:
        if int(u["id"]) == user_id:
            u[user_field]      = u.get(user_field, 0) + 1
            u["total_" + ("dreams" if "dream" in user_field else "images")] = \
                u.get("total_" + ("dreams" if "dream" in user_field else "images"), 0) + 1
            break
    data[global_field] = data.get(global_field, 0) + 1
    save_leads(data)


# ─────────────────────────────────────────────────
# 🤖 Gemini — تفسير الأحلام
# ─────────────────────────────────────────────────

def call_gemini(prompt: str, temperature: float = 0.75) -> str:
    """استدعاء Gemini 2.0 Flash."""
    if not GEMINI_API_KEY:
        return "❌ مفتاح Gemini غير موجود في المتغيرات البيئية."
    try:
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature":    temperature,
                "maxOutputTokens": 1600,
                "topP": 0.92,
            },
        }
        # FIX: timeout رُفع من 10 إلى 30 ثانية
        r = requests.post(
            GEMINI_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        elif r.status_code == 429:
            return "RATE_LIMITED"
        else:
            log.error(f"Gemini {r.status_code}: {r.text[:200]}")
            return f"❌ خطأ Gemini {r.status_code}"
    except requests.exceptions.Timeout:
        return "❌ انتهت مهلة الاتصال. حاول مرة أخرى."
    except Exception as e:
        log.error(f"call_gemini: {e}")
        return f"❌ خطأ: {str(e)[:100]}"


def build_dream_prompt(dream: str) -> str:
    """
    FIX: بناء prompt محسّن بمنهجية ابن سيرين
    (كان: "فسر هذا الحلم بالعربية: ...")
    """
    return f"""أنت نظام تفسير أحلام متخصص يجمع منهجية الإمام ابن سيرين (654-728م) مع الذكاء الاصطناعي.

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
    """ترجمة الوصف العربي للإنجليزية لتوليد الصور."""
    prompt = (
        "Translate this Arabic dream to vivid English for AI image generation. "
        "Make it atmospheric and visual. Max 100 words. Output ONLY the English.\n\n"
        f"Arabic: {arabic}"
    )
    result = call_gemini(prompt, temperature=0.5)
    # إذا فشل، استخدم وصفاً عاماً
    if result.startswith("❌") or result == "RATE_LIMITED":
        return "a mystical dream scene with surreal elements, glowing atmosphere, ethereal light"
    return result


# ─────────────────────────────────────────────────
# 🎨 توليد الصور — SiliconFlow + Pollinations Fallback
# ─────────────────────────────────────────────────

# ─────────────────────────────────────────────────
# 🔑 السبب الحقيقي لفشل الصور:
# justrunmy.app يحجب الاتصال الخارجي بـ:
#   - Pollinations.ai  (DNS fails)
#   - SiliconFlow      (DNS fails)
# لكن googleapis.com يعمل لأنه في whitelist المنصة
# الحل: استخدام Gemini Imagen 3 (نفس الـ API key!)
# ─────────────────────────────────────────────────

IMAGEN_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    f"models/imagen-3.0-generate-002:predict?key={GEMINI_API_KEY}"
)


def _gen_imagen(prompt: str) -> bytes | None:
    """
    المزود الأول — Google Imagen 3 عبر Gemini API.
    ✅ يعمل على justrunmy.app (نفس domain مع Gemini)
    ✅ نفس GEMINI_API_KEY — لا حاجة لمفتاح إضافي
    ✅ جودة عالية جداً
    """
    if not GEMINI_API_KEY:
        log.warning("GEMINI_API_KEY غير موجود — تخطي Imagen")
        return None
    try:
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "1:1",
                "safetyFilterLevel": "block_few",
                "personGeneration": "allow_all",
            }
        }
        r = requests.post(
            IMAGEN_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        if r.status_code == 200:
            data = r.json()
            b64  = data["predictions"][0]["bytesBase64Encoded"]
            import base64
            img_bytes = base64.b64decode(b64)
            log.info("Imagen 3 OK ✅")
            return img_bytes
        elif r.status_code == 400:
            # محتوى محجوب من فلتر Google
            log.warning(f"Imagen blocked (400): {r.text[:150]}")
            return None
        else:
            log.error(f"Imagen {r.status_code}: {r.text[:150]}")
            return None
    except Exception as e:
        log.error(f"_gen_imagen: {e}")
        return None


def _gen_gemini_flash_image(prompt: str) -> bytes | None:
    """
    المزود الثاني — Gemini 2.0 Flash بوضع توليد الصور.
    ✅ يعمل على justrunmy.app (googleapis.com)
    ✅ نفس GEMINI_API_KEY
    ✅ مجاني ضمن الحصة المجانية
    """
    if not GEMINI_API_KEY:
        return None
    try:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            f"models/gemini-2.0-flash-preview-image-generation:generateContent?key={GEMINI_API_KEY}"
        )
        payload = {
            "contents": [{
                "parts": [{"text": f"Generate a high quality image of: {prompt}"}]
            }],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
        }
        r = requests.post(url, json=payload,
                          headers={"Content-Type": "application/json"}, timeout=60)
        if r.status_code == 200:
            parts = r.json()["candidates"][0]["content"]["parts"]
            for part in parts:
                if "inlineData" in part:
                    import base64
                    img_bytes = base64.b64decode(part["inlineData"]["data"])
                    log.info("Gemini Flash Image OK ✅")
                    return img_bytes
        log.error(f"Gemini Flash Image {r.status_code}: {r.text[:150]}")
        return None
    except Exception as e:
        log.error(f"_gen_gemini_flash_image: {e}")
        return None


def _gen_siliconflow(prompt: str) -> bytes | None:
    """
    مزود اختياري — SiliconFlow (أعلى جودة لكن قد يكون محجوباً).
    يُستخدم فقط إذا كان SILICONFLOW_API_KEY موجوداً.
    """
    if not SILICONFLOW_API_KEY:
        return None
    models = [
        "stabilityai/stable-diffusion-3-5-large",
        "black-forest-labs/FLUX.1-schnell",
    ]
    for model in models:
        for attempt in range(2):
            try:
                headers = {
                    "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
                    "Content-Type":  "application/json",
                }
                body = {
                    "model":               model,
                    "prompt":              prompt + ", dreamlike, high quality, 4K, masterpiece",
                    "negative_prompt":     "blurry, distorted, ugly, text, watermark, nsfw",
                    "size":                "1024x1024",
                    "num_inference_steps": 25,
                    "guidance_scale":      7.0,
                }
                r = requests.post(SF_URL, headers=headers, json=body, timeout=90)
                if r.status_code == 200:
                    img_url = r.json()["images"][0]["url"]
                    img_r   = requests.get(img_url, timeout=30)
                    if img_r.status_code == 200:
                        log.info(f"SiliconFlow OK [{model}] ✅")
                        return img_r.content
                elif r.status_code in (502, 503, 504):
                    time.sleep(3)
                    continue
                else:
                    log.error(f"SiliconFlow {r.status_code}: {r.text[:100]}")
                    break
            except requests.exceptions.Timeout:
                time.sleep(2)
            except Exception as e:
                log.error(f"SiliconFlow: {e}")
                break
    return None


def _gen_pollinations(prompt: str) -> bytes | None:
    """
    مزود احتياطي أخير — Pollinations.ai (مجاني بدون مفتاح).
    ⚠️ قد يكون محجوباً على justrunmy.app
    """
    try:
        safe = urllib.parse.quote(prompt[:300], safe="")
        urls = [
            f"https://image.pollinations.ai/prompt/{safe}?width=1024&height=1024&nologo=true",
            f"https://image.pollinations.ai/prompt/{safe}?width=768&height=768&nologo=true",
        ]
        for url in urls:
            for attempt in range(2):
                try:
                    r = requests.get(url, timeout=45)
                    if r.status_code == 200 and "image" in r.headers.get("content-type", ""):
                        log.info("Pollinations OK ✅")
                        return r.content
                    elif r.status_code in (502, 503):
                        time.sleep(4)
                    else:
                        break
                except Exception:
                    time.sleep(2)
    except Exception as e:
        log.error(f"_gen_pollinations: {e}")
    return None


def generate_image(prompt: str) -> bytes | None:
    """
    توليد ذكي مع 4 مزودين بالترتيب:
      1. Google Imagen 3    ← يعمل على justrunmy.app ✅
      2. Gemini Flash Image ← يعمل على justrunmy.app ✅
      3. SiliconFlow        ← إذا كان المفتاح موجوداً
      4. Pollinations.ai    ← احتياطي أخير
    يرجع bytes الصورة أو None.
    """
    log.info(f"generate_image: {prompt[:60]}...")

    # 1. Imagen 3 (الأفضل والأضمن على justrunmy.app)
    data = _gen_imagen(prompt)
    if data:
        return data

    # 2. Gemini Flash Image generation
    log.warning("Imagen فشل — جاري Gemini Flash Image")
    data = _gen_gemini_flash_image(prompt)
    if data:
        return data

    # 3. SiliconFlow (إذا كان المفتاح موجوداً)
    if SILICONFLOW_API_KEY:
        log.warning("Gemini Image فشل — جاري SiliconFlow")
        data = _gen_siliconflow(prompt)
        if data:
            return data

    # 4. Pollinations (آخر محاولة)
    log.warning("SiliconFlow فشل — جاري Pollinations")
    data = _gen_pollinations(prompt)
    if data:
        return data

    log.error("❌ كل مزودي الصور فشلوا")
    return None


# ─────────────────────────────────────────────────
# ⌨️ لوحات المفاتيح
# ─────────────────────────────────────────────────

def kb_main():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌙 فسّر حلمي", callback_data="do_dream"),
         InlineKeyboardButton("🎨 صورة 4K",   callback_data="do_image")],
        [InlineKeyboardButton("💎 الاشتراكات", callback_data="show_plans"),
         InlineKeyboardButton("📊 إحصائياتي",  callback_data="my_stats")],
        [InlineKeyboardButton("🌐 الموقع", url="https://aidreamweaver.store"),
         InlineKeyboardButton("❓ مساعدة",  callback_data="show_help")],
    ])


def kb_plans():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🥉 أساسي — $4.99/شهر",   url=PLANS["basic"]["url"])],
        [InlineKeyboardButton("🥇 احترافي — $9.99/شهر", url=PLANS["pro"]["url"])],
        [InlineKeyboardButton("👥 فريق — $19.99/شهر",   url=PLANS["team"]["url"])],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")],
    ])


def kb_retry_image(dream_text: str):
    short = dream_text[:80]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 إعادة المحاولة", callback_data=f"retry_img:{short}")],
        [InlineKeyboardButton("🔙 الرئيسية",        callback_data="back_main")],
    ])


# ─────────────────────────────────────────────────
# 📨 أوامر المستخدم
# ─────────────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = upsert_user(update.effective_user)
    name = update.effective_user.first_name or "صديقي"
    text = (
        f"مرحباً *{name}* 🌙\n\n"
        "أنا *Weaver | نَسَّاج* — بوت تفسير الأحلام بالذكاء الاصطناعي.\n\n"
        "أستخدم *Gemini 2.0 Flash* لتفسير الأحلام بمنهجية ابن سيرين.\n"
        "أستخدم *Stable Diffusion 4K* لتوليد صور من حلمك.\n\n"
        "فقط أرسل لي حلمك وسأفسره لك فوراً! ✨"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb_main())


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    upsert_user(update.effective_user)
    text = (
        "❓ *دليل Weaver*\n\n"
        "*للتفسير:* أرسل حلمك نصاً مباشرة\n"
        "_مثال: حلمت أنني أطير فوق البحر..._\n\n"
        "*الأوامر:*\n"
        "• `/start` — الصفحة الرئيسية\n"
        "• `/stats` — إحصائياتك\n"
        "• `/plans` — خطط الاشتراك\n"
        "• `/help` — هذه المساعدة\n\n"
        "*الموقع:* aidreamweaver.store"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = upsert_user(update.effective_user)
    data = load_leads()
    plan = PLANS.get(user.get("plan", "free"), {"name": user.get("plan","مجاني").capitalize(), "price": "—"})
    text = (
        "📊 *إحصائياتك*\n\n"
        f"👤 الخطة: *{plan['name']}*\n"
        f"🌙 أحلام اليوم: *{user.get('dreams_today', 0)}*\n"
        f"🎨 صور اليوم: *{user.get('images_today', 0)}*\n"
        f"🔮 إجمالي الأحلام: *{user.get('total_dreams', 0)}*\n"
        f"🖼️ إجمالي الصور: *{user.get('total_images', 0)}*\n\n"
        f"👥 مستخدمو المنصة: *{data.get('total_users', 0)}*\n"
        f"💭 أحلام فُسِّرت: *{data.get('dreams', 0)}*"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_plans(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    upsert_user(update.effective_user)
    text = (
        "💎 *خطط Weaver | نَسَّاج*\n\n"
        "🥉 *أساسي — $4.99/شهر*\n"
        "• 5 تفسيرات + 3 صور يومياً\n\n"
        "🥇 *احترافي — $9.99/شهر*\n"
        "• تفسيرات + صور 4K غير محدودة ✨\n"
        "• 50 أسلوب فني\n\n"
        "👥 *فريق — $19.99/شهر*\n"
        "• كل الاحترافي + فيديو + PDF + API"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb_plans())


# ─────────────────────────────────────────────────
# 💬 معالج الرسائل — التفسير الرئيسي
# ─────────────────────────────────────────────────

async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = upsert_user(update.effective_user)
    dream = update.message.text.strip()

    if len(dream) < 8:
        await update.message.reply_text(
            "🌙 أرسل لي وصفاً لحلمك (8 كلمات على الأقل).\n"
            "_مثال: حلمت أنني أطير فوق السحاب وأرى البحر تحتي..._",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # فحص الحد اليومي
    can, used, limit = check_limit(user["id"], "dreams_today")
    if not can:
        plan_url = PLANS.get(user.get("plan", "free"), PLANS["basic"])["url"]
        await update.message.reply_text(
            f"⚠️ *وصلت لحد التفسيرات اليومية* ({used}/{limit})\n\n"
            "🔓 الترقية للاحترافي: تفسيرات *غير محدودة*!",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 ترقية الآن", url=PLANS["pro"]["url"])],
                [InlineKeyboardButton("🔄 حاول غداً",  callback_data="back_main")],
            ])
        )
        return

    # إرسال رسالة انتظار
    msg = await update.message.reply_text("🔮 *جاري تحليل رموز حلمك...*", parse_mode=ParseMode.MARKDOWN)
    await update.message.chat.send_action(ChatAction.TYPING)

    # استدعاء Gemini
    prompt       = build_dream_prompt(dream)
    result       = call_gemini(prompt)

    if result == "RATE_LIMITED":
        await msg.edit_text(
            "⚠️ *وصل Gemini للحد اليومي المجاني*\n\n"
            "سيعود الخدمة خلال بضع ساعات. "
            "للاستخدام غير المحدود، قم بترقية اشتراكك.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=kb_plans()
        )
        return

    await msg.delete()
    await update.message.reply_text(result, parse_mode=ParseMode.MARKDOWN)

    # تحديث العداد
    inc_field(user["id"], "dreams_today", "dreams")

    # عرض زر الصورة
    can_img, used_img, img_limit = check_limit(user["id"], "images_today")
    if can_img:
        await update.message.reply_text(
            "✨ هل تريد توليد صورة 4K من حلمك؟",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎨 توليد صورة 4K", callback_data=f"gen_img:{dream[:90]}")],
                [InlineKeyboardButton("🌙 حلم جديد",  callback_data="do_dream"),
                 InlineKeyboardButton("🔙 الرئيسية",   callback_data="back_main")],
            ])
        )
    else:
        await update.message.reply_text(
            f"⚠️ وصلت لحد الصور اليومية ({used_img}/{img_limit})",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 صور غير محدودة", url=PLANS["pro"]["url"])],
            ])
        )


# ─────────────────────────────────────────────────
# 🎛️ معالج الأزرار (Callback)
# ─────────────────────────────────────────────────

async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user  = upsert_user(update.effective_user)
    data  = query.data

    # ── توليد صورة من حلم ──
    if data.startswith("gen_img:") or data.startswith("retry_img:"):
        dream_text = data.split(":", 1)[1]
        ctx.user_data["pending_dream"] = dream_text

        can_img, used_img, img_limit = check_limit(user["id"], "images_today")
        if not can_img:
            await query.edit_message_text(
                f"⚠️ *حد الصور اليومي* ({used_img}/{img_limit})",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💎 ترقية للصور اللامحدودة", url=PLANS["pro"]["url"])],
                ])
            )
            return

        await query.edit_message_text(
            "🎨 *جاري توليد صورة 4K من حلمك...*\n"
            "قد يستغرق ذلك 15-30 ثانية ⏳",
            parse_mode=ParseMode.MARKDOWN
        )

        # ترجمة للإنجليزية ثم توليد
        en_prompt = translate_for_image(dream_text)
        img_bytes = generate_image(en_prompt + ", dreamlike surrealism, ethereal light, 4K cinematic")

        if img_bytes:
            await query.message.reply_photo(
                photo=img_bytes,
                caption=(
                    "🎨 *صورة حلمك*\n"
                    "_Powered by Stable Diffusion — Weaver نَسَّاج_"
                ),
                parse_mode=ParseMode.MARKDOWN
            )
            await query.delete_message()
            inc_field(user["id"], "images_today", "images")
        else:
            await query.edit_message_text(
                "⚠️ *فشل توليد الصورة*\n\n"
                "السيرفر مزدحم حالياً. اضغط إعادة المحاولة.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=kb_retry_image(dream_text)
            )

    elif data == "do_dream":
        await query.edit_message_text(
            "🌙 *أرسل لي حلمك الآن:*\n\n"
            "_مثال: حلمت أنني أطير فوق البحر وأرى جزراً خضراء..._",
            parse_mode=ParseMode.MARKDOWN
        )

    elif data == "do_image":
        await query.edit_message_text(
            "🎨 *أرسل وصف الصورة بالعربية أو الإنجليزية:*\n\n"
            "_مثال: غابة سحرية في ليل مضيء بالنجوم..._",
            parse_mode=ParseMode.MARKDOWN
        )
        ctx.user_data["direct_image"] = True

    elif data == "show_plans":
        text = (
            "💎 *خطط Weaver*\n\n"
            "🥉 *أساسي $4.99* — 5 تفسيرات + 3 صور/يوم\n"
            "🥇 *احترافي $9.99* — ∞ تفسيرات + ∞ صور 4K\n"
            "👥 *فريق $19.99* — كل شيء + فيديو + API"
        )
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb_plans())

    elif data == "my_stats":
        plan = PLANS.get(user.get("plan", "free"), {"name": "مجاني"})
        text = (
            "📊 *إحصائياتك*\n\n"
            f"📋 الخطة: *{plan['name']}*\n"
            f"🌙 أحلام اليوم: *{user.get('dreams_today', 0)}*\n"
            f"🎨 صور اليوم: *{user.get('images_today', 0)}*\n"
            f"🔮 إجمالي الأحلام: *{user.get('total_dreams', 0)}*"
        )
        await query.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]])
        )

    elif data == "show_help":
        text = (
            "❓ *مساعدة Weaver*\n\n"
            "أرسل حلمك نصاً مباشرة للتفسير الفوري.\n\n"
            "الأوامر:\n"
            "• `/start` — الرئيسية\n"
            "• `/stats` — إحصائياتك\n"
            "• `/plans` — الاشتراكات\n\n"
            "الموقع: aidreamweaver.store"
        )
        await query.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]])
        )

    elif data == "back_main":
        name = update.effective_user.first_name or "صديقي"
        await query.edit_message_text(
            f"🌙 *Weaver | نَسَّاج* — أهلاً *{name}*\n\nأرسل حلمك أو اختر:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=kb_main()
        )


# ─────────────────────────────────────────────────
# 👑 أوامر المسؤول
# ─────────────────────────────────────────────────

def admin_only(func):
    """Decorator للتحقق من صلاحيات المسؤول."""
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ADMIN_USER_ID:
            await update.message.reply_text("⛔ هذا الأمر للمسؤول فقط.")
            return
        return await func(update, ctx)
    wrapper.__name__ = func.__name__
    return wrapper


@admin_only
async def cmd_genimage(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """توليد صورة من وصف إنجليزي مباشر."""
    if not ctx.args:
        return await update.message.reply_text(
            "الاستخدام: `/genimage [English prompt]`",
            parse_mode=ParseMode.MARKDOWN
        )
    prompt = " ".join(ctx.args)
    msg    = await update.message.reply_text(f"🎨 *توليد صورة...*\n`{prompt[:80]}`", parse_mode=ParseMode.MARKDOWN)
    await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)

    img = generate_image(prompt)
    if img:
        await update.message.reply_photo(photo=img, caption=f"✨ `{prompt[:100]}`", parse_mode=ParseMode.MARKDOWN)
        await msg.delete()
    else:
        await msg.edit_text(
            "⚠️ فشل توليد الصورة من جميع المزودين.\n"
            "تحقق من SILICONFLOW_API_KEY أو انتظر دقيقة."
        )


@admin_only
async def cmd_auto(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """ترجمة وصف عربي تلقائياً ثم توليد صورة."""
    if not ctx.args:
        return await update.message.reply_text(
            "الاستخدام: `/auto [وصف عربي]`",
            parse_mode=ParseMode.MARKDOWN
        )
    arabic = " ".join(ctx.args)
    msg    = await update.message.reply_text("🔄 *ترجمة الوصف...*", parse_mode=ParseMode.MARKDOWN)
    en     = translate_for_image(arabic)
    await msg.edit_text(f"🎨 *توليد الصورة...*\n`{en[:100]}`", parse_mode=ParseMode.MARKDOWN)
    await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)

    img = generate_image(en)
    if img:
        await update.message.reply_photo(
            photo=img,
            caption=f"🌙 *{arabic[:80]}*\n\n`{en[:100]}`",
            parse_mode=ParseMode.MARKDOWN
        )
        await msg.delete()
    else:
        await msg.edit_text("⚠️ فشل توليد الصورة. حاول مرة أخرى.")


@admin_only
async def cmd_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """تقرير مفصل عن حلم."""
    if not ctx.args:
        return await update.message.reply_text(
            "الاستخدام: `/report [وصف الحلم]`",
            parse_mode=ParseMode.MARKDOWN
        )
    dream  = " ".join(ctx.args)
    msg    = await update.message.reply_text("📝 *جاري كتابة التقرير...*", parse_mode=ParseMode.MARKDOWN)
    await update.message.chat.send_action(ChatAction.TYPING)

    prompt = f"""اكتب تقريراً تفصيلياً منظماً عن هذا الحلم:

الحلم: {dream}

الهيكل:
═══════════════════
📋 ملخص الحلم
═══════════════════
[جملتان]

🏛️ الخلفية الثقافية
═══════════════════
[معلومات ثقافية عن الرموز الرئيسية]

🔮 تحليل الرموز
═══════════════════
[كل رمز مهم + معناه]

✨ التفسير الشامل
═══════════════════
[تفسير كامل متكامل]

💡 التوجيهات العملية
═══════════════════
[نصائح مبنية على التفسير]

📿 الجانب الروحي
═══════════════════
[آيات أو أحاديث ذات صلة إن وجدت]

⚠️ ملاحظة: للاستئناس وليس فتوى."""

    result = call_gemini(prompt, temperature=0.7)
    await msg.delete()

    # تقسيم إذا طال النص
    if len(result) > 4000:
        for chunk in [result[i:i+4000] for i in range(0, len(result), 4000)]:
            await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(result, parse_mode=ParseMode.MARKDOWN)

    data = load_leads()
    data["articles"] = data.get("articles", 0) + 1
    save_leads(data)


@admin_only
async def cmd_article(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """كتابة مقالة ثقافية عن موضوع."""
    if not ctx.args:
        return await update.message.reply_text(
            "الاستخدام: `/article [موضوع]`",
            parse_mode=ParseMode.MARKDOWN
        )
    topic = " ".join(ctx.args)
    msg   = await update.message.reply_text(
        f"✍️ *كتابة مقالة: {topic}*\nقد يستغرق 20-30 ثانية...",
        parse_mode=ParseMode.MARKDOWN
    )
    await update.message.chat.send_action(ChatAction.TYPING)

    prompt = f"""اكتب مقالة ثقافية احترافية عن: {topic}

المتطلبات:
- باللغة العربية الفصيحة
- معلومات تاريخية وثقافية موثوقة
- مرتبطة بتفسير الأحلام وتراث ابن سيرين
- منظمة بعناوين فرعية واضحة
- 600-900 كلمة
- أسلوب أكاديمي-صحفي راقٍ"""

    result = call_gemini(prompt, temperature=0.8)
    await msg.delete()

    if len(result) > 4000:
        for chunk in [result[i:i+4000] for i in range(0, len(result), 4000)]:
            await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(result, parse_mode=ParseMode.MARKDOWN)

    data = load_leads()
    data["articles"] = data.get("articles", 0) + 1
    save_leads(data)


@admin_only
async def cmd_astats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """إحصائيات مفصلة للمسؤول."""
    data  = load_leads()
    users = data.get("users", [])
    today = datetime.now().date().isoformat()

    plans_count   = {"free": 0, "basic": 0, "pro": 0, "team": 0}
    active_today  = 0
    for u in users:
        plans_count[u.get("plan", "free")] = plans_count.get(u.get("plan", "free"), 0) + 1
        if u.get("last_seen", "")[:10] == today:
            active_today += 1

    text = (
        "👑 *إحصائيات المسؤول*\n\n"
        f"📅 التاريخ: {today}\n\n"
        "👥 *المستخدمون:*\n"
        f"• الإجمالي: {len(users)}\n"
        f"• نشطون اليوم: {active_today}\n"
        f"• مجاني: {plans_count.get('free',0)}\n"
        f"• أساسي: {plans_count.get('basic',0)}\n"
        f"• احترافي: {plans_count.get('pro',0)}\n"
        f"• فريق: {plans_count.get('team',0)}\n\n"
        "📊 *النشاط:*\n"
        f"• أحلام فُسِّرت: {data.get('dreams',0)}\n"
        f"• صور وُلِّدت: {data.get('images',0)}\n"
        f"• مقالات كُتبت: {data.get('articles',0)}\n\n"
        "🔑 *الخدمات:*\n"
        f"• Gemini: {'✅' if GEMINI_API_KEY else '❌'}\n"
        f"• SiliconFlow: {'✅' if SILICONFLOW_API_KEY else '⚠️ غير موجود'}\n"
        "• Pollinations: ✅ (مجاني)\n\n"
        "*آخر 5 مستخدمين:*"
    )
    recent = sorted(users, key=lambda u: u.get("joined", ""), reverse=True)[:5]
    for u in recent:
        plan_badge = "👑" if u.get("plan") == "admin" else "💎" if u.get("plan") in ("pro","team") else "🥉" if u.get("plan") == "basic" else "🆓"
        text += f"\n• {plan_badge} `{u['id']}` @{u.get('username','N/A')} — {u.get('plan','free')}"

    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


@admin_only
async def cmd_ahelp(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = (
        "👑 *أوامر المسؤول*\n\n"
        "🎨 *الصور:*\n"
        "• `/genimage [prompt]` — توليد من وصف إنجليزي\n"
        "• `/auto [وصف عربي]` — ترجمة + توليد\n\n"
        "📝 *المحتوى:*\n"
        "• `/report [حلم]` — تقرير مفصل\n"
        "• `/article [موضوع]` — مقالة ثقافية\n\n"
        "📊 *الإدارة:*\n"
        "• `/astats` — إحصائيات مفصلة\n"
        "• `/setplan [id] [plan]` — تعيين خطة\n"
        "• `/resetlimits` — إعادة الحدود لجميع المستخدمين\n"
        "• `/resetlimits [id]` — إعادة حدود مستخدم\n"
        "• `/broadcast [رسالة]` — إشعار جماعي"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


@admin_only
async def cmd_setplan(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if len(ctx.args) < 2:
        return await update.message.reply_text(
            "الاستخدام: `/setplan [user_id] [free/basic/pro/team]`",
            parse_mode=ParseMode.MARKDOWN
        )
    try:
        target = int(ctx.args[0])
        plan   = ctx.args[1].lower()
        if plan not in ("free", "basic", "pro", "team"):
            return await update.message.reply_text("❌ الخطط: free, basic, pro, team")
        data = load_leads()
        for u in data["users"]:
            if int(u["id"]) == target:
                u["plan"] = plan
                save_leads(data)
                return await update.message.reply_text(
                    f"✅ خطة *{plan}* → `{target}`", parse_mode=ParseMode.MARKDOWN
                )
        await update.message.reply_text(f"❌ المستخدم `{target}` غير موجود", parse_mode=ParseMode.MARKDOWN)
    except ValueError:
        await update.message.reply_text("❌ user_id يجب أن يكون رقماً")


@admin_only
async def cmd_resetlimits(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data  = load_leads()
    today = datetime.now().date().isoformat()

    if not ctx.args or ctx.args[0] == "all":
        for u in data["users"]:
            u["dreams_today"] = 0
            u["images_today"] = 0
            u["last_reset"]   = today
        save_leads(data)
        await update.message.reply_text(
            f"✅ تم إعادة ضبط الحدود لـ *{len(data['users'])}* مستخدم",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        try:
            target = int(ctx.args[0])
            for u in data["users"]:
                if int(u["id"]) == target:
                    u["dreams_today"] = 0
                    u["images_today"] = 0
                    u["last_reset"]   = today
                    save_leads(data)
                    return await update.message.reply_text(
                        f"✅ تم إعادة ضبط حدود `{target}`", parse_mode=ParseMode.MARKDOWN
                    )
            await update.message.reply_text(f"❌ المستخدم `{target}` غير موجود", parse_mode=ParseMode.MARKDOWN)
        except ValueError:
            await update.message.reply_text("الاستخدام: `/resetlimits` أو `/resetlimits [user_id]`", parse_mode=ParseMode.MARKDOWN)


@admin_only
async def cmd_broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        return await update.message.reply_text(
            "الاستخدام: `/broadcast [الرسالة]`", parse_mode=ParseMode.MARKDOWN
        )
    message = " ".join(ctx.args)
    users   = load_leads().get("users", [])
    msg     = await update.message.reply_text(
        f"📢 *إرسال لـ {len(users)} مستخدم...*", parse_mode=ParseMode.MARKDOWN
    )
    sent = failed = 0
    for u in users:
        try:
            await ctx.bot.send_message(
                chat_id=int(u["id"]),
                text=f"📢 *إشعار من Weaver*\n\n{message}",
                parse_mode=ParseMode.MARKDOWN
            )
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1
    await msg.edit_text(
        f"✅ *تم الإرسال*\n• نجح: {sent}\n• فشل: {failed}",
        parse_mode=ParseMode.MARKDOWN
    )


# ─────────────────────────────────────────────────
# ⚠️ معالج الأخطاء
# ─────────────────────────────────────────────────

async def error_handler(update: object, ctx: ContextTypes.DEFAULT_TYPE):
    log.error(f"Error: {ctx.error}")
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ حدث خطأ مؤقت. حاول مرة أخرى."
            )
        except Exception:
            pass


# ─────────────────────────────────────────────────
# 🚀 التشغيل
# ─────────────────────────────────────────────────

def main():
    print("🧵 Weaver | نَسَّاج Bot v3.0 — Starting...")
    print(f"   Gemini:       {'✅' if GEMINI_API_KEY      else '❌ مفقود'}")
    print(f"   Imagen 3:     {'✅ (نفس مفتاح Gemini)' if GEMINI_API_KEY else '❌'}")
    print(f"   SiliconFlow:  {'✅' if SILICONFLOW_API_KEY else '⚠️  اختياري'}")
    print(f"   Pollinations: ✅ (احتياطي أخير)")
    print(f"   Admin ID:     {ADMIN_USER_ID}")

    # تهيئة leads.json
    if not Path(LEADS_FILE).exists():
        save_leads({"total_users": 0, "users": [], "dreams": 0, "images": 0, "articles": 0})
        print(f"   Created {LEADS_FILE}")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # أوامر المستخدم
    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("help",   cmd_help))
    app.add_handler(CommandHandler("stats",  cmd_stats))
    app.add_handler(CommandHandler("plans",  cmd_plans))

    # أوامر المسؤول
    app.add_handler(CommandHandler("genimage",    cmd_genimage))
    app.add_handler(CommandHandler("auto",         cmd_auto))
    app.add_handler(CommandHandler("report",       cmd_report))
    app.add_handler(CommandHandler("article",      cmd_article))
    app.add_handler(CommandHandler("astats",       cmd_astats))
    app.add_handler(CommandHandler("ahelp",        cmd_ahelp))
    app.add_handler(CommandHandler("setplan",      cmd_setplan))
    app.add_handler(CommandHandler("resetlimits",  cmd_resetlimits))
    app.add_handler(CommandHandler("broadcast",    cmd_broadcast))

    # أزرار inline
    app.add_handler(CallbackQueryHandler(handle_callback))

    # الرسائل النصية (التفسير الرئيسي)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # معالج الأخطاء
    app.add_error_handler(error_handler)

    print("✅ البوت يعمل! اضغط Ctrl+C للإيقاف.\n")
    app.run_polling(
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
