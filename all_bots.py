#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 AI DREAM WEAVER - بوت تفسير الأحلام مع نظام تتبع العملاء
===============================================================
"""

import os
import json
import logging
import openai
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== التوكنات من المتغيرات البيئية ==========
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# التحقق من وجود التوكنات
if not TELEGRAM_TOKEN:
    print("❌ خطأ: توكن تيليجرام غير موجود!")
    exit(1)

if not OPENAI_API_KEY:
    print("❌ خطأ: مفتاح OpenRouter غير موجود!")
    exit(1)

# ========== إعداد OpenRouter ==========
openai.api_key = OPENAI_API_KEY
openai.base_url = "https://openrouter.ai/api/v1"

# ========== إعداد التسجيل ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== نظام تتبع العملاء ==========
class LeadTracker:
    def __init__(self):
        self.leads_file = "leads.json"
        self.load_leads()
    
    def load_leads(self):
        """تحميل بيانات العملاء من ملف JSON"""
        try:
            with open(self.leads_file, 'r', encoding='utf-8') as f:
                self.leads = json.load(f)
        except FileNotFoundError:
            # إذا الملف مش موجود، ننشئه
            self.leads = {
                "total_users": 0,
                "total_images": 0,
                "users": [],
                "last_updated": str(datetime.now())
            }
            self.save_leads()
        except json.JSONDecodeError:
            # إذا الملف فيه مشكلة، ننشئه من جديد
            self.leads = {
                "total_users": 0,
                "total_images": 0,
                "users": [],
                "last_updated": str(datetime.now())
            }
            self.save_leads()
    
    def save_leads(self):
        """حفظ بيانات العملاء في ملف JSON"""
        self.leads["last_updated"] = str(datetime.now())
        with open(self.leads_file, 'w', encoding='utf-8') as f:
            json.dump(self.leads, f, indent=2, ensure_ascii=False)
    
    def add_user(self, user_id, username, first_name):
        """إضافة مستخدم جديد أو تحديث آخر تفاعل له"""
        user_id_str = str(user_id)
        now = str(datetime.now())
        
        # البحث عن المستخدم في القائمة
        for user in self.leads["users"]:
            if user["user_id"] == user_id_str:
                # المستخدم موجود → نحدث آخر تفاعل
                user["last_interaction"] = now
                user["interaction_count"] += 1
                self.save_leads()
                return False
        
        # مستخدم جديد → نضيفه
        new_user = {
            "user_id": user_id_str,
            "username": username,
            "first_name": first_name,
            "first_seen": now,
            "last_interaction": now,
            "interaction_count": 1
        }
        self.leads["users"].append(new_user)
        self.leads["total_users"] += 1
        self.save_leads()
        return True
    
    def add_image(self):
        """زيادة عداد الصور المولدة"""
        self.leads["total_images"] += 1
        self.save_leads()
    
    def get_stats(self):
        """إرجاع إحصائيات سريعة"""
        today = datetime.now().date()
        today_users = 0
        today_images = 0  # هذا مؤقت، يمكن تطويره لاحقاً
        
        for user in self.leads["users"]:
            last_date = datetime.fromisoformat(user["last_interaction"]).date()
            if last_date == today:
                today_users += 1
        
        return {
            "total_users": self.leads["total_users"],
            "total_images": self.leads["total_images"],
            "active_today": today_users,
            "users_count": len(self.leads["users"])
        }

# إنشاء كائن التتبع
tracker = LeadTracker()

# ========== دوال البوت ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة الترحيب مع تسجيل المستخدم"""
    user = update.effective_user
    
    # تسجيل المستخدم
    is_new = tracker.add_user(user.id, user.username, user.first_name)
    
    welcome_msg = (
        f"مرحباً {user.first_name}! 🌙\n\n"
        "أنا بوت **حالم** لتفسير الأحلام بالذكاء الاصطناعي.\n"
        "أرسل لي حلمك وسأقوم بتفسيره لك.\n\n"
        "✨ **مثال:** حلمت أني أطير في السماء\n\n"
        f"📊 إحصائيات: {tracker.get_stats()['total_users']} مستخدم حتى الآن"
    )
    
    await update.message.reply_text(welcome_msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة المساعدة"""
    await update.message.reply_text(
        "🔍 **مساعدة البوت**\n\n"
        "• أرسل لي أي حلم وسأفسره لك\n"
        "• /start - بدء المحادثة\n"
        "• /help - عرض هذه المساعدة\n"
        "• /stats - عرض إحصائيات البوت"
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض إحصائيات البوت للمشرف"""
    user = update.effective_user
    
    # يمكنك تحديد مشرفين معينين هنا (اختياري)
    # if user.id != ADMIN_ID:
    #     await update.message.reply_text("⛔ هذا الأمر للمشرف فقط.")
    #     return
    
    stats = tracker.get_stats()
    
    stats_msg = (
        f"📊 **إحصائيات حالم**\n\n"
        f"👥 إجمالي المستخدمين: {stats['total_users']}\n"
        f"🖼️ الصور المولدة: {stats['total_images']}\n"
        f"📅 نشط اليوم: {stats['active_today']}\n"
        f"📋 عدد السجلات: {stats['users_count']}"
    )
    
    await update.message.reply_text(stats_msg)

async def interpret_dream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """استقبال الحلم وتفسيره باستخدام OpenRouter"""
    user = update.effective_user
    dream = update.message.text
    
    # تسجيل التفاعل
    tracker.add_user(user.id, user.username, user.first_name)
    
    # إرسال رسالة انتظار
    await update.message.reply_text("🔮 جاري التفسير...")
    
    try:
        # الاتصال بـ OpenRouter
        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": "أنت مفسر أحلام متخصص باللغة العربية. فسر الأحلام بأسلوب بسيط وشيق. اجعل التفسير مفيداً ومراعياً للثقافة العربية."
                },
                {
                    "role": "user", 
                    "content": f"فسر هذا الحلم: {dream}"
                }
            ]
        )
        
        # استخراج التفسير
        interpretation = response.choices[0].message.content
        
        # إرسال التفسير للمستخدم
        await update.message.reply_text(
            f"✨ **تفسير حلمك:**\n\n{interpretation}\n\n"
            "🌟 شاركنا حلمك القادم!"
        )
        
    except Exception as e:
        logger.error(f"خطأ في التفسير: {e}")
        await update.message.reply_text(
            "❌ حدث خطأ في التفسير. الرجاء المحاولة مرة أخرى لاحقاً.\n"
            "يمكنك التواصل مع الدعم عبر @aidreamweaver_bot"
        )

# ========== الدالة الرئيسية ==========
def main():
    """تشغيل البوت"""
    print("🚀 بدء تشغيل البوت مع نظام تتبع العملاء...")
    
    # إنشاء التطبيق
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, interpret_dream))
    
    print("✅ البوت شغال وجاهز لتفسير الأحلام!")
    print(f"📊 إحصائيات أولية: {tracker.get_stats()}")
    
    # تشغيل البوت
    app.run_polling()

if __name__ == '__main__':
    main()
