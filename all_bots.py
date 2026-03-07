"""
╔══════════════════════════════════════════════════════════════╗
║          🧵 Weaver | نَسَّاج — Telegram Dream Bot             ║
║       AI Dream Interpretation + 4K Image Generation          ║
║       Version 2.0 — March 2026                               ║
╚══════════════════════════════════════════════════════════════╝

Environment Variables Required:
  TELEGRAM_TOKEN     — from @BotFather
  GEMINI_API_KEY     — from https://aistudio.google.com
  SILICONFLOW_API_KEY — from https://cloud.siliconflow.cn
  ADMIN_USER_ID      — your Telegram numeric user ID

Deploy: python all_bots.py
"""

import os
import json
import asyncio
import logging
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)
from telegram.constants import ParseMode, ChatAction

# ─────────────────────────────────────────
# CONFIG & LOGGING
# ─────────────────────────────────────────
load_dotenv()

TELEGRAM_TOKEN      = os.getenv("TELEGRAM_TOKEN", "")
GEMINI_API_KEY      = os.getenv("GEMINI_API_KEY", "")
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
ADMIN_USER_ID       = int(os.getenv("ADMIN_USER_ID", "0"))

LEADS_FILE  = "leads.json"
GEMINI_URL  = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
SF_URL      = "https://api.siliconflow.cn/v1/images/generations"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("weaver.log", encoding="utf-8")
    ]
)
log = logging.getLogger(__name__)

# Subscription plans (Gumroad links)
PLANS = {
    "basic": {
        "name_ar": "أساسي",
        "name_en": "Basic",
        "price": "$4.99/mo",
        "url": "https://casperblac.gumroad.com/l/dtiobz",
        "daily_dreams": 5,
        "daily_images": 3,
    },
    "pro": {
        "name_ar": "احترافي",
        "name_en": "Pro",
        "price": "$9.99/mo",
        "url": "https://casperblac.gumroad.com/l/byqzxd",
        "daily_dreams": 9999,
        "daily_images": 9999,
    },
    "team": {
        "name_ar": "فريق",
        "name_en": "Team",
        "price": "$19.99/mo",
        "url": "https://casperblac.gumroad.com/l/hiulqi",
        "daily_dreams": 9999,
        "daily_images": 9999,
    },
}

# ─────────────────────────────────────────
# LEADS / DATA MANAGEMENT
# ─────────────────────────────────────────
def load_leads() -> dict:
    default = {"total_users": 0, "users": [], "dreams": 0, "images": 0, "articles": 0}
    try:
        if Path(LEADS_FILE).exists():
            return json.loads(Path(LEADS_FILE).read_text(encoding="utf-8"))
    except Exception as e:
        log.error(f"load_leads error: {e}")
    return default


def save_leads(data: dict) -> None:
    try:
        Path(LEADS_FILE).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        log.error(f"save_leads error: {e}")


def get_user(user_id: int) -> dict | None:
    data = load_leads()
    for u in data["users"]:
        if u["id"] == user_id:
            return u
    return None


def upsert_user(update: Update) -> dict:
    tg = update.effective_user
    data = load_leads()
    for u in data["users"]:
        if u["id"] == tg.id:
            u["last_seen"] = datetime.now().isoformat()
            u["username"] = tg.username or u.get("username", "")
            u["name"] = tg.full_name or u.get("name", "")
            save_leads(data)
            return u
    # New user
    new_user = {
        "id": tg.id,
        "username": tg.username or "",
        "name": tg.full_name or "",
        "joined": datetime.now().isoformat(),
        "last_seen": datetime.now().isoformat(),
        "plan": "free",
        "dreams_today": 0,
        "images_today": 0,
        "last_reset": datetime.now().date().isoformat(),
        "total_dreams": 0,
        "total_images": 0,
        "lang": "ar",
    }
    data["users"].append(new_user)
    data["total_users"] = len(data["users"])
    save_leads(data)
    log.info(f"New user: {tg.id} (@{tg.username})")
    return new_user


def increment_stat(user_id: int, field: str, global_field: str = None) -> None:
    data = load_leads()
    for u in data["users"]:
        if u["id"] == user_id:
            # Reset daily counters if new day
            today = datetime.now().date().isoformat()
            if u.get("last_reset") != today:
                u["dreams_today"] = 0
                u["images_today"] = 0
                u["last_reset"] = today
            u[field] = u.get(field, 0) + 1
            break
    if global_field:
        data[global_field] = data.get(global_field, 0) + 1
    save_leads(data)


