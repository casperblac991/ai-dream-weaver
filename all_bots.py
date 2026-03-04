#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 AI DREAM WEAVER - البوت الموحد المتكامل
============================================
يجمع كل الميزات في ملف واحد:
- تفسير الأحلام بالذكاء الاصطناعي
- نظام العملاء المحتملين
- بوت التحديثات الأسبوعية
- روابط دفع مباشرة
- رسائل متابعة ذكية
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, ContextTypes, CallbackQueryHandler
)

# ========== الإعدادات العامة ==========
STORE_URL = "https://aidreamweaver.store"
STORE_NAME = "AI Dream Weaver"

# المفاتيح من متغيرات البيئة
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
UNSPLASH_ACCESS_KEY = os.environ.get('UNSPLASH_ACCESS_KEY')

# روابط منتجات Gumroad
GUMROAD_LINKS = {
    "basic": "https://casperblac.gumroad.com/l/dtiobz",
    "premium": "https://casperblac.gumroad.com/l/byqzxd",
    "ultimate": "https://casperblac.gumroad.com/l/hiulqi"
}

# مجلد البيانات
DATA_DIR = "bot_data"
os.makedirs(DATA_DIR, exist_ok=True)

# معرف المشرف (استبدله بمعرفك)
ADMIN_CHAT_ID = 123456789  # ⚠️ غير هذا الرقم بمعرفك من @userinfobot

# ========== إعداد التسجيل ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ========== دالة مساعدة للطباعة ==========
def log(message: str, type: str = "info"):
    icons = {
        "info": "📘", "success": "✅", "warning": "⚠️",
        "error": "❌", "bot": "🤖", "lead": "👤"
    }
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {icons.get(type, 'ℹ️')} {message}")


# ========== كلاس إدارة البيانات ==========
class DataManager:
    def __init__(self):
        self.stats_file = os.path.join(DATA_DIR, "stats.json")
        self.load_data()

    def load_data(self):
        if not os.path.exists(self.stats_file):
            self.data = {"users": 0, "images_generated": 0}
            self.save_data()
        else:
            with open(self.stats_file, 'r') as f:
                self.data = json.load(f)

    def save_data(self):
        with open(self.stats_file, 'w') as f:
            json.dump(self.data, f)

    def get_stats(self):
        return self.data


# ========== كلاس إدارة العملاء المحتملين ==========
class LeadManager:
    def __init__(self):
        self.leads_file = os.path.join(DATA_DIR, "leads.json")
        self.load_leads()

    def load_leads(self):
        if not os.path.exists(self.leads_file):
            self.leads = {}
            self.save_leads()
        else:
            with open(self.leads_file, 'r') as f:
                self.leads = json.load(f)

    def save_leads(self):
        with open(self.leads_file, 'w') as f:
            json.dump(self.leads, f, indent=2)

    def add_lead(self, user_id, username, first_name, dream_text=""):
        user_id = str(user_id)
        now = str(datetime.now())
        
        if user_id not in self.leads:
            self.leads[user_id] = {
                "user_id": user_id,
                "username": username,
                "first_name": first_name,
                "first_interaction": now,
                "last_interaction": now,
                "dreams": [dream_text] if dream_text else [],
                "dream_count": 1 if dream_text else 0,
                "total_interactions": 1,
                "plan_purchased": None,
                "lead_score": 10
            }
        else:
            self.leads[user_id]["last_interaction"] = now
            if dream_text:
                self.leads[user_id]["dreams"].append(dream_text)
                self.leads[user_id]["dream_count"] += 1
            self.leads[user_id]["total_interactions"] += 1
            self.leads[user_id]["lead_score"] += 5
        
        self.save_leads()
        return self.leads[user_id]

    def get_hot_leads(self, min_score=30):
        """العملاء الأكثر اهتماماً"""
        return [l for l in self.leads.values() if l["lead_score"] >= min_score]

    def mark_purchased(self, user_id, plan):
        user_id = str(user_id)
        if user_id in self.leads:
            self.leads[user_id]["plan_purchased"] = plan
            self.leads[user_id]["lead_score"] = 100
            self.save_leads()


