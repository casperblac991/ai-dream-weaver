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

# استيراد نظام توليد الصور المتعدد
try:
    from image_generators import ImageGenerator, generate_image
    IMAGE_SYSTEM_AVAILABLE = True
except ImportError:
    IMAGE_SYSTEM_AVAILABLE = False
    print("⚠️ نظام الصور المتعدد غير موجود. استخدم image_generators.py")

# ─────────────────────────────────────────────────
# ⚙️ الإعدادات
# ─────────────────────────────────────────────────

# تحميل المتغيرات البيئية
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TELEGRAM_TOKEN = os.environ.get("telegram_token", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
SILICONFLOW_API_KEY = os.environ.get("SILICONFLOW_API_KEY", "")
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", "6790340715"))

if not TELEGRAM_TOKEN:
    print("❌ خطأ فادح: TELEGRAM_TOKEN غير موجود!")
    exit(1)

# ─────────────────────────────────────────────────
# 🤖 نظام توليد الصور المتعدد
# ─────────────────────────────────────────────────

# إنشاء كائن توليد الصور
if IMAGE_SYSTEM_AVAILABLE:
    image_generator = ImageGenerator(
        gemini_api_key=GEMINI_API_KEY,
        siliconflow_api_key=SILICONFLOW_API_KEY
    )
    print("✅ نظام الصور المتعدد جاهز (5 مزودين مجانيين)")
else:
    image_generator = None
    print("⚠️ نظام الصور المتعدد غير متاح")

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
    """
    توليد صورة باستخدام النظام المتعدد (5 مزودين مجانيين)
    """
    if not image_generator:
        log.error("نظام الصور غير متاح")
        return None
    
    try:
        # تشغيل التوليد في Thread منفصل حتى لا نعطل البوت
        loop = asyncio.get_event_loop()
        img_bytes = await loop.run_in_executor(
            None, 
            lambda: image_generator.generate(prompt)
        )
        return img_bytes
    except Exception as e:
        log.error(f"generate_dream_image: {e}")
        return None

# ─────────────────────────────────────────────────
# ⌨️ لوحات المفاتيح
# ─────────────────────────────────────────────────

def kb_main():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌙 فسّر حلمي", callback_data="do_dream"),
         InlineKeyboardButton("🎨 صورة 4K", callback_data="do_image")],
        [InlineKeyboardButton("💎 الاشتراكات", callback_data="show_plans"),
         InlineKeyboardButton("📊 إحصائياتي", callback_data="my_stats")],
        [InlineKeyboardButton("🌐 الموقع", url="https://aidreamweaver.store"),
         InlineKeyboardButton("❓ مساعدة", callback_data="show_help")],
    ])

def kb_plans():
    PLANS_URL = {
        "basic": "https://casperblac.gumroad.com/l/dtiobz",
        "pro": "https://casperblac.gumroad.com/l/byqzxd",
        "team": "https://casperblac.gumroad.com/l/hiulqi",
    }
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🥉 أساسي — $4.99/شهر", url=PLANS_URL["basic"])],
        [InlineKeyboardButton("🥇 احترافي — $9.99/شهر", url=PLANS_URL["pro"])],
        [InlineKeyboardButton("👥 فريق — $19.99/شهر", url=PLANS_URL["team"])],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")],
    ])

