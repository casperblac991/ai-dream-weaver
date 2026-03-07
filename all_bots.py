#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 AI DREAM WEAVER - بوت المدير الذكي (مع إعادة المحاولة)
==============================================================
- تفسير الأحلام (Gemini 2.0 Flash)
- توليد الصور (Pollinations.ai - مع إعادة المحاولة)
- أوامر المسؤول
- نظام تتبع العملاء
"""

import os
import json
import asyncio
import requests
import logging
from datetime import datetime
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# ========== إعدادات المسؤول ==========
ADMIN_USER_ID = 6790340715  # ⚠️ تأكد من صحة هذا الرقم

# ========== المفاتيح من المتغيرات البيئية ==========
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

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
        return {"total_users": 0, "users": [], "dreams": 0, "images": 0, "articles": 0}

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
        if datetime.fromisoformat(user['last_seen']).date() == today:
            today_users += 1
    return {
        "total_users": leads['total_users'],
        "total_dreams": leads['dreams'],
        "total_images": leads['images'],
        "total_articles": leads['articles'],
        "active_today": today_users
    }

# ========== دوال البوت الأساسية ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username, user.first_name)
    
    welcome_msg = (
        f"مرحباً {user.first_name}! 🌙\n\n"
        "أنا بوت **حالم** المتطور.\n"
        "أستخدم **Gemini 2.0 Flash** لتفسير الأحلام.\n"
        "أستخدم **Pollinations.ai** لتوليد الصور.\n\n"
        "📌 **الأوامر المتاحة:**\n"
        "• أرسل لي حلمك مباشرة للتفسير\n"
        "• /stats - إحصائيات البوت\n"
        "• /help - مساعدة"
    )
    
    keyboard = [
        [InlineKeyboardButton("📝 تفسير حلم", callback_data="dream")],
        [InlineKeyboardButton("📚 المدونة", url="https://aidreamweaver.store/blog.html"),
         InlineKeyboardButton("🛒 المتجر", url="https://aidreamweaver.store")]
    ]
    await update.message.reply_text(welcome_msg, reply_markup=InlineKeyboardMarkup(keyboard))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    stats = get_stats()
    await update.message.reply_text(
        f"📊 **إحصائيات حالم**\n\n"
        f"👥 إجمالي المستخدمين: {stats['total_users']}\n"
        f"💭 إجمالي الأحلام: {stats['total_dreams']}\n"
        f"🎨 إجمالي الصور: {stats['total_images']}\n"
        f"📅 نشط اليوم: {stats['active_today']}",
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "dream":
        await query.edit_message_text("📝 أرسل لي حلمك الآن وسأقوم بتفسيره.")

async def interpret_dream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    dream = update.message.text
    
    add_user(user.id, user.username, user.first_name)
    increment_dreams(user.id)
    
    if not GEMINI_API_KEY:
        await update.message.reply_text("❌ مفتاح Gemini غير متوفر.")
        return
    
    await update.message.reply_text("🔮 جاري التفسير...")
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": f"فسر هذا الحلم بالعربية: {dream}"}]}]}
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            interpretation = result['candidates'][0]['content']['parts'][0]['text']
            await update.message.reply_text(f"✨ {interpretation}")
        elif response.status_code == 429:
            await update.message.reply_text("⚠️ وصلت للحد اليومي. انتظر حتى الغد.")
        else:
            await update.message.reply_text(f"❌ خطأ {response.status_code}")
    except Exception as e:
        logger.error(f"خطأ: {e}")
        await update.message.reply_text("❌ حدث خطأ.")

# ========== دوال المسؤول ==========
async def is_admin(update: Update) -> bool:
    user = update.effective_user
    if user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ هذا الأمر للمشرف فقط.")
        return False
    return True

async def admin_genimage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """توليد صورة مع إعادة المحاولة التلقائية"""
    if not await is_admin(update):
        return

    if not context.args:
        await update.message.reply_text("⚠️ اكتب وصف الصورة: /genimage [وصف]")
        return

    prompt = " ".join(context.args)
    await update.message.reply_text("🎨 جاري توليد الصورة باستخدام Pollinations.ai...")

    # تجربة حتى 3 مرات
    for attempt in range(3):
        try:
            url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1024&height=1024&nologo=true"
            
            response = requests.get(url, timeout=90)
            
            if response.status_code == 200:
                await update.message.reply_photo(
                    photo=response.content,
                    caption=f"🎨 {prompt}"
                )
                increment_images(update.effective_user.id)
                return
            elif response.status_code == 502 and attempt < 2:
                # انتظر ثانيتين ثم حاول مجدداً
                await update.message.reply_text(f"⚠️ المحاولة {attempt+1} فشلت، جاري إعادة المحاولة...")
                await asyncio.sleep(2)
                continue
            else:
                await update.message.reply_text(f"❌ خطأ {response.status_code}")
                return
                
        except Exception as e:
            if attempt < 2:
                await asyncio.sleep(2)
                continue
            logger.error(f"خطأ: {e}")
            await update.message.reply_text(f"❌ خطأ: {str(e)}")
            return

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return
    stats = get_stats()
    await update.message.reply_text(
        f"📊 **تقرير المسؤول**\n\n"
        f"👥 إجمالي المستخدمين: {stats['total_users']}\n"
        f"💭 إجمالي الأحلام: {stats['total_dreams']}\n"
        f"🎨 إجمالي الصور: {stats['total_images']}\n"
        f"📅 نشط اليوم: {stats['active_today']}\n\n"
        f"• Gemini: {'✅' if GEMINI_API_KEY else '❌'}\n"
        f"• Pollinations: ✅ (مجاني)",
        parse_mode='Markdown'
    )

async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return
    await update.message.reply_text(
        "👑 **أوامر المسؤول**\n\n"
        "• `/genimage [وصف]` - توليد صورة\n"
        "• `/astats` - إحصائيات مفصلة",
        parse_mode='Markdown'
    )

# ========== الدالة الرئيسية ==========
def main():
    print("🚀 بدء تشغيل بوت حالم (مع إعادة المحاولة)...")
    print(f"   - Gemini: {'✅' if GEMINI_API_KEY else '❌'}")
    print(f"   - Pollinations: ✅ (مجاني)")
    print(f"   - المسؤول: {ADMIN_USER_ID}")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, interpret_dream))
    
    app.add_handler(CommandHandler("genimage", admin_genimage))
    app.add_handler(CommandHandler("astats", admin_stats))
    app.add_handler(CommandHandler("ahelp", admin_help))
    
    print("✅ البوت شغال!")
    app.run_polling()

if __name__ == '__main__':
    main()