# ========== كلاس التقارير الأسبوعية ==========
class WeeklyReportBot:
    def __init__(self, lead_manager):
        self.lead_manager = lead_manager
        self.report_file = os.path.join(DATA_DIR, "weekly_reports.json")
        self.load_reports()

    def load_reports(self):
        if os.path.exists(self.report_file):
            with open(self.report_file, 'r') as f:
                self.reports = json.load(f)
        else:
            self.reports = {"last_report": None, "reports": []}

    def save_reports(self):
        with open(self.report_file, 'w') as f:
            json.dump(self.reports, f, indent=2)

    def generate_weekly_stats(self):
        """توليد إحصائيات الأسبوع"""
        leads = self.lead_manager.leads
        week_ago = datetime.now() - timedelta(days=7)
        
        stats = {
            "date": str(datetime.now()),
            "new_leads": 0,
            "active_users": 0,
            "new_purchases": 0,
            "revenue": 0.0,
            "hot_leads": 0,
            "total_leads": len(leads),
            "total_purchases": 0
        }
        
        for user_id, data in leads.items():
            last = datetime.fromisoformat(data["last_interaction"])
            first = datetime.fromisoformat(data["first_interaction"])
            
            if first > week_ago:
                stats["new_leads"] += 1
            if last > week_ago:
                stats["active_users"] += 1
            if data.get("plan_purchased"):
                stats["total_purchases"] += 1
                if last > week_ago:
                    stats["new_purchases"] += 1
                    if data["plan_purchased"] == "basic":
                        stats["revenue"] += 4.99
                    elif data["plan_purchased"] == "premium":
                        stats["revenue"] += 9.99
                    elif data["plan_purchased"] == "ultimate":
                        stats["revenue"] += 19.99
            if data.get("lead_score", 0) > 50 and not data.get("plan_purchased"):
                stats["hot_leads"] += 1
        
        return stats

    def format_report(self, stats):
        report = f"""
📊 **التقرير الأسبوعي للمتجر**
📅 التاريخ: {stats['date'][:10]}

━━━━━━━━━━━━━━━━━━━
**📈 إحصائيات عامة**
• إجمالي العملاء: {stats['total_leads']}
• عملاء جدد: {stats['new_leads']}
• مستخدمين نشطين: {stats['active_users']}

**💰 المبيعات**
• مشتريات جديدة: {stats['new_purchases']}
• إيرادات الأسبوع: ${stats['revenue']:.2f}
• إجمالي المشتريات: {stats['total_purchases']}

**🔥 فرص تسويقية**
• عملاء محتملين: {stats['hot_leads']}

━━━━━━━━━━━━━━━━━━━
"""
        return report

    async def send_weekly_report(self, context, chat_id):
        stats = self.generate_weekly_stats()
        report = self.format_report(stats)
        await context.bot.send_message(
            chat_id=chat_id,
            text=report,
            parse_mode='Markdown'
        )
        self.reports["last_report"] = stats
        self.reports["reports"].append(stats)
        self.save_reports()


# ========== معالجات البوت ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة الترحيب"""
    user = update.effective_user
    lead_manager = context.bot_data.get('lead_manager')
    
    if lead_manager:
        lead_manager.add_lead(user.id, user.username, user.first_name)
    
    welcome_msg = (
        f"مرحباً {user.first_name}! 🌙\n\n"
        "أنا بوت **حالم** لتفسير الأحلام بالذكاء الاصطناعي.\n"
        "أرسل لي حلمك وسأقوم بتفسيره لك.\n\n"
        "✨ **مميزاتي:**\n"
        "• تفسير عميق بالذكاء الاصطناعي\n"
        "• مراعاة الثقافة العربية\n"
        "• إمكانية توليد الصور (في الخطط المدفوعة)\n\n"
        "📌 **الأوامر المتاحة:**\n"
        "/start - بدء المحادثة\n"
        "/plans - عرض خطط الأسعار\n"
        "/help - مساعدة"
    )
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مساعدة"""
    help_text = """
🔍 **مساعدة البوت**

**كيفية الاستخدام:**
• أرسل لي حلمك وسأقوم بتفسيره
• للحصول على تفسير أعمق، اشترك في الخطة المناسبة

**الأوامر:**
/start - بدء المحادثة
/plans - عرض خطط الأسعار
/report - عرض تقرير المبيعات (للمشرف)
/leads - عرض العملاء المحتملين (للمشرف)

**خطط الأسعار:**
• الأساسية: $4.99 - تفسير + صور محدودة
• الاحترافية: $9.99 - صور 4K غير محدودة
• النهائية: $19.99 - كل المميزات + API

