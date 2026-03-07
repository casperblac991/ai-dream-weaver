#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 AI DREAM WEAVER - بوت المدير الذكي (مع Hugging Face للصور)
==============================================================
- تفسير الأحلام (Gemini 2.0 Flash)
- توليد الصور (Hugging Face FLUX.1-schnell)
- أوامر المسؤول
- نظام تتبع العملاء
- إحصائيات وتقارير
"""

import os
import json
import base64
import requests
import logging
from datetime import datetime
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from huggingface_hub import InferenceClient

# ========== إعدادات المسؤول ==========
ADMIN_USER_ID = 6790340715  # ⚠️ تأكد من صحة هذا الرقم

# ========== المفاتيح من المتغيرات البيئية ==========
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
HF_TOKEN = os.environ.get('HF_TOKEN')

# التحقق من وجود المفاتيح الأساسية
if not TELEGRAM_TOKEN:
    print("❌ خطأ: توكن تيليجرام غير موجود!")
    exit(1)

# ========== إعداد التسجيل ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== نظام تتبع العملاء ==========
LEADS_FILE = "leads.json"

def load_leads():
    try:
        with open(LEADS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            "total_users": 0,
            "users": [],
            "dreams": 0,
            "images": 0,
            "articles": 0
        }

def save_leads(leads):
    with open(LEADS_FILE, 'w', encoding='utf-8') as f:
        json.dump(leads, f, indent=2, ensure_ascii=False)

def add_user(user_id, username, first_name):
    leads = load_leads()
    user_id_str = str(user_id)
    
    for user in leads['users']:
        if user['id'] == user_id_str:
            user['last_seen'] = str(datetime.now())
            user['interactions'] += 1
            save_leads(leads)
            return False
    
    new_user = {
        "id": user_id_str,
        "username": username,
        "first_name": first_name,
        "first_seen": str(datetime.now()),
        "last_seen": str(datetime.now()),
        "interactions": 1,
        "dreams": 0,
        "images": 0
    }
    leads['users'].append(new_user)
    leads['total_users'] += 1
    save_leads(leads)
    return True

def increment_dreams(user_id):
    leads = load_leads()
    user_id_str = str(user_id)
    for user in leads['users']:
        if user['id'] == user_id_str:
            user['dreams'] += 1
            leads['dreams'] += 1
            save_leads(leads)
            break

def increment_images(user_id):
    leads = load_leads()
    user_id_str = str(user_id)
    for user in leads['users']:
        if user['id'] == user_id_str:
            user['images'] += 1
            leads['images'] += 1
            save_leads(leads)
            break

def get_stats():
    leads = load_leads()
    today = datetime.now().date()
    today_users = 0
    
    for user in leads['users']:
        last_seen = datetime.fromisoformat(user['last_seen']).date()
        if last_seen == today:
            today_users += 1
    
    return {
        "total_users": leads['total_users'],
        "total_dreams": leads['dreams'],
        "total_images": leads['images'],
        "total_articles": leads['articles'],
        "active_today": today_users
    }

# ========== دوال البوت الأساسية (للمستخدمين) ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة الترحيب للمستخدمين"""
    user = update.effective_user
    add_user(user.id, user.username, user.first_name)
    
    welcome_msg = (
        f"مرحباً {user.first_name}! 🌙\n\n"
        "أنا بوت **حالم** المتطور.\n"
        "أستخدم **Gemini 2.0 Flash** لتفسير الأحلام.\n"
        "أستخدم **Hugging Face** لتوليد الصور.\n\n"
        "📌 **الأوامر المتاحة:**\n"
        "• أرسل لي حلمك مباشرة للتفسير\n"
        "• /stats - إحصائيات البوت\n"
        "• /help - مساعدة"
    )
    
    # أزرار تفاعلية
    keyboard = [
        [InlineKeyboardButton("📝 تفسير حلم", callback_data="dream")],
        [InlineKeyboardButton("📚 المدونة", url="https://aidreamweaver.store/blog.html"),
         InlineKeyboardButton("🛒 المتجر", url="https://aidreamweaver.store")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة المساعدة للمستخدمين"""
    help_text = """
🔍 **مساعدة البوت**

**📝 لتفسير حلمك:**
أرسل لي حلمك مباشرة (مثال: "حلمت أني أطير في السماء")

**📊 للإحصائيات:**
/stats - عرض إحصائيات البوت

**🔗 روابط مفيدة:**
• المتجر: https://aidreamweaver.store
• المدونة: https://aidreamweaver.store/blog.html
"""
    await update.message.reply_text(help_text)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض إحصائيات البوت للمستخدمين"""
    stats = get_stats()
    stats_msg = (
        f"📊 **إحصائيات حالم**\n\n"
        f"👥 إجمالي المستخدمين: {stats['total_users']}\n"
        f"💭 إجمالي الأحلام: {stats['total_dreams']}\n"
        f"🎨 إجمالي الصور: {stats['total_images']}\n"
        f"📅 نشط اليوم: {stats['active_today']}"
    )
    await update.message.reply_text(stats_msg)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الأزرار التفاعلية"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "dream":
        await query.edit_message_text("📝 أرسل لي حلمك الآن وسأقوم بتفسيره.")

# ========== دالة تفسير الأحلام (Gemini) ==========
async def interpret_dream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تفسير الأحلام باستخدام Gemini 2.0 Flash"""
    user = update.effective_user
    dream = update.message.text
    
    # تسجيل التفاعل
    add_user(user.id, user.username, user.first_name)
    increment_dreams(user.id)
    
    if not GEMINI_API_KEY:
        await update.message.reply_text("❌ مفتاح Gemini غير متوفر.")
        return
    
    await update.message.reply_text("🔮 جاري التفسير...")
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": f"فسر هذا الحلم بالعربية: {dream}"}]}]}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            interpretation = result['candidates'][0]['content']['parts'][0]['text']
            await update.message.reply_text(f"✨ {interpretation}")
        elif response.status_code == 429:
            await update.message.reply_text("⚠️ وصلت للحد اليومي. انتظر حتى الغد.")
        else:
            await update.message.reply_text(f"❌ خطأ {response.status_code}")
            
    except Exception as e:
        logger.error(f"خطأ في التفسير: {str(e)}")
        await update.message.reply_text("❌ حدث خطأ.")

# ========== دوال المسؤول (Admin Commands) ==========
async def is_admin(update: Update) -> bool:
    """التحقق من أن المستخدم هو المسؤول"""
    user = update.effective_user
    if user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ هذا الأمر للمشرف فقط.")
        return False
    return True

async def admin_genimage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """توليد صورة باستخدام Hugging Face"""
    if not await is_admin(update):
        return

    if not context.args:
        await update.message.reply_text("⚠️ اكتب وصف الصورة: /genimage [وصف]")
        return

    prompt = " ".join(context.args)
    await update.message.reply_text("🎨 جاري توليد الصورة باستخدام Hugging Face...")

    if not HF_TOKEN:
        await update.message.reply_text("❌ مفتاح Hugging Face غير موجود.")
        return

    try:
        # استخدام FLUX.1-schnell (أفضل نموذج حالي)
        client = InferenceClient(
            model="black-forest-labs/FLUX.1-schnell",
            token=HF_TOKEN
        )
        
        # توليد الصورة
        image = client.text_to_image(
            prompt,
            width=1024,
            height=1024
        )
        
        if image:
            # حفظ الصورة في BytesIO
            img_bytes = BytesIO()
            image.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            await update.message.reply_photo(
                photo=img_bytes,
                caption=f"🎨 {prompt}"
            )
            increment_images(update.effective_user.id)
        else:
            await update.message.reply_text("❌ فشل توليد الصورة")
            
    except Exception as e:
        logger.error(f"خطأ في توليد الصورة: {str(e)}")
        await update.message.reply_text(f"❌ خطأ: {str(e)}")

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إحصائيات مفصلة للمسؤول"""
    if not await is_admin(update):
        return
    
    stats = get_stats()
    msg = (
        f"📊 **تقرير المسؤول**\n\n"
        f"👥 إجمالي المستخدمين: {stats['total_users']}\n"
        f"💭 إجمالي الأحلام: {stats['total_dreams']}\n"
        f"🎨 إجمالي الصور: {stats['total_images']}\n"
        f"📝 المقالات: {stats['total_articles']}\n"
        f"📅 نشط اليوم: {stats['active_today']}\n\n"
        f"• Gemini: {'✅' if GEMINI_API_KEY else '❌'}\n"
        f"• Hugging Face: {'✅' if HF_TOKEN else '❌'}"
    )
    await update.message.reply_text(msg)

async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مساعدة المسؤول"""
    if not await is_admin(update):
        return
    
    help_msg = """
👑 **أوامر المسؤول**

• `/genimage [وصف]` - توليد صورة باستخدام Hugging Face
• `/astats` - إحصائيات مفصلة
    """
    await update.message.reply_text(help_msg)

# ========== الدالة الرئيسية ==========
def main():
    """تشغيل البوت"""
    print("🚀 بدء تشغيل بوت حالم (مع Hugging Face)...")
    print(f"   - Gemini: {'✅' if GEMINI_API_KEY else '❌'}")
    print(f"   - Hugging Face: {'✅' if HF_TOKEN else '❌'}")
    print(f"   - المسؤول: {ADMIN_USER_ID}")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # أوامر المستخدمين العادية
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, interpret_dream))
    
    # أوامر المسؤول
    app.add_handler(CommandHandler("genimage", admin_genimage))
    app.add_handler(CommandHandler("astats", admin_stats))
    app.add_handler(CommandHandler("ahelp", admin_help))
    
    print("✅ البوت شغال!")
    app.run_polling()

if __name__ == '__main__':
    main()
