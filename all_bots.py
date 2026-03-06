#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 AI DREAM WEAVER - بوت المدير الذكي لمتجر حالم
====================================================
- تفسير الأحلام للمستخدمين (Gemini 2.0 Flash)
- أوامر المسؤول لكتابة ونشر المقالات
- توليد الصور (PixVerse)
- نظام تتبع العملاء
- إحصائيات وتقارير
"""

import os
import json
import time
import requests
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# ========== إعدادات المسؤول ==========
# معرف المسؤول من @userinfobot
ADMIN_USER_ID = 6790340715

# ========== المفاتيح من المتغيرات البيئية ==========
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
PIXVERSE_API_KEY = os.environ.get('PIXVERSE_API_KEY')

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
        "أستخدم **Gemini 2.0 Flash** لتفسير الأحلام (1,500 تفسير مجاني يومياً).\n\n"
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

# ========== دالة تفسير الأحلام (للمستخدمين) ==========
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
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": f"فسر هذا الحلم بالعربية بأسلوب بسيط: {dream}"}]}]}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            interpretation = result['candidates'][0]['content']['parts'][0]['text']
            await update.message.reply_text(f"✨ **تفسير حلمك:**\n\n{interpretation}")
        elif response.status_code == 429:
            await update.message.reply_text(
                "⚠️ وصلت للحد اليومي للتفسيرات (1,500). انتظر حتى الغد."
            )
        else:
            await update.message.reply_text(f"❌ خطأ {response.status_code}")
            
    except Exception as e:
        logger.error(f"خطأ في التفسير: {str(e)}")
        await update.message.reply_text("❌ حدث خطأ. حاول مرة أخرى.")

# ========== دوال المسؤول (Admin Commands) ==========
async def is_admin(update: Update) -> bool:
    """التحقق من أن المستخدم هو المسؤول"""
    user = update.effective_user
    if user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ هذا الأمر للمشرف فقط.")
        return False
    return True

async def admin_article(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر المسؤول: كتابة مقالة جديدة (للمشرف فقط)"""
    if not await is_admin(update):
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ الرجاء كتابة موضوع المقالة.\n"
            "مثال: `/article تفسير الأحلام في بلاد الرافدين`"
        )
        return
    
    topic = " ".join(context.args)
    await update.message.reply_text(f"📝 جاري كتابة مقالة عن '{topic}'...")
    
    try:
        # طلب المقالة من Gemini
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        prompt = f"""
        اكتب مقالة شاملة باللغة العربية عن '{topic}'.
        يجب أن تتضمن المقالة:
        - مقدمة شيقة
        - 3-5 عناوين فرعية (مقسمة بـ <h3>)
        - فقرات تحت كل عنوان
        - خاتمة مفيدة
        
        استخدم تنسيق HTML مناسب للنشر في مدونة.
        """
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            article_content = result['candidates'][0]['content']['parts'][0]['text']
            
            # حفظ المقالة في context للاستخدام لاحقاً
            context.user_data['last_article'] = {
                "title": topic,
                "content": article_content
            }
            
            # إرسال المقالة للمراجعة
            preview = article_content[:500] + "..." if len(article_content) > 500 else article_content
            await update.message.reply_text(
                f"✅ تمت كتابة المقالة!\n\n"
                f"**معاينة:**\n{preview}\n\n"
                f"لاستكمال النشر، استخدم:\n"
                f"`/publish` - لنشر المقالة في المدونة\n"
                f"`/genimage [وصف]` - لتوليد صورة للمقالة"
            )
        else:
            await update.message.reply_text(f"❌ خطأ في كتابة المقالة: {response.status_code}")
            
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")

