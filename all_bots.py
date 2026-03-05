#!/usr/bin/env python3
import os
import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً! أرسل لي حلمك وسأفسره.")

async def interpret_dream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dream = update.message.text
    await update.message.reply_text("🔮 جاري التفسير...")
    
    # --- بداية الكود التشخيصي ---
    await update.message.reply_text(f"1. تم استلام الحلم. جاري الاتصال بـ Gemini...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    await update.message.reply_text(f"2. عنوان URL الذي سأتصل به هو: {url.replace(GEMINI_API_KEY, 'API_KEY_MASKED')}")
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"فسر هذا الحلم باللغة العربية: {dream}"
            }]
        }]
    }
    await update.message.reply_text(f"3. البيانات المرسلة: {payload}")
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        await update.message.reply_text(f"4. تم استلام رد. رمز الحالة: {response.status_code}")
        
        if response.status_code != 200:
            await update.message.reply_text(f"5. محتوى الخطأ: {response.text[:500]}")  # أرسل أول 500 حرف من الخطأ
        else:
            result = response.json()
            interpretation = result['candidates'][0]['content']['parts'][0]['text']
            await update.message.reply_text(f"✅ {interpretation}")
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ غير متوقع: {str(e)}")
    # --- نهاية الكود التشخيصي ---

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, interpret_dream))
    app.run_polling()

if __name__ == '__main__':
    main()