def check_daily_limit(user_id: int, limit_field: str) -> tuple[bool, int, int]:
    """Returns (can_use, used_today, limit)"""
    user = get_user(user_id)
    if not user:
        return True, 0, 5

    # Reset if new day
    today = datetime.now().date().isoformat()
    if user.get("last_reset") != today:
        user["dreams_today"] = 0
        user["images_today"] = 0

    plan = PLANS.get(user.get("plan", "free"), PLANS["basic"])
    used = user.get(limit_field, 0)
    limit_key = "daily_dreams" if limit_field == "dreams_today" else "daily_images"
    limit = plan.get(limit_key, 5) if user.get("plan") != "free" else (5 if limit_field == "dreams_today" else 2)

    return used < limit, used, limit


# ─────────────────────────────────────────
# AI FUNCTIONS
# ─────────────────────────────────────────
def call_gemini(prompt: str, temperature: float = 0.7) -> str:
    """Call Google Gemini API and return text response."""
    try:
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 1500,
                "topP": 0.9,
            }
        }
        resp = requests.post(
            GEMINI_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except requests.exceptions.Timeout:
        return "⚠️ انتهت مهلة الاتصال. حاول مرة أخرى."
    except Exception as e:
        log.error(f"Gemini error: {e}")
        return f"⚠️ خطأ في الاتصال بـ Gemini: {str(e)[:100]}"


def interpret_dream(dream_text: str, lang: str = "ar") -> str:
    """Generate dream interpretation using Gemini + Ibn Sirin methodology."""
    if lang == "ar":
        prompt = f"""أنت نظام تفسير أحلام متخصص يجمع بين منهجية الإمام ابن سيرين (654-728م) والذكاء الاصطناعي الحديث.

قواعد التفسير:
- اتبع منهجية ابن سيرين في مراعاة السياق وحال الحالم وتوقيت الحلم
- فرّق بين الرؤيا الصادقة والحلم العادي
- استخدم رمزية القرآن الكريم واللغة العربية في التفسير
- قدّم تفسيراً متكاملاً وعملياً

الحلم المُقدَّم:
{dream_text}

اكتب تفسيراً منظماً يشمل:
1. 🌙 **المقدمة** — الانطباع العام عن الحلم
2. 🔮 **تحليل الرموز** — أبرز الرموز ومعانيها
3. ✨ **التفسير الكامل** — الرسالة الكاملة للحلم
4. 💡 **التوجيه** — ما يُنصح به الحالم
5. 📿 **الختام** — ملاحظة دينية أو روحية

اكتب بأسلوب واثق وعميق، مع الإشارة إلى أن التفسير للاستئناس وليس فتوى."""
    else:
        prompt = f"""You are a specialized dream interpretation system combining Ibn Sirin's classical Islamic methodology (654-728 CE) with modern AI.

Interpretation principles:
- Follow Ibn Sirin's contextual approach: consider the dreamer's state, timing, and life circumstances
- Distinguish between divine visions (ru'ya) and ordinary dreams (hulm)
- Apply Quranic symbolism and Arabic linguistic roots where relevant
- Deliver a layered, practical interpretation

Dream submitted:
{dream_text}

Write a structured interpretation including:
1. 🌙 **Overview** — General impression of the dream
2. 🔮 **Symbol Analysis** — Key symbols and their meanings
3. ✨ **Full Interpretation** — The complete message of the dream
4. 💡 **Guidance** — Recommended actions or reflections for the dreamer
5. 📿 **Closing Note** — Spiritual or cultural context

Write with depth and authority. Note that this is for reflection, not a religious ruling."""

    return call_gemini(prompt, temperature=0.75)


def translate_to_english(arabic_text: str) -> str:
    """Translate Arabic dream description to English for image generation."""
    prompt = f"""Translate the following Arabic dream description into vivid English for AI image generation.
Make it descriptive, atmospheric, and visual. Keep it under 120 words.
Output ONLY the English translation, nothing else.

Arabic text: {arabic_text}"""
    return call_gemini(prompt, temperature=0.5)


def generate_image_prompt(dream_text: str, style: str = "dreamlike") -> str:
    """Create an optimized image prompt from dream description."""
    styles = {
        "dreamlike": "dreamlike surrealism, glowing ethereal atmosphere, soft mystical light",
        "cinematic": "cinematic photography, dramatic lighting, 8K ultra detailed",
        "watercolor": "watercolor painting, soft brushstrokes, flowing colors",
        "fantasy": "fantasy digital art, epic scale, luminous magical atmosphere",
        "islamic": "Islamic geometric patterns, arabesque, warm gold and deep blue palette",
        "ancient": "ancient civilization aesthetic, hieroglyphic elements, timeless atmosphere",
    }
    style_desc = styles.get(style, styles["dreamlike"])

    prompt = f"""Convert this dream description into a vivid, detailed image generation prompt.
Focus on visual elements, atmosphere, colors, and mood.
Add: {style_desc}
Make it cinematic and emotionally evocative. Under 150 words.
Output ONLY the image prompt, no explanation.

Dream: {dream_text}"""
    return call_gemini(prompt, temperature=0.8)


def generate_image(prompt: str, size: str = "1024x1024") -> str | None:
    """Generate image via SiliconFlow API. Returns URL or None."""
    try:
        headers = {
            "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "stabilityai/stable-diffusion-3-5-large",
            "prompt": prompt + ", high quality, 4K, detailed",
            "negative_prompt": "blurry, low quality, distorted, ugly, text, watermark",
            "size": size,
            "num_inference_steps": 30,
            "guidance_scale": 7.5,
        }
        resp = requests.post(SF_URL, headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        return result["images"][0]["url"]
    except Exception as e:
        log.error(f"SiliconFlow error: {e}")
        return None


def write_dream_report(dream_text: str) -> str:
    """Generate a detailed structured dream report."""
    prompt = f"""اكتب تقريراً تفصيلياً ومنظماً عن الحلم التالي، يصلح للاطلاع الشخصي أو المشاركة:

الحلم: {dream_text}

هيكل التقرير:
═══════════════════════════════
📋 ملخص الحلم
═══════════════════════════════
[ملخص موجز في جملتين]

🏛️ الخلفية الثقافية والتاريخية
═══════════════════════════════
[معلومات ثقافية عن الرموز الرئيسية في الحلم]

🔮 تحليل الرموز المفصّل
═══════════════════════════════
[قائمة بكل رمز مهم ومعناه وفق ابن سيرين والنابلسي]

✨ التفسير الشامل
═══════════════════════════════
[تفسير كامل ومفصّل يجمع كل الرموز في رسالة متكاملة]

🌟 التوجيهات العملية
═══════════════════════════════
[نصائح عملية مبنية على التفسير]

📿 الجانب الروحي والديني
═══════════════════════════════
[آيات قرآنية أو أحاديث ذات صلة إن وجدت]

⚠️ ملاحظة: هذا التفسير للتأمل والاستئناس وليس فتوى دينية."""

    return call_gemini(prompt, temperature=0.7)


def write_article(topic: str) -> str:
    """Generate a cultural article about dreams."""
    prompt = f"""اكتب مقالة ثقافية احترافية وعميقة عن: {topic}

المقالة يجب أن:
- تكون باللغة العربية الفصيحة
- تتضمن معلومات تاريخية وثقافية موثوقة
- تربط الموضوع بمنصة Weaver وتفسير الأحلام بالذكاء الاصطناعي
- تكون منظمة بعناوين فرعية واضحة
- طولها 600-900 كلمة

هيكل المقالة:
1. مقدمة جذابة
2. الخلفية التاريخية/الثقافية
3. الجوانب الرئيسية والتفاصيل
4. الصلة بعلم تفسير الأحلام
5. كيف يستفيد Weaver من هذا التراث
6. خاتمة ملهمة

اكتب بأسلوب أكاديمي-صحفي راقٍ."""

    return call_gemini(prompt, temperature=0.8)


# ─────────────────────────────────────────
# KEYBOARD HELPERS
# ─────────────────────────────────────────
def main_keyboard_ar():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌙 فسّر حلماً", callback_data="start_dream"),
         InlineKeyboardButton("🎨 صورة 4K", callback_data="start_image")],
        [InlineKeyboardButton("💎 الاشتراكات", callback_data="show_plans"),
         InlineKeyboardButton("📊 إحصائياتي", callback_data="my_stats")],
        [InlineKeyboardButton("🌐 الموقع", url="https://aidreamweaver.store"),
         InlineKeyboardButton("❓ مساعدة", callback_data="help_menu")],
    ])


