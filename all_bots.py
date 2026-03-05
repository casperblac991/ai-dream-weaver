#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 AI DREAM WEAVER - البوت المتكامل النهائي
=============================================
- تفسير الأحلام باستخدام Google Gemini
- توليد الصور باستخدام PixVerse Ultra
- توليد مقالات للمدونة
- نظام تتبع العملاء المتقدم
- إحصائيات وتقارير
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# ========== المفاتيح من المتغيرات البيئية ==========
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
PIXVERSE_API_KEY = os.environ.get('PIXVERSE_API_KEY')

# التحقق من وجود المفاتيح الأساسية
if not TELEGRAM_TOKEN:
    print("❌ خطأ: توكن تيليجرام غير موجود!")
    exit(1)

if not GEMINI_API_KEY:
    print("⚠️ تحذير: مفتاح Gemini غير موجود - تفسير الأحلام لن يعمل")

# ========== إعداد التسجيل ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== نظام تتبع العملاء المتقدم ==========
LEADS_FILE = "leads.json"

def load_leads():
    try:
        with open(LEADS_FILE, 'r') as f:
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
    with open(LEADS_FILE, 'w') as f:
        json.dump(leads, f, indent=2)

def add_user(user_id, username, first_name):
    leads = load_leads()
    user_id_str = str(user_id)
    
    # البحث عن المستخدم
    for user in leads['users']:
        if user['id'] == user_id_str:
            user['last_seen'] = str(datetime.now())
            user['interactions'] += 1
            save_leads(leads)
            return False
    
    # مستخدم جديد
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
        "active_today": today_users
    }

