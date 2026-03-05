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
    
    try:
        # الرابط الصحيح لاستدعاء Gemini API [citation:7]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        # هيكل الطلب الصحيح [citation:1][citation:7]
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"فسر هذا الحلم باللغة العربية: {dream}"
                }]
            }]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()  # إذا كان هناك خطأ، هذا السطر سيرميه
        
        result = response.json()
        interpretation = result['candidates'][0]['content']['parts'][0]['text']
        await update.message.reply_text(f"✨ {interpretation}")
        
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error: {http_err} - Response: {response.text}")
        await update.message.reply_text(f"❌ خطأ في الاتصال: {response.status_code}")
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("❌ حدث خطأ غير متوقع.")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, interpret_dream))
    app.run_polling()

if __name__ == '__main__':
    main()