def kb_retry_image(dream_text: str):
    short = dream_text[:80]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 إعادة المحاولة", callback_data=f"retry_img:{short}")],
        [InlineKeyboardButton("🔙 الرئيسية", callback_data="back_main")],
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
        "✨ أستخدم 5 مزودين مجانيين لتوليد الصور (felo.ai, Pollinations, وغيرها)\n"
        "🔮 أستخدم Gemini 2.0 Flash لتفسير الأحلام بمنهجية ابن سيرين\n\n"
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
    text = (
        "📊 *إحصائياتك*\n\n"
        f"👤 خطتك: *{user.get('plan', 'مجاني').capitalize()}*\n"
        f"🌙 أحلام اليوم: *{user.get('dreams_today', 0)}*\n"
        f"🎨 صور اليوم: *{user.get('images_today', 0)}*\n"
        f"🔮 إجمالي الأحلام: *{user.get('total_dreams', 0)}*\n"
        f"🖼️ إجمالي الصور: *{user.get('total_images', 0)}*\n\n"
        f"👥 مستخدمو المنصة: *{data.get('total_users', 0)}*"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def cmd_plans(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    upsert_user(update.effective_user)
    text = (
        "💎 *خطط Weaver | نَسَّاج*\n\n"
        "🥉 *أساسي — $4.99/شهر*\n"
        "• 5 تفسيرات + 3 صور يومياً\n\n"
        "🥇 *احترافي — $9.99/شهر*\n"
        "• تفسيرات + صور 4K غير محدودة ✨\n\n"
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
            "_مثال: حلمت أنني أطير فوق السحاب..._",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    can, used, limit = check_limit(user["id"], "dreams_today")
    if not can:
        await update.message.reply_text(
            f"⚠️ *وصلت لحد التفسيرات اليومية* ({used}/{limit})\n\n"
            "🔓 الترقية للاحترافي: تفسيرات *غير محدودة*!",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 ترقية الآن", url="https://casperblac.gumroad.com/l/byqzxd")],
            ])
        )
        return

    msg = await update.message.reply_text("🔮 *جاري تحليل رموز حلمك...*", parse_mode=ParseMode.MARKDOWN)
    await update.message.chat.send_action(ChatAction.TYPING)

    prompt = build_dream_prompt(dream)
    result = call_gemini(prompt)

    if result == "RATE_LIMITED":
        await msg.edit_text(
            "⚠️ *وصل Gemini للحد اليومي المجاني*\n\nسيعود الخدمة خلال بضع ساعات.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=kb_plans()
        )
        return

    await msg.delete()
    await update.message.reply_text(result, parse_mode=ParseMode.MARKDOWN)
    inc_field(user["id"], "dreams_today", "dreams")

    can_img, used_img, img_limit = check_limit(user["id"], "images_today")
    if can_img:
        await update.message.reply_text(
            "✨ هل تريد توليد صورة 4K من حلمك؟",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎨 توليد صورة 4K", callback_data=f"gen_img:{dream[:90]}")],
                [InlineKeyboardButton("🌙 حلم جديد", callback_data="do_dream"),
                 InlineKeyboardButton("🔙 الرئيسية", callback_data="back_main")],
            ])
        )

# ─────────────────────────────────────────────────
# 🎛️ معالج الأزرار (Callback)
# ─────────────────────────────────────────────────

