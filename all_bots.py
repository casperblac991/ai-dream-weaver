#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 AI DREAM WEAVER - بوت حالم النهائي
=======================================
- يستخدم Gemini 2.0 Flash (1,500 طلب/يوم مجاناً)
- إدارة ذكية لحدود الاستخدام
- رسائل واضحة للمستخدم
"""

import os
import json
import time
import requests
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# ========== المفاتيح من المتغيرات البيئية ==========
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# التحقق من وجود المفاتيح
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

# ========== نظام تتبع العملاء البسيط ==========
LEADS_FILE = "leads.json"

def load_leads():
    try:
        with open(LEADS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"total_users": 0, "users": [], "dreams": 0}

def save_leads(leads):
    with open(LEADS_FILE, 'w') as f:
        json.dump(leads, f, indent=2)

def add_user(user_id, username, first_name):
    leads = load_leads()
    user_id_str = str(user_id)
    
    if user_id_str not in [u['id'] for u in leads['users']]:
        leads['users'].append({
            "id": user_id_str,
            "username": username,
            "first_name": first_name,
            "first_seen": str(datetime.now()),
            "dream_count": 0
        })
        leads['total_users'] += 1
        save_leads(leads)
        return True
    return False

def increment_dreams(user_id):
    leads = load_leads()
    user_id_str = str(user_id)
    for user in leads['users']:
        if user['id'] == user_id_str:
            user['dream_count'] += 1
            leads['dreams'] += 1
            save_leads(leads)
            break

# ========== دوال البوت الأساسية ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة الترحيب مع الأزرار التفاعلية"""
    user = update.effective_user
    add_user(user.id, user.username, user.first_name)
    
    welcome_msg = (
        f"مرحباً {user.first_name}! 🌙\n\n"
        "أنا بوت **حالم** المتطور.\n"
        "أستخدم **Gemini 2.0 Flash** لتفسير الأحلام (1,500 تفسير مجاني يومياً).\n\n"
        "📌 **الأوامر المتاحة:**\n"
        "• أرسل لي حلمك مباشرة للتفسير\n"
        "• /stats - إحصائيات البوت\n"
        "• /help - مساعدة"
    )
    
    # أزرار تفاعلية
    keyboard = [
        [
            InlineKeyboardButton("📝 تفسير حلم", callback_data="dream"),
            InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")
        ],
        [
            InlineKeyboardButton("📚 المدونة", url="https://aidreamweaver.store/blog.html"),
            InlineKeyboardButton("🛒 المتجر", url="https://aidreamweaver.store")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة المساعدة"""
    help_text = """
🔍 **مساعدة البوت**

**📝 لتفسير حلمك:**
أرسل لي حلمك مباشرة (مثال: "حلمت أني أطير في السماء")

**📊 للإحصائيات:**
/stats - عرض إحصائيات البوت

**🔗 روابط مفيدة:**
• المتجر: https://aidreamweaver.store
• المدونة: https://aidreamweaver.store/blog.html

**⚠️ ملاحظة:** البوت يستخدم Gemini 2.0 Flash مع حد 1,500 تفسير يومياً.
"""
    await update.message.reply_text(help_text)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض إحصائيات البوت"""
    leads = load_leads()
    stats_msg = (
        f"📊 **إحصائيات حالم**\n\n"
        f"👥 إجمالي المستخدمين: {leads['total_users']}\n"
        f"💭 إجمالي الأحلام المفسرة: {leads['dreams']}\n"
        f"🤖 النموذج المستخدم: Gemini 2.0 Flash\n"
        f"📅 الحد اليومي: 1,500 تفسير"
    )
    await update.message.reply_text(stats_msg)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الضغط على الأزرار"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "dream":
        await query.edit_message_text("📝 أرسل لي حلمك الآن وسأقوم بتفسيره.")
    elif query.data == "stats":
        leads = load_leads()
        await query.edit_message_text(
            f"📊 **إحصائيات حالم**\n\n"
            f"👥 المستخدمين: {leads['total_users']}\n"
            f"💭 الأحلام: {leads['dreams']}"
        )

# ========== دالة تفسير الأحلام باستخدام Gemini 2.0 Flash ==========
async def interpret_dream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تفسير الأحلام باستخدام Gemini 2.0 Flash"""
    user = update.effective_user
    dream = update.message.text
    
    # تسجيل التفاعل
    add_user(user.id, user.username, user.first_name)
    increment_dreams(user.id)
    
    if not GEMINI_API_KEY:
        await update.message.reply_text("❌ مفتاح Gemini غير متوفر حالياً.")
        return
    
    await update.message.reply_text("🔮 جاري التفسير باستخدام Gemini 2.0 Flash...")
    
    try:
        # استخدام Gemini 2.0 Flash (أعلى حد مجاني)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"فسر هذا الحلم باللغة العربية بأسلوب بسيط وشيق: {dream}"
                }]
            }]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            interpretation = result['candidates'][0]['content']['parts'][0]['text']
            await update.message.reply_text(f"✨ **تفسير حلمك:**\n\n{interpretation}")
            
        elif response.status_code == 429:
            # تجاوز الحد اليومي - رسالة مفيدة
            await update.message.reply_text(
                "⚠️ **وصلت للحد اليومي للتفسيرات المجانية**\n\n"
                "الحد الأقصى هو 1,500 تفسير يومياً. انتظر حتى الغد وسيعود الرصيد تلقائياً.\n\n"
                "شكراً لتفهمك! 🌙"
            )
            logger.warning(f"User {user.id} exceeded daily limit")
            
        else:
            error_text = response.text[:200]
            logger.error(f"Gemini error {response.status_code}: {error_text}")
            await update.message.reply_text(
                f"❌ حدث خطأ في التفسير (الرمز: {response.status_code})\n"
                "الرجاء المحاولة مرة أخرى لاحقاً."
            )
            
    except requests.exceptions.Timeout:
        await update.message.reply_text("❌ انتهت مهلة الاتصال. حاول مرة أخرى.")
    except requests.exceptions.ConnectionError:
        await update.message.reply_text("❌ مشكلة في الاتصال بالإنترنت. تحقق من اتصالك.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        await update.message.reply_text("❌ حدث خطأ غير متوقع. حاول مرة أخرى.")

# ========== الدالة الرئيسية ==========
def main():
    """تشغيل البوت النهائي"""
    print("🚀 بدء تشغيل بوت حالم النهائي...")
    print(f"   - Gemini 2.0 Flash: {'✅ مفعل' if GEMINI_API_KEY else '❌ غير مفعل'}")
    print(f"   - الحد اليومي: 1,500 تفسير")
    
    # إنشاء التطبيق
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, interpret_dream))
    
    print("✅ البوت شغال وجاهز!")
    
    # تشغيل البوت
    app.run_polling()

if __name__ == '__main__':
    main()