def plans_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🥉 أساسي — $4.99/شهر", url=PLANS["basic"]["url"])],
        [InlineKeyboardButton("🥇 احترافي — $9.99/شهر", url=PLANS["pro"]["url"])],
        [InlineKeyboardButton("👥 فريق — $19.99/شهر", url=PLANS["team"]["url"])],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")],
    ])


def style_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✨ حلمي", callback_data="style_dreamlike"),
         InlineKeyboardButton("🎬 سينمائي", callback_data="style_cinematic")],
        [InlineKeyboardButton("🎨 ألوان مائية", callback_data="style_watercolor"),
         InlineKeyboardButton("🏰 فانتازيا", callback_data="style_fantasy")],
        [InlineKeyboardButton("🕌 إسلامي", callback_data="style_islamic"),
         InlineKeyboardButton("🏛️ حضاري", callback_data="style_ancient")],
        [InlineKeyboardButton("❌ إلغاء", callback_data="cancel")],
    ])


# ─────────────────────────────────────────
# COMMAND HANDLERS
# ─────────────────────────────────────────
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = upsert_user(update)
    name = update.effective_user.first_name or "صديقي"
    welcome = f"""🌙 *أهلاً بك في Weaver | نَسَّاج* ✨

مرحباً *{name}*، أنا بوت تفسير الأحلام بالذكاء الاصطناعي.

أستطيع مساعدتك في:
🔮 *تفسير أحلامك* وفق منهجية ابن سيرين
🎨 *توليد صور 4K* مستوحاة من حلمك
📚 *معلومات ثقافية* عن عالم الأحلام

*كيف تبدأ؟*
فقط أرسل لي وصف حلمك، وسأفسره لك فوراً! 💫

أو استخدم الأزرار أدناه:"""

    await update.message.reply_text(
        welcome,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_keyboard_ar()
    )


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    upsert_user(update)
    text = """❓ *دليل استخدام Weaver*

*أوامر المستخدم:*
• `/start` — الصفحة الرئيسية
• `/help` — هذه المساعدة
• `/stats` — إحصائياتك الشخصية
• `/plans` — عرض خطط الاشتراك
• `/lang en` — تغيير اللغة للإنجليزية
• `/lang ar` — تغيير اللغة للعربية

*كيف أفسر حلمي؟*
ببساطة أرسل وصفاً لحلمك — مثال:
_"رأيت في منامي أنني أطير فوق البحر..."_

*الموقع:* aidreamweaver.store
*قناة تيليجرام:* @aidreamweaver"""

    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = upsert_user(update)
    data = load_leads()
    plan_name = user.get("plan", "free")
    plan_info = PLANS.get(plan_name, {"name_ar": "مجاني", "price": "مجاني"})

    text = f"""📊 *إحصائياتك الشخصية*

👤 *الاسم:* {user.get('name', 'غير محدد')}
📋 *الخطة:* {plan_info['name_ar']} — {plan_info['price']}
📅 *تاريخ الانضمام:* {user.get('joined', '')[:10]}

*اليوم:*
🌙 التفسيرات: {user.get('dreams_today', 0)}
🎨 الصور: {user.get('images_today', 0)}

*الإجمالي:*
🌙 كل التفسيرات: {user.get('total_dreams', 0)}
🎨 كل الصور: {user.get('total_images', 0)}

*إحصائيات المنصة:*
👥 المستخدمون: {data.get('total_users', 0)}
🔮 الأحلام المفسَّرة: {data.get('dreams', 0)}"""

    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_plans(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    upsert_user(update)
    text = """💎 *خطط Weaver | نَسَّاج*

🥉 *أساسي — $4.99/شهر*
• 5 تفسيرات يومياً
• 3 صور يومياً
• جميع الأساليب الفنية

🥇 *احترافي — $9.99/شهر*
• تفسيرات غير محدودة ✨
• صور 4K غير محدودة 🎨
• 50 أسلوب فني
• أولوية في المعالجة

👥 *فريق — $19.99/شهر/مستخدم*
• كل مميزات الاحترافي
• توليد فيديو 🎬
• تقارير PDF 📄
• وصول API 🔧
• دعم أولوية"""

    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=plans_keyboard()
    )