async def admin_publish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر المسؤول: نشر المقالة في المدونة"""
    if not await is_admin(update):
        return
    
    if 'last_article' not in context.user_data:
        await update.message.reply_text("⚠️ لا توجد مقالة في الذاكرة. استخدم `/article` أولاً.")
        return
    
    article = context.user_data['last_article']
    
    await update.message.reply_text("📤 جاري نشر المقالة في المدونة...")
    
    # هنا يمكن إضافة كود نشر المقالة في GitHub
    # للتبسيط، سنقوم بإنشاء ملف HTML جديد للمقالة
    
    try:
        # توليد اسم ملف آمن من عنوان المقالة
        safe_title = article['title'].replace(' ', '-').replace('/', '-')[:30]
        filename = f"article-{safe_title}.html"
        
        # إنشاء محتوى HTML كامل للمقالة
        html_content = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title']} - حالم</title>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800;900&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Tajawal', sans-serif; background: #0a0514; color: #e2d9f3; padding: 2rem; line-height: 1.8; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #f0c060; text-align: center; margin-bottom: 2rem; }}
        h3 {{ color: #a855f7; margin-top: 2rem; }}
        .back-link {{ display: block; text-align: center; margin-top: 3rem; color: #f0c060; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{article['title']}</h1>
        {article['content']}
        <hr>
        <p style="text-align: center; color: rgba(226,217,243,0.5);">📅 {datetime.now().strftime('%Y-%m-%d')} | منصة حالم - تفسير الأحلام بالذكاء الاصطناعي</p>
        <a href="blog.html" class="back-link">← العودة للمدونة</a>
    </div>
</body>
</html>"""
        
        # إرسال المحتوى للمراجعة
        await update.message.reply_text(
            f"✅ **تم تجهيز المقالة للنشر!**\n\n"
            f"**الملف:** `{filename}`\n\n"
            f"**لنشرها فعلياً، تحتاج إلى:**\n"
            f"1. إنشاء هذا الملف في مستودع GitHub (`casperblac991/ai-dream-weaver`)\n"
            f"2. تحديث صفحة `blog.html` برابط المقالة الجديدة\n\n"
            f"يمكنك نسخ محتوى المقالة من الأسفل:\n\n"
            f"```html\n{html_content[:1000]}...```"
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في النشر: {str(e)}")

async def admin_genimage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر المسؤول: توليد صورة باستخدام PixVerse"""
    if not await is_admin(update):
        return
    
    if not PIXVERSE_API_KEY:
        await update.message.reply_text("❌ مفتاح PixVerse غير متوفر.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ الرجاء كتابة وصف الصورة.\n"
            "مثال: `/genimage شخص يطير في السماء، ألوان بنفسجية`"
        )
        return
    
    prompt = " ".join(context.args)
    await update.message.reply_text("🎨 جاري توليد الصورة...")
    
    try:
        # الاتصال بـ PixVerse API
        url = "https://api.pixverse.ai/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {PIXVERSE_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "prompt": prompt,
            "aspect_ratio": "1:1",
            "style": "fantasy"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            image_url = result.get('data', [{}])[0].get('url')
            if image_url:
                await update.message.reply_photo(photo=image_url, caption=f"🎨 {prompt}")
            else:
                await update.message.reply_text("❌ لم يتم العثور على رابط الصورة")
        else:
            await update.message.reply_text(f"❌ خطأ {response.status_code}")
            
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إحصائيات مفصلة للمسؤول"""
    if not await is_admin(update):
        return
    
    stats = get_stats()
    leads = load_leads()
    
    # إحصائيات المستخدمين النشطين
    active_users = []
    now = datetime.now()
    for user in leads['users']:
        last = datetime.fromisoformat(user['last_seen'])
        days = (now - last).days
        if days <= 7:
            active_users.append(user)
    
    msg = (
        f"📊 **تقرير المسؤول**\n\n"
        f"👥 إجمالي المستخدمين: {stats['total_users']}\n"
        f"👤 نشط آخر 7 أيام: {len(active_users)}\n"
        f"💭 إجمالي الأحلام: {stats['total_dreams']}\n"
        f"🎨 إجمالي الصور: {stats['total_images']}\n"
        f"📝 المقالات المنشورة: {stats['total_articles']}\n"
        f"📅 نشط اليوم: {stats['active_today']}\n\n"
        f"**المفاتيح:**\n"
        f"• Gemini: {'✅' if GEMINI_API_KEY else '❌'}\n"
        f"• PixVerse: {'✅' if PIXVERSE_API_KEY else '❌'}\n"
    )
    
    await update.message.reply_text(msg)

async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مساعدة المسؤول"""
    if not await is_admin(update):
        return
    
    help_msg = """
👑 **أوامر المسؤول**

**المحتوى:**
• `/article [موضوع]` - كتابة مقالة جديدة
• `/publish` - نشر المقالة الأخيرة في المدونة
• `/genimage [وصف]` - توليد صورة

**الإحصائيات:**
• `/astats` - إحصائيات مفصلة

**المستخدمين:**
• كل أوامر المستخدم العادي تعمل أيضاً
    """
    await update.message.reply_text(help_msg)

# ========== الدالة الرئيسية ==========
def main():
    """تشغيل البوت"""
    print("🚀 بدء تشغيل بوت المدير الذكي...")
    print(f"   - Gemini: {'✅' if GEMINI_API_KEY else '❌'}")
    print(f"   - PixVerse: {'✅' if PIXVERSE_API_KEY else '❌'}")
    print(f"   - معرف المسؤول: {ADMIN_USER_ID}")
    
    # إنشاء التطبيق
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # أوامر المستخدمين العادية
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, interpret_dream))
    
    # أوامر المسؤول
    app.add_handler(CommandHandler("article", admin_article))
    app.add_handler(CommandHandler("publish", admin_publish))
    app.add_handler(CommandHandler("genimage", admin_genimage))
    app.add_handler(CommandHandler("astats", admin_stats))
    app.add_handler(CommandHandler("ahelp", admin_help))
    
    print("✅ البوت شغال وجاهز!")
    
    # تشغيل البوت
    app.run_polling()

if __name__ == '__main__':
    main()
