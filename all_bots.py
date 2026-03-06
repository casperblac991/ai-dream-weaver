#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 AI DREAM WEAVER - البوت المتكامل النهائي
=============================================
- تفسير الأحلام (Gemini)
- توليد الصور (SiliconFlow)
- ترجمة عربية ← إنجليزية (Gemini)
- تقارير منظمة عن الأحلام
- أوامر المسؤول
- نظام تتبع العملاء
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

# ========== إعدادات المسؤول ==========
ADMIN_USER_ID = 6790340715  # ⚠️ تأكد من صحة هذا الرقم

# ========== المفاتيح من المتغيرات البيئية ==========
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
SILICONFLOW_KEY = os.environ.get('SILICONFLOW_API_KEY')

if not TELEGRAM_TOKEN:
    print("❌ خطأ: توكن تيليجرام غير موجود!")
    exit(1)

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

# ========== دوال البوت الأساسية ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username, user.first_name)
    
    welcome_msg = (
        f"مرحباً {user.first_name}! 🌙\n\n"
        "أنا بوت **حالم** المتكامل.\n\n"
        "✨ **الأوامر الأساسية:**\n"
        "• أرسل حلمك مباشرة للتفسير\n"
        "• /auto [وصف عربي] - ترجمة + توليد صورة\n"
        "• /report [حلم] - كتابة تقرير مفصل\n"
        "• /stats - إحصائيات\n\n"
        "📌 **أوامر المسؤول فقط:**\n"
        "• /genimage [وصف] - توليد صورة\n"
        "• /article [موضوع] - كتابة مقالة\n"
        "• /astats - إحصائيات مفصلة"
    )
    
    keyboard = [
        [InlineKeyboardButton("📝 تفسير حلم", callback_data="dream")],
        [InlineKeyboardButton("📚 المدونة", url="https://aidreamweaver.store/blog.html"),
         InlineKeyboardButton("🛒 المتجر", url="https://aidreamweaver.store")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🔍 **مساعدة البوت**

**📝 لتفسير حلمك:**
أرسل حلمك مباشرة (مثال: "حلمت أني أطير في السماء")

**🎨 لتوليد صورة:**
/auto [وصف عربي] - ترجمة + صورة
/genimage [وصف إنجليزي] - صورة مباشرة

**📊 للإحصائيات:**
/stats - إحصائيات البوت
/astats - إحصائيات مفصلة (للمسؤول)

**📄 للتقارير:**
/report [حلم] - كتابة تقرير مفصل

**🔗 روابط مفيدة:**
• المتجر: https://aidreamweaver.store
• المدونة: https://aidreamweaver.store/blog.html
"""
    await update.message.reply_text(help_text)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    query = update.callback_query
    await query.answer()
    if query.data == "dream":
        await query.edit_message_text("📝 أرسل لي حلمك الآن وسأقوم بتفسيره.")

# ========== دالة تفسير الأحلام ==========
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

# ========== دالة الترجمة (عربي ← إنجليزي) ==========
async def translate_to_english(text: str) -> str:
    """ترجمة النص العربي إلى إنجليزي باستخدام Gemini"""
    if not GEMINI_API_KEY:
        return text
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        prompt = f"Translate this Arabic text to English. Return ONLY the translation, no explanations:\n\n{text}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            translation = result['candidates'][0]['content']['parts'][0]['text']
            return translation.strip()
        else:
            return text
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text

# ========== دالة توليد الصور ==========
async def admin_genimage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """توليد صورة باستخدام SiliconFlow"""
    if not await is_admin(update):
        return

    if not context.args:
        await update.message.reply_text("⚠️ اكتب وصف الصورة: /genimage [وصف]")
        return

    prompt = " ".join(context.args)
    await update.message.reply_text("🎨 جاري توليد الصورة...")

    if not SILICONFLOW_KEY:
        await update.message.reply_text("❌ مفتاح SiliconFlow غير موجود.")
        return

    headers = {
        "Authorization": f"Bearer {SILICONFLOW_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "stabilityai/stable-diffusion-3-5-large",
        "prompt": prompt,
        "size": "1024x1024"
    }

    try:
        response = requests.post(
            "https://api.siliconflow.cn/v1/images/generations",
            headers=headers,
            json=data,
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            if 'images' in result and len(result['images']) > 0:
                image_url = result['images'][0]['url']
                await update.message.reply_photo(
                    photo=image_url,
                    caption=f"🎨 {prompt}"
                )
                increment_images(update.effective_user.id)
                return
            else:
                await update.message.reply_text("⚠️ الاستجابة لا تحتوي على صورة")
        else:
            error_message = response.text[:200]
            await update.message.reply_text(f"❌ فشل التوليد: {response.status_code}\n{error_message}")

    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في الاتصال: {str(e)}")

# ========== بوت الترجمة + توليد الصور ==========
async def auto_translate_and_generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """يترجم الأوصاف العربية وينشئ صوراً تلقائياً"""
    if not await is_admin(update):
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ مثال: /auto قطة بيضاء صغيرة")
        return
    
    arabic_prompt = " ".join(context.args)
    await update.message.reply_text(f"🌍 تم استلام: {arabic_prompt}\n⏳ جاري الترجمة...")
    
    # 1. ترجمة الوصف
    english_prompt = await translate_to_english(arabic_prompt)
    await update.message.reply_text(f"🇬🇧 الترجمة: {english_prompt}")
    
    # 2. توليد الصورة
    await update.message.reply_text("🎨 جاري توليد الصورة...")
    
    # استخدام دالة توليد الصور الموجودة
    context.args = english_prompt.split()
    await admin_genimage(update, context)

# ========== بوت كتابة تقارير منظمة ==========
async def generate_dream_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """يكتب تقريراً منظماً عن الحلم باستخدام Gemini"""
    if not await is_admin(update):
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ مثال: /report حلمت أني أطير في السماء")
        return
    
    dream = " ".join(context.args)
    await update.message.reply_text("📝 جاري كتابة تقرير مفصل عن الحلم...")
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        
        prompt = f"""
        اكتب تقريراً منظماً عن هذا الحلم باللغة العربية:
        
        الحلم: {dream}
        
        التقرير يجب أن يتضمن:
        1. **تحليل الحلم** - تفسير عام للحلم
        2. **الرموز الرئيسية** - شرح الرموز المهمة في الحلم
        3. **الدلالات النفسية** - ماذا يقول الحلم عن الحالة النفسية
        4. **توصيات** - نصائح للحالم
        
        استخدم تنسيق Markdown للعناوين والقوائم.
        """
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            report = result['candidates'][0]['content']['parts'][0]['text']
            
            # حفظ التقرير في الذاكرة للنشر لاحقاً
            context.user_data['last_report'] = {
                "dream": dream,
                "report": report,
                "date": str(datetime.now())
            }
            
            await update.message.reply_text(f"✅ تم إنشاء التقرير!\n\n{report}")
        else:
            await update.message.reply_text(f"❌ خطأ {response.status_code}")
            
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")

# ========== دوال المسؤول ==========
async def is_admin(update: Update) -> bool:
    user = update.effective_user
    if user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ هذا الأمر للمشرف فقط.")
        return False
    return True

async def admin_article(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ الرجاء كتابة موضوع المقالة.")
        return
    
    topic = " ".join(context.args)
    await update.message.reply_text(f"📝 جاري كتابة مقالة عن '{topic}'...")
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        prompt = f"""
        اكتب مقالة شاملة بالعربية عن '{topic}'.
        استخدم HTML للتنسيق: <h3> للعناوين، <p> للفقرات.
        """
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            article_content = result['candidates'][0]['content']['parts'][0]['text']
            context.user_data['last_article'] = {"title": topic, "content": article_content}
            await update.message.reply_text(f"✅ تمت كتابة المقالة!\n\n{article_content[:500]}...")
        else:
            await update.message.reply_text(f"❌ خطأ {response.status_code}")
            
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        f"• SiliconFlow: {'✅' if SILICONFLOW_KEY else '❌'}"
    )
    await update.message.reply_text(msg)

async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return
    
    help_msg = """
👑 **أوامر المسؤول**

• `/genimage [وصف]` - توليد صورة
• `/auto [وصف عربي]` - ترجمة + توليد صورة
• `/report [حلم]` - كتابة تقرير مفصل
• `/article [موضوع]` - كتابة مقالة
• `/astats` - إحصائيات مفصلة
    """
    await update.message.reply_text(help_msg)

# ========== الدالة الرئيسية ==========
def main():
    print("🚀 بدء تشغيل بوت حالم المتكامل...")
    print(f"   - Gemini: {'✅' if GEMINI_API_KEY else '❌'}")
    print(f"   - SiliconFlow: {'✅' if SILICONFLOW_KEY else '❌'}")
    print(f"   - المسؤول: {ADMIN_USER_ID}")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # أوامر المستخدمين
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, interpret_dream))
    
    # أوامر المسؤول
    app.add_handler(CommandHandler("genimage", admin_genimage))
    app.add_handler(CommandHandler("auto", auto_translate_and_generate))
    app.add_handler(CommandHandler("report", generate_dream_report))
    app.add_handler(CommandHandler("article", admin_article))
    app.add_handler(CommandHandler("astats", admin_stats))
    app.add_handler(CommandHandler("ahelp", admin_help))
    
    print("✅ البوت شغال!")
    app.run_polling()

if __name__ == '__main__':
    main()