async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = upsert_user(update.effective_user)
    data = query.data

    if data.startswith("gen_img:") or data.startswith("retry_img:"):
        dream_text = data.split(":", 1)[1]
        ctx.user_data["pending_dream"] = dream_text

        can_img, used_img, img_limit = check_limit(user["id"], "images_today")
        if not can_img:
            await query.edit_message_text(
                f"⚠️ *حد الصور اليومي* ({used_img}/{img_limit})",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💎 ترقية للصور اللامحدودة", url="https://casperblac.gumroad.com/l/byqzxd")],
                ])
            )
            return

        await query.edit_message_text(
            "🎨 *جاري توليد صورة 4K من حلمك...*\n"
            "قد يستغرق ذلك 15-30 ثانية ⏳",
            parse_mode=ParseMode.MARKDOWN
        )

        en_prompt = translate_for_image(dream_text)
        img_bytes = await generate_dream_image(en_prompt + ", dreamlike surrealism, ethereal light, 4K cinematic")

        if img_bytes:
            await query.message.reply_photo(
                photo=img_bytes,
                caption="🎨 *صورة حلمك*\n_Powered by 5 free AI image generators — Weaver نَسَّاج_",
                parse_mode=ParseMode.MARKDOWN
            )
            await query.delete_message()
            inc_field(user["id"], "images_today", "images")
            
            # طباعة إحصائيات المزودين كل 10 صور
            if user.get("total_images", 0) % 10 == 0 and image_generator:
                image_generator.print_stats()
        else:
            await query.edit_message_text(
                "⚠️ *فشل توليد الصورة*\n\nجميع المزودين الخمسة لم يستجيبوا. حاول مرة أخرى.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=kb_retry_image(dream_text)
            )

    elif data == "do_dream":
        await query.edit_message_text(
            "🌙 *أرسل لي حلمك الآن:*\n\n"
            "_مثال: حلمت أنني أطير فوق البحر..._",
            parse_mode=ParseMode.MARKDOWN
        )

    elif data == "do_image":
        await query.edit_message_text(
            "🎨 *أرسل وصف الصورة بالعربية أو الإنجليزية:*\n\n"
            "_مثال: غابة سحرية في ليل مضيء..._",
            parse_mode=ParseMode.MARKDOWN
        )
        ctx.user_data["direct_image"] = True

    elif data == "show_plans":
        await query.edit_message_text(
            "💎 *خطط Weaver*\n\n"
            "🥉 *أساسي $4.99* — 5 تفسيرات + 3 صور/يوم\n"
            "🥇 *احترافي $9.99* — ∞ تفسيرات + ∞ صور 4K\n"
            "👥 *فريق $19.99* — كل شيء + فيديو + API",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=kb_plans()
        )

    elif data == "my_stats":
        text = (
            "📊 *إحصائياتك*\n\n"
            f"📋 خطتك: *{user.get('plan', 'مجاني').capitalize()}*\n"
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
            "✨ *ميزة الصور:* 5 مزودين مجانيين (felo.ai، Pollinations، وغيرها)"
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
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ADMIN_USER_ID:
            await update.message.reply_text("⛔ هذا الأمر للمسؤول فقط.")
            return
        return await func(update, ctx)
    return wrapper

@admin_only
async def cmd_genimage(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        return await update.message.reply_text("الاستخدام: `/genimage [English prompt]`", parse_mode=ParseMode.MARKDOWN)
    prompt = " ".join(ctx.args)
    msg = await update.message.reply_text(f"🎨 *توليد صورة...*\n`{prompt[:80]}`", parse_mode=ParseMode.MARKDOWN)
    
    img_bytes = await generate_dream_image(prompt)
    if img_bytes:
        await update.message.reply_photo(photo=img_bytes, caption=f"✨ `{prompt[:100]}`", parse_mode=ParseMode.MARKDOWN)
        await msg.delete()
    else:
        await msg.edit_text("⚠️ فشل توليد الصورة من جميع المزودين الخمسة.")

@admin_only
async def cmd_auto(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        return await update.message.reply_text("الاستخدام: `/auto [وصف عربي]`", parse_mode=ParseMode.MARKDOWN)
    arabic = " ".join(ctx.args)
    msg = await update.message.reply_text("🔄 *ترجمة الوصف...*", parse_mode=ParseMode.MARKDOWN)
    en = translate_for_image(arabic)
    await msg.edit_text(f"🎨 *توليد الصورة...*\n`{en[:100]}`", parse_mode=ParseMode.MARKDOWN)
    
    img_bytes = await generate_dream_image(en)
    if img_bytes:
        await update.message.reply_photo(
            photo=img_bytes,
            caption=f"🌙 *{arabic[:80]}*\n\n`{en[:100]}`",
            parse_mode=ParseMode.MARKDOWN
        )
        await msg.delete()
    else:
        await msg.edit_text("⚠️ فشل توليد الصورة. حاول مرة أخرى.")

@admin_only
async def cmd_stats_all(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """إحصائيات شاملة مع أداء المزودين"""
    data = load_leads()
    users = data.get("users", [])
    
    text = "👑 *إحصائيات شاملة*\n\n"
    text += f"👥 إجمالي المستخدمين: {len(users)}\n"
    text += f"🌙 إجمالي الأحلام: {data.get('dreams', 0)}\n"
    text += f"🎨 إجمالي الصور: {data.get('images', 0)}\n\n"
    
    if image_generator:
        text += "*📊 أداء مزودي الصور:*\n"
        for provider, stats in image_generator.stats.items():
            total = stats["success"] + stats["fail"]
            if total > 0:
                rate = (stats["success"] / total) * 100
                text += f"• {provider}: {stats['success']} نجاح, {stats['fail']} فشل ({rate:.1f}%)\n"
    
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ─────────────────────────────────────────────────
# 🚀 التشغيل
# ─────────────────────────────────────────────────

def main():
    print("🧵 Weaver | نَسَّاج Bot v3.1 — Starting...")
    print(f"   Telegram Token: {'✅' if TELEGRAM_TOKEN else '❌'}")
    print(f"   Gemini API Key: {'✅' if GEMINI_API_KEY else '❌'}")
    print(f"   SiliconFlow Key: {'✅' if SILICONFLOW_API_KEY else '⚠️ اختياري'}")
    print(f"   Image System: {'✅ (5 مزودين مجانيين)' if IMAGE_SYSTEM_AVAILABLE else '❌'}")
    print(f"   Admin ID: {ADMIN_USER_ID}")

    if not Path(LEADS_FILE).exists():
        save_leads({"total_users": 0, "users": [], "dreams": 0, "images": 0, "articles": 0})
        print(f"   Created {LEADS_FILE}")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # أوامر المستخدم
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("plans", cmd_plans))

    # أوامر المسؤول
    app.add_handler(CommandHandler("genimage", cmd_genimage))
    app.add_handler(CommandHandler("auto", cmd_auto))
    app.add_handler(CommandHandler("statsall", cmd_stats_all))

    # أزرار ورسائل
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ البوت يعمل! اضغط Ctrl+C للإيقاف.\n")
    app.run_polling(
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()