async def cmd_lang(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    upsert_user(update)
    args = ctx.args
    if not args or args[0] not in ["ar", "en"]:
        await update.message.reply_text("استخدم: `/lang ar` أو `/lang en`", parse_mode=ParseMode.MARKDOWN)
        return
    lang = args[0]
    data = load_leads()
    for u in data["users"]:
        if u["id"] == update.effective_user.id:
            u["lang"] = lang
            break
    save_leads(data)
    msg = "✅ تم تغيير اللغة إلى العربية 🇸🇦" if lang == "ar" else "✅ Language changed to English 🇬🇧"
    await update.message.reply_text(msg)


# ─────────────────────────────────────────
# ADMIN COMMANDS
# ─────────────────────────────────────────
def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_USER_ID


async def cmd_genimage(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("⛔ أوامر المسؤول فقط.")
    if not ctx.args:
        return await update.message.reply_text("الاستخدام: `/genimage [prompt in English]`", parse_mode=ParseMode.MARKDOWN)

    prompt = " ".join(ctx.args)
    await update.message.reply_text(f"🎨 *توليد صورة...*\n`{prompt[:80]}...`", parse_mode=ParseMode.MARKDOWN)
    await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)

    url = generate_image(prompt)
    if url:
        await update.message.reply_photo(photo=url, caption=f"✨ `{prompt[:100]}`", parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("❌ فشل توليد الصورة. تحقق من SILICONFLOW_API_KEY.")


async def cmd_auto(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Auto: translate Arabic description then generate image."""
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("⛔ أوامر المسؤول فقط.")
    if not ctx.args:
        return await update.message.reply_text("الاستخدام: `/auto [وصف بالعربية]`", parse_mode=ParseMode.MARKDOWN)

    arabic = " ".join(ctx.args)
    msg = await update.message.reply_text("🔄 *ترجمة الوصف...*", parse_mode=ParseMode.MARKDOWN)
    english_prompt = translate_to_english(arabic)
    await msg.edit_text(f"🎨 *توليد الصورة...*\n`{english_prompt[:100]}`", parse_mode=ParseMode.MARKDOWN)
    await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)

    url = generate_image(english_prompt)
    if url:
        await update.message.reply_photo(photo=url, caption=f"🌙 *{arabic[:80]}*\n\n`{english_prompt[:100]}`", parse_mode=ParseMode.MARKDOWN)
        await msg.delete()
    else:
        await msg.edit_text("❌ فشل توليد الصورة.")


async def cmd_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Generate detailed dream report (admin command)."""
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("⛔ أوامر المسؤول فقط.")
    if not ctx.args:
        return await update.message.reply_text("الاستخدام: `/report [وصف الحلم]`", parse_mode=ParseMode.MARKDOWN)

    dream = " ".join(ctx.args)
    msg = await update.message.reply_text("📝 *كتابة تقرير مفصّل...*", parse_mode=ParseMode.MARKDOWN)
    await update.message.chat.send_action(ChatAction.TYPING)

    report = write_dream_report(dream)
    await msg.delete()
    # Split if too long for Telegram
    if len(report) > 4000:
        chunks = [report[i:i+4000] for i in range(0, len(report), 4000)]
        for chunk in chunks:
            await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(report, parse_mode=ParseMode.MARKDOWN)


async def cmd_article(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Generate cultural article (admin command)."""
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("⛔ أوامر المسؤول فقط.")
    if not ctx.args:
        return await update.message.reply_text("الاستخدام: `/article [موضوع المقالة]`", parse_mode=ParseMode.MARKDOWN)

    topic = " ".join(ctx.args)
    msg = await update.message.reply_text(f"✍️ *كتابة مقالة عن: {topic}*\nقد يستغرق ذلك 20-30 ثانية...", parse_mode=ParseMode.MARKDOWN)
    await update.message.chat.send_action(ChatAction.TYPING)

    article = write_article(topic)
    await msg.delete()
    data = load_leads()
    data["articles"] = data.get("articles", 0) + 1
    save_leads(data)

    if len(article) > 4000:
        chunks = [article[i:i+4000] for i in range(0, len(article), 4000)]
        for chunk in chunks:
            await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(article, parse_mode=ParseMode.MARKDOWN)


async def cmd_astats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin: detailed statistics."""
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("⛔ أوامر المسؤول فقط.")

    data = load_leads()
    users = data.get("users", [])
    plan_counts = {"free": 0, "basic": 0, "pro": 0, "team": 0}
    for u in users:
        plan = u.get("plan", "free")
        plan_counts[plan] = plan_counts.get(plan, 0) + 1

    today = datetime.now().date().isoformat()
    active_today = sum(1 for u in users if u.get("last_seen", "")[:10] == today)

    text = f"""👑 *إحصائيات المسؤول — Weaver*

📅 *التاريخ:* {today}

👥 *المستخدمون:*
• الإجمالي: {len(users)}
• نشطون اليوم: {active_today}
• مجاني: {plan_counts.get('free', 0)}
• أساسي: {plan_counts.get('basic', 0)}
• احترافي: {plan_counts.get('pro', 0)}
• فريق: {plan_counts.get('team', 0)}

📊 *النشاط الكلي:*
• الأحلام المفسَّرة: {data.get('dreams', 0)}
• الصور المولَّدة: {data.get('images', 0)}
• المقالات المكتوبة: {data.get('articles', 0)}

*آخر 5 مستخدمين:*"""

    recent = sorted(users, key=lambda u: u.get("joined", ""), reverse=True)[:5]
    for u in recent:
        text += f"\n• `{u['id']}` @{u.get('username', 'N/A')} — {u.get('plan', 'free')}"

    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_ahelp(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin help."""
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("⛔")

    text = """👑 *أوامر المسؤول — Weaver*

🎨 *توليد الصور:*
• `/genimage [prompt]` — توليد صورة من وصف إنجليزي مباشر
• `/auto [وصف عربي]` — ترجمة + توليد صورة تلقائياً

📝 *المحتوى:*
• `/report [حلم]` — تقرير مفصّل عن حلم
• `/article [موضوع]` — كتابة مقالة ثقافية

📊 *الإحصائيات:*
• `/astats` — إحصائيات مفصّلة للمسؤول

⚙️ *إدارة المستخدمين:*
• `/setplan [user_id] [plan]` — تعيين خطة لمستخدم
• `/broadcast [رسالة]` — إرسال إشعار لجميع المستخدمين"""

    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_setplan(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin: set user subscription plan."""
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("⛔")
    if len(ctx.args) < 2:
        return await update.message.reply_text("الاستخدام: `/setplan [user_id] [free/basic/pro/team]`", parse_mode=ParseMode.MARKDOWN)

    try:
        target_id = int(ctx.args[0])
        plan = ctx.args[1].lower()
        if plan not in ["free", "basic", "pro", "team"]:
            return await update.message.reply_text("❌ الخطط المتاحة: free, basic, pro, team")

        data = load_leads()
        updated = False
        for u in data["users"]:
            if u["id"] == target_id:
                u["plan"] = plan
                updated = True
                break

        if updated:
            save_leads(data)
            await update.message.reply_text(f"✅ تم تعيين خطة *{plan}* للمستخدم `{target_id}`", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(f"❌ المستخدم `{target_id}` غير موجود", parse_mode=ParseMode.MARKDOWN)
    except ValueError:
        await update.message.reply_text("❌ user_id يجب أن يكون رقماً")


async def cmd_broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin: broadcast message to all users."""
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("⛔")
    if not ctx.args:
        return await update.message.reply_text("الاستخدام: `/broadcast [الرسالة]`", parse_mode=ParseMode.MARKDOWN)

    message = " ".join(ctx.args)
    data = load_leads()
    users = data.get("users", [])
    sent, failed = 0, 0

    status_msg = await update.message.reply_text(f"📢 *إرسال لـ {len(users)} مستخدم...*", parse_mode=ParseMode.MARKDOWN)

    for u in users:
        try:
            await ctx.bot.send_message(
                chat_id=u["id"],
                text=f"📢 *إشعار من Weaver*\n\n{message}",
                parse_mode=ParseMode.MARKDOWN
            )
            sent += 1
            await asyncio.sleep(0.05)  # Rate limiting
        except Exception:
            failed += 1

    await status_msg.edit_text(f"✅ *تم الإرسال*\n• نجح: {sent}\n• فشل: {failed}", parse_mode=ParseMode.MARKDOWN)


# ─────────────────────────────────────────
# MESSAGE HANDLER (Main dream interpretation)
# ─────────────────────────────────────────
async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = upsert_user(update)
    text = update.message.text.strip()

    if len(text) < 10:
        await update.message.reply_text(
            "🌙 أرسل لي وصفاً لحلمك (10 كلمات على الأقل) وسأفسره لك فوراً!\n\n"
            "_مثال: رأيت في منامي أنني أطير فوق السحاب وأرى البحر تحتي..._",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # Check daily limit
    can_use, used, limit = check_daily_limit(user["id"], "dreams_today")
    if not can_use:
        await update.message.reply_text(
            f"⚠️ *وصلت لحد التفسيرات اليومية* ({used}/{limit})\n\n"
            "🔓 *الترقية للاحترافي:* تفسيرات غير محدودة!\n",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=plans_keyboard()
        )
        return

    lang = user.get("lang", "ar")
    thinking_msgs = [
        "🔮 *جاري تحليل رموز حلمك...*",
        "🌙 *أستشير تراث ابن سيرين...*",
        "✨ *أنسج تفسير حلمك...*"
    ]

    msg = await update.message.reply_text(thinking_msgs[0], parse_mode=ParseMode.MARKDOWN)
    await update.message.chat.send_action(ChatAction.TYPING)

    # Get interpretation
    interpretation = interpret_dream(text, lang)

    await msg.edit_text(thinking_msgs[1], parse_mode=ParseMode.MARKDOWN)

    # Send interpretation
    await msg.delete()
    await update.message.reply_text(interpretation, parse_mode=ParseMode.MARKDOWN)

    # Update stats
    increment_stat(user["id"], "dreams_today", "dreams")
    data = load_leads()
    for u in data["users"]:
        if u["id"] == user["id"]:
            u["total_dreams"] = u.get("total_dreams", 0) + 1
            break
    save_leads(data)

    # Ask if user wants image
    plan_name = user.get("plan", "free")
    can_image, used_img, img_limit = check_daily_limit(user["id"], "images_today")

    if can_image:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎨 توليد صورة 4K من حلمي", callback_data=f"gen_img:{text[:100]}")],
            [InlineKeyboardButton("🌙 تفسير حلم جديد", callback_data="start_dream"),
             InlineKeyboardButton("🔙 الرئيسية", callback_data="back_main")],
        ])
        await update.message.reply_text(
            "✨ هل تريد توليد صورة فنية 4K من حلمك؟",
            reply_markup=keyboard
        )
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌙 تفسير حلم جديد", callback_data="start_dream")],
            [InlineKeyboardButton("💎 ترقية للصور اللامحدودة", url=PLANS["pro"]["url"])],
        ])
        await update.message.reply_text(
            f"⚠️ وصلت لحد الصور اليومية ({used_img}/{img_limit})\nقم بالترقية للحصول على صور غير محدودة!",
            reply_markup=keyboard
        )


# ─────────────────────────────────────────
# CALLBACK QUERY HANDLERS
# ─────────────────────────────────────────
async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = upsert_user(update)

    # ── Image generation from dream ──
    if data.startswith("gen_img:"):
        dream_text = data[8:]
        await query.edit_message_text("🎨 *اختر أسلوباً فنياً لصورتك:*", parse_mode=ParseMode.MARKDOWN, reply_markup=style_keyboard())
        ctx.user_data["pending_dream"] = dream_text

    elif data.startswith("style_"):
        style = data[6:]
        dream_text = ctx.user_data.get("pending_dream", "")
        if not dream_text:
            await query.edit_message_text("❌ انتهت جلسة الصورة. أرسل حلمك مرة أخرى.")
            return
        await query.edit_message_text(f"🎨 *جاري توليد صورة بأسلوب {style}...*\nقد يستغرق 15-30 ثانية ⏳", parse_mode=ParseMode.MARKDOWN)

        # Translate and generate
        en_text = translate_to_english(dream_text)
        img_prompt = generate_image_prompt(en_text, style)
        url = generate_image(img_prompt)

        if url:
            await query.message.reply_photo(
                photo=url,
                caption=f"🎨 *صورة حلمك*\n✨ الأسلوب: _{style}_\n\n_Powered by Stable Diffusion 3.5 — Weaver نَسَّاج_",
                parse_mode=ParseMode.MARKDOWN
            )
            await query.delete_message()
            increment_stat(user["id"], "images_today", "images")
            data2 = load_leads()
            for u in data2["users"]:
                if u["id"] == user["id"]:
                    u["total_images"] = u.get("total_images", 0) + 1
                    break
            save_leads(data2)
        else:
            await query.edit_message_text("❌ فشل توليد الصورة. حاول مرة أخرى لاحقاً.")

    elif data == "start_dream":
        await query.edit_message_text(
            "🌙 *أرسل لي وصف حلمك:*\n\n_مثال: رأيت في منامي أنني أطير فوق البحر وأرى جزراً خضراء..._",
            parse_mode=ParseMode.MARKDOWN
        )

    elif data == "start_image":
        await query.edit_message_text(
            "🎨 *أرسل وصف الصورة التي تريد توليدها:*\n\n_مثال: غابة سحرية تحت ضوء القمر مع نجوم لامعة..._",
            parse_mode=ParseMode.MARKDOWN
        )
        ctx.user_data["direct_image"] = True

    elif data == "show_plans":
        text = """💎 *خطط Weaver | نَسَّاج*

🥉 *أساسي — $4.99/شهر*
• 5 تفسيرات يومياً • 3 صور

🥇 *احترافي — $9.99/شهر*
• ∞ تفسيرات • ∞ صور 4K • 50 أسلوب فني

👥 *فريق — $19.99/شهر*
• كل الاحترافي + فيديو + PDF + API"""
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=plans_keyboard())

    elif data == "my_stats":
        user_full = get_user(user["id"])
        plan_name = user_full.get("plan", "free") if user_full else "free"
        plan_info = PLANS.get(plan_name, {"name_ar": "مجاني", "price": "مجاني"})
        text = f"""📊 *إحصائياتك*

📋 الخطة: *{plan_info['name_ar']}*
🌙 أحلام اليوم: *{user_full.get('dreams_today', 0)}*
🎨 صور اليوم: *{user_full.get('images_today', 0)}*
🔮 إجمالي الأحلام: *{user_full.get('total_dreams', 0)}*"""
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]]))

    elif data == "help_menu":
        text = """❓ *مساعدة Weaver*

*كيف أفسر حلمي؟*
فقط أرسل وصف حلمك نصياً!

*الأوامر:*
• `/start` — الرئيسية
• `/stats` — إحصائياتك
• `/plans` — خطط الاشتراك
• `/lang en` — تغيير للإنجليزية

*الموقع:* aidreamweaver.store"""
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]]))

    elif data == "back_main":
        name = update.effective_user.first_name or "صديقي"
        await query.edit_message_text(
            f"🌙 *Weaver | نَسَّاج* — مرحباً *{name}*\n\nأرسل لي حلمك أو اختر من الأزرار:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=main_keyboard_ar()
        )

    elif data == "cancel":
        await query.edit_message_text("❌ تم الإلغاء.")
        ctx.user_data.clear()


# ─────────────────────────────────────────
# ERROR HANDLER
# ─────────────────────────────────────────
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    log.error(f"Update {update} caused error: {context.error}")
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ حدث خطأ مؤقت. حاول مرة أخرى بعد لحظة."
            )
        except Exception:
            pass


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def main():
    # Validate config
    if not TELEGRAM_TOKEN:
        log.error("❌ TELEGRAM_TOKEN is missing!")
        return
    if not GEMINI_API_KEY:
        log.warning("⚠️ GEMINI_API_KEY is missing — dream interpretation will fail")
    if not SILICONFLOW_API_KEY:
        log.warning("⚠️ SILICONFLOW_API_KEY is missing — image generation will fail")

    log.info("🧵 Starting Weaver Bot...")
    log.info(f"   Admin ID: {ADMIN_USER_ID}")
    log.info(f"   Gemini: {'✅' if GEMINI_API_KEY else '❌'}")
    log.info(f"   SiliconFlow: {'✅' if SILICONFLOW_API_KEY else '❌'}")

    # Initialize leads file if needed
    if not Path(LEADS_FILE).exists():
        save_leads({"total_users": 0, "users": [], "dreams": 0, "images": 0, "articles": 0})
        log.info(f"Created {LEADS_FILE}")

    # Build application
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # User commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("plans", cmd_plans))
    app.add_handler(CommandHandler("lang", cmd_lang))

    # Admin commands
    app.add_handler(CommandHandler("genimage", cmd_genimage))
    app.add_handler(CommandHandler("auto", cmd_auto))
    app.add_handler(CommandHandler("report", cmd_report))
    app.add_handler(CommandHandler("article", cmd_article))
    app.add_handler(CommandHandler("astats", cmd_astats))
    app.add_handler(CommandHandler("ahelp", cmd_ahelp))
    app.add_handler(CommandHandler("setplan", cmd_setplan))
    app.add_handler(CommandHandler("broadcast", cmd_broadcast))

    # Callback queries
    app.add_handler(CallbackQueryHandler(handle_callback))

    # Text messages (main dream handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Error handler
    app.add_error_handler(error_handler)

    log.info("✅ Bot is running! Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=["message", "callback_query"], drop_pending_updates=True)


if __name__ == "__main__":
    main()