# ========== دوال البوت الأساسية ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة الترحيب مع الأزرار التفاعلية"""
    user = update.effective_user
    is_new = add_user(user.id, user.username, user.first_name)
    
    welcome_msg = (
        f"مرحباً {user.first_name}! 🌙\n\n"
        "أنا بوت **حالم** المتكامل، أستخدم Google Gemini لتفسير الأحلام و PixVerse لتوليد الصور.\n\n"
        "**📌 الأوامر المتاحة:**\n"
        "• أرسل لي حلمك مباشرة للتفسير\n"
        "• /image [وصف] - لتوليد صورة\n"
        "• /article [موضوع] - لتوليد مقالة\n"
        "• /stats - إحصائيات البوت\n"
        "• /help - مساعدة"
    )
    
    # أزرار تفاعلية
    keyboard = [
        [
            InlineKeyboardButton("📝 تفسير حلم", callback_data="dream"),
            InlineKeyboardButton("🎨 توليد صورة", callback_data="image")
        ],
        [
            InlineKeyboardButton("📚 المدونة", url="https://aidreamweaver.store/blog.html"),
            InlineKeyboardButton("🤖 المتجر", url="https://aidreamweaver.store")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة المساعدة"""
    help_text = """
🔍 **مساعدة البوت**

**📝 تفسير الأحلام:**
أرسل لي حلمك مباشرة (مثال: "حلمت أني أطير في السماء")

**🎨 توليد الصور:**
استخدم الأمر /image متبوعاً بوصف الصورة
مثال: `/image شخص يطير في السماء، ألوان بنفسجية`

**📚 توليد مقالات:**
استخدم الأمر /article متبوعاً بموضوع المقالة
مثال: `/article تفسير الأحلام في اليونان القديمة`

**📊 الإحصائيات:**
/stats - عرض إحصائيات البوت

**🔗 روابط مفيدة:**
• المتجر: https://aidreamweaver.store
• المدونة: https://aidreamweaver.store/blog.html
• الأسئلة الشائعة: https://aidreamweaver.store/faq.html
"""
    await update.message.reply_text(help_text)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض إحصائيات البوت"""
    stats = get_stats()
    stats_msg = (
        f"📊 **إحصائيات حالم**\n\n"
        f"👥 إجمالي المستخدمين: {stats['total_users']}\n"
        f"💭 إجمالي الأحلام: {stats['total_dreams']}\n"
        f"🎨 إجمالي الصور: {stats['total_images']}\n"
        f"📅 نشط اليوم: {stats['active_today']}"
    )
    await update.message.reply_text(stats_msg)

# ========== دالة تفسير الأحلام باستخدام Gemini ==========
async def interpret_dream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تفسير الأحلام باستخدام Google Gemini"""
    user = update.effective_user
    dream = update.message.text
    
    # تسجيل التفاعل
    add_user(user.id, user.username, user.first_name)
    increment_dreams(user.id)
    
    if not GEMINI_API_KEY:
        await update.message.reply_text("❌ مفتاح Gemini غير متوفر حالياً.")
        return
    
    await update.message.reply_text("🔮 جاري التفسير باستخدام Google Gemini...")
    
    try:
        # الاتصال بـ Gemini API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"فسر هذا الحلم باللغة العربية بأسلوب بسيط وشيق، مع ذكر الدلالات والرموز: {dream}"
                }]
            }]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            interpretation = result['candidates'][0]['content']['parts'][0]['text']
            
            # إضافة روابط للمدونة
            keyboard = [
                [InlineKeyboardButton("📚 اقرأ عن تفسير الأحلام", url="https://aidreamweaver.store/blog.html")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✨ **تفسير حلمك:**\n\n{interpretation}",
                reply_markup=reply_markup
            )
        else:
            logger.error(f"خطأ Gemini {response.status_code}: {response.text}")
            await update.message.reply_text(f"❌ خطأ في الاتصال بـ Gemini: {response.status_code}")
            
    except Exception as e:
        logger.error(f"استثناء: {str(e)}")
        await update.message.reply_text("❌ حدث خطأ. حاول مرة أخرى.")

# ========== دالة توليد الصور باستخدام PixVerse ==========
async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """توليد صورة باستخدام PixVerse Ultra"""
    user = update.effective_user
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ الرجاء كتابة وصف الصورة بعد الأمر.\n"
            "مثال: `/image شخص يطير في السماء، ألوان بنفسجية`"
        )
        return
    
    prompt = " ".join(context.args)
    
    if not PIXVERSE_API_KEY:
        await update.message.reply_text("❌ مفتاح PixVerse غير متوفر حالياً.")
        return
    
    await update.message.reply_text("🎨 جاري توليد الصورة... (قد يستغرق 30-60 ثانية)")
    
    try:
        # تسجيل الطلب
        add_user(user.id, user.username, user.first_name)
        increment_images(user.id)
        
        # الاتصال بـ PixVerse API
        url = "https://api.pixverse.ai/v1/images/generations"
        
        headers = {
            "Authorization": f"Bearer {PIXVERSE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "aspect_ratio": "1:1",
            "style": "fantasy",
            "quality": "standard"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            image_url = result.get('data', [{}])[0].get('url')
            if image_url:
                await update.message.reply_photo(
                    photo=image_url,
                    caption=f"🎨 صورة: {prompt}"
                )
            else:
                await update.message.reply_text("❌ لم يتم العثور على رابط الصورة")
        else:
            logger.error(f"خطأ PixVerse {response.status_code}: {response.text}")
            await update.message.reply_text(f"❌ خطأ في توليد الصورة: {response.status_code}")
            
    except Exception as e:
        logger.error(f"استثناء PixVerse: {str(e)}")
        await update.message.reply_text("❌ حدث خطأ في توليد الصورة")

# ========== دالة توليد مقالات للمدونة ==========
async def generate_article(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """توليد مقالة للمدونة باستخدام Gemini"""
    user = update.effective_user
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ الرجاء كتابة موضوع المقالة بعد الأمر.\n"
            "مثال: `/article تفسير الأحلام في بلاد الرافدين`"
        )
        return
    
    topic = " ".join(context.args)
    
    if not GEMINI_API_KEY:
        await update.message.reply_text("❌ مفتاح Gemini غير متوفر حالياً.")
        return
    
    await update.message.reply_text(f"📝 جاري توليد مقالة عن '{topic}' باستخدام Gemini...")
    
    try:
        # الاتصال بـ Gemini API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"اكتب مقالة شاملة باللغة العربية عن '{topic}'، مع مقدمة وعناوين فرعية وخاتمة. اجعلها مناسبة لنشرها في مدونة ثقافية."
                }]
            }]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            article = result['candidates'][0]['content']['parts'][0]['text']
            
            # إرسال المقالة (مقسمة إذا كانت طويلة)
            if len(article) > 4096:
                parts = [article[i:i+4096] for i in range(0, len(article), 4096)]
                for part in parts:
                    await update.message.reply_text(part)
            else:
                await update.message.reply_text(f"📄 **مقالة عن {topic}**\n\n{article}")
            
            # تسجيل المقالة
            leads = load_leads()
            leads['articles'] += 1
            save_leads(leads)
            
        else:
            logger.error(f"خطأ Gemini {response.status_code}: {response.text}")
            await update.message.reply_text(f"❌ خطأ في توليد المقالة: {response.status_code}")
            
    except Exception as e:
        logger.error(f"استثناء: {str(e)}")
        await update.message.reply_text("❌ حدث خطأ في توليد المقالة")

# ========== معالج الأزرار التفاعلية ==========
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الضغط على الأزرار"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "dream":
        await query.edit_message_text("📝 أرسل لي حلمك الآن وسأقوم بتفسيره.")
    elif query.data == "image":
        await query.edit_message_text("🎨 استخدم الأمر /image متبوعاً بوصف الصورة.\nمثال: `/image شخص يطير في السماء`")

# ========== الدالة الرئيسية ==========
def main():
    """تشغيل البوت المتكامل"""
    print("🚀 بدء تشغيل البوت المتكامل...")
    print(f"   - Gemini: {'✅ مفعل' if GEMINI_API_KEY else '❌ غير مفعل'}")
    print(f"   - PixVerse: {'✅ مفعل' if PIXVERSE_API_KEY else '❌ غير مفعل'}")
    
    # إنشاء التطبيق
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("image", generate_image))
    app.add_handler(CommandHandler("article", generate_article))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, interpret_dream))
    
    print("✅ البوت شغال وجاهز!")
    
    # تشغيل البوت
    app.run_polling()

if __name__ == '__main__':
    main()