استمتع بتجربة تفسير الأحلام! ✨
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def plans_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض خطط الأسعار"""
    keyboard = [
        [InlineKeyboardButton("⭐ الأساسية - $4.99", callback_data="plan_basic")],
        [InlineKeyboardButton("🔥 الاحترافية - $9.99", callback_data="plan_premium")],
        [InlineKeyboardButton("👑 النهائية - $19.99", callback_data="plan_ultimate")],
        [InlineKeyboardButton("📞 دعم فني", url="https://t.me/your_support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🚀 **اختر خطتك المناسبة:**\n\n"
        "⭐ **الأساسية $4.99**\n"
        "• تفسير غير محدود\n"
        "• صور محدودة\n"
        "• يوميات أساسية\n\n"
        "🔥 **الاحترافية $9.99**\n"
        "• صور 4K غير محدودة\n"
        "• +50 أسلوب فني\n"
        "• تحليل الأنماط الشهرية\n\n"
        "👑 **النهائية $19.99**\n"
        "• كل مميزات الاحترافية\n"
        "• تحريك الأحلام\n"
        "• API للمطورين",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الضغط على الأزرار"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    lead_manager = context.bot_data.get('lead_manager')
    
    plan_messages = {
        "plan_basic": {
            "name": "الأساسية",
            "link": GUMROAD_LINKS['basic'],
            "price": "4.99"
        },
        "plan_premium": {
            "name": "الاحترافية",
            "link": GUMROAD_LINKS['premium'],
            "price": "9.99"
        },
        "plan_ultimate": {
            "name": "النهائية",
            "link": GUMROAD_LINKS['ultimate'],
            "price": "19.99"
        }
    }
    
    if query.data in plan_messages:
        plan = plan_messages[query.data]
        await query.edit_message_text(
            f"✅ **تم اختيار الخطة {plan['name']}**\n\n"
            f"للشراء، اضغط على الرابط التالي:\n"
            f"{plan['link']}\n\n"
            "بعد الشراء، سيتم تفعيل اشتراكك تلقائياً.",
            parse_mode='Markdown'
        )
        if lead_manager:
            lead_manager.mark_purchased(user.id, query.data.replace("plan_", ""))


async def handle_dream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة رسائل الأحلام"""
    user = update.effective_user
    dream_text = update.message.text
    
    lead_manager = context.bot_data.get('lead_manager')
    if lead_manager:
        lead_manager.add_lead(user.id, user.username, user.first_name, dream_text)
    
    # هنا يمكنك إضافة دالة تفسير الأحلام باستخدام OpenAI
    # حالياً سأرسل رداً وهمياً
    await update.message.reply_text(
        f"🌙 **تفسير حلمك:**\n\n"
        f"'{dream_text}'\n\n"
        "هذا تفسير تجريبي. للحصول على تفسير دقيق، قم بترقية اشتراكك.\n\n"
        "👉 استخدم الأمر /plans لعرض خطط الأسعار",
        parse_mode='Markdown'
    )


# ========== أوامر المشرف ==========
async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إرسال التقرير الأسبوعي (للمشرف فقط)"""
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ هذا الأمر للمشرف فقط.")
        return
    
    report_bot = context.bot_data.get('report_bot')
    if report_bot:
        await report_bot.send_weekly_report(context, update.effective_chat.id)


async def leads_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض العملاء المحتملين (للمشرف فقط)"""
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ هذا الأمر للمشرف فقط.")
        return
    
    lead_manager = context.bot_data.get('lead_manager')
    if not lead_manager:
        return
    
    hot_leads = lead_manager.get_hot_leads()
    
    if not hot_leads:
        await update.message.reply_text("لا يوجد عملاء محتملين حالياً.")
        return
    
    message = "🔥 **العملاء المحتملين:**\n\n"
    for lead in hot_leads[:10]:
        message += f"• {lead.get('first_name', 'مستخدم')} "
        if lead.get('username'):
            message += f"(@{lead['username']}) "
        message += f"- درجة {lead['lead_score']}\n"
        message += f"  أحلام: {lead['dream_count']}\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')


# ========== الدالة الرئيسية ==========
def main():
    """تشغيل البوت"""
    log("🚀 بدء تشغيل البوت الموحد...", "bot")
    
    # التأكد من وجود التوكن
    if not TELEGRAM_TOKEN:
        log("❌ توكن تيليجرام غير موجود!", "error")
        return
    
    # تهيئة المديرين
    data_manager = DataManager()
    lead_manager = LeadManager()
    report_bot = WeeklyReportBot(lead_manager)
    
    # إنشاء التطبيق
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # تخزين الكلاسات في بيانات التطبيق
    app.bot_data['data_manager'] = data_manager
    app.bot_data['lead_manager'] = lead_manager
    app.bot_data['report_bot'] = report_bot
    
    # إضافة معالجات الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("plans", plans_command))
    app.add_handler(CommandHandler("report", report_command))
    app.add_handler(CommandHandler("leads", leads_command))
    
    # معالج الرسائل النصية
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_dream))
    
    # معالج الأزرار
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # جدولة التقارير الأسبوعية
    if ADMIN_CHAT_ID != 123456789:
        job_queue = app.job_queue
        
        # تقرير كل يوم أحد الساعة 10 صباحاً
        job_queue.run_daily(
            lambda ctx: report_bot.send_weekly_report(ctx, ADMIN_CHAT_ID),
            time=datetime.time(hour=10, minute=0),
            days=(6,)  # الأحد
        )
    
    log("✅ البوت شغال بنجاح!", "success")
    stats = data_manager.get_stats()
    log(f"📊 الإحصائيات: {stats}", "info")
    
    # تشغيل البوت
    app.run_polling()


if __name__ == "__main__":
    main()
