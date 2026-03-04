#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 AI DREAM WEAVER - بوت تفسير الأحلام
========================================
بوت تيليجرام يعمل على justrunmy.app
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== التوكن من المتغيرات البيئية ==========
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

# التحقق من وجود التوكن
if not TELEGRAM_TOKEN:
    print("❌ خطأ: توكن تيليجرام غير موجود!")
    exit(1)

# ========== إعداد التسجيل ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== دالة بدء المحادثة ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة الترحيب"""
    user = update.effective_user
    await update.message.reply_text(
        f"مرحباً {user.first_name}! 🌙\n\n"
        "أنا بوت **حالم** لتفسير الأحلام.\n"
        "أرسل لي حلمك وسأقوم بتفسيره قريباً.\n\n"
        "🚧 هذا الإصدار تجريبي - التفسير الفعلي قيد التطوير."
    )

# ========== دالة المساعدة ==========
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة المساعدة"""
    await update.message.reply_text(
        "🔍 **مساعدة البوت**\n\n"
        "• أرسل لي أي حلم وسأحاول تفسيره\n"
        "• /start - بدء المحادثة\n"
        "• /help - عرض هذه المساعدة"
    )

# ========== دالة معالجة الأحلام ==========
async def handle_dream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """استقبال الحلم والرد عليه"""
    user_message = update.message.text
    
    # هنا يمكنك إضافة الاتصال بـ OpenRouter لاحقاً
    await update.message.reply_text(
        f"🌙 **حلمك:** {user_message}\n\n"
        "📢 هذا رد تجريبي. قريباً سيعمل التفسير الفعلي بالذكاء الاصطناعي.\n\n"
        "تابعنا للمزيد!"
    )

# ========== الدالة الرئيسية ==========
def main():
    """تشغيل البوت"""
    print("🚀 بدء تشغيل البوت...")
    
    # إنشاء التطبيق
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_dream))
    
    print("✅ البوت شغال وجاهز لاستقبال الرسائل!")
    
    # تشغيل البوت
    app.run_polling()

if __name__ == '__main__':
    main()
