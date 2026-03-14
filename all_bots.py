#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import logging
import threading
import requests
import base64
import asyncio
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode, ChatAction

# =============================================
# خادم وهمي لـ Render المجاني
# =============================================
PORT = int(os.environ.get('PORT', 10000))

class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running')
    def log_message(self, format, *args): pass

def run_dummy_server():
    server = HTTPServer(('0.0.0.0', PORT), DummyServer)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()
print(f"✅ Dummy server running on port {PORT}")

# =============================================
# المتغيرات البيئية
# =============================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

if not TELEGRAM_TOKEN:
    print("❌ TELEGRAM_TOKEN غير موجود!")
    exit(1)

print(f"✅ TELEGRAM_TOKEN found: {TELEGRAM_TOKEN[:10]}...")
print(f"✅ GEMINI_API_KEY: {'موجود' if GEMINI_API_KEY else 'غير موجود'}")

# =============================================
# دالة تفسير الأحلام باستخدام Gemini
# =============================================
def interpret_dream(dream_text):
    if not GEMINI_API_KEY:
        return "❌ مفتاح Gemini غير موجود. أضفه في Environment Variables."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""أنت مفسر أحلام متخصص. فسر هذا الحلم باللغة العربية الفصحى بأسلوب واضح ومنظم:

الحلم: {dream_text}

اكتب تفسيراً يتضمن:
1. المعنى العام للحلم
2. دلالات الرموز الرئيسية
3. رسالة للحالم
4. نصيحة عملية"""
    
    try:
        response = requests.post(url, json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 800
            }
        }, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            return f"❌ خطأ في الاتصال بـ Gemini: {response.status_code}"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

# =============================================
# أوامر البوت
# =============================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌙 *مرحباً بك في بوت تفسير الأحلام*\n\n"
        "أرسل لي حلمك وسأفسره لك باستخدام الذكاء الاصطناعي.",
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dream = update.message.text.strip()
    
    if len(dream) < 10:
        await update.message.reply_text("❌ الرجاء إرسال وصف أطول للحلم (10 كلمات على الأقل).")
        return
    
    waiting_msg = await update.message.reply_text("🔮 *جاري تفسير حلمك...*\nقد يستغرق ذلك بضع ثوان.", parse_mode=ParseMode.MARKDOWN)
    
    result = interpret_dream(dream)
    
    await waiting_msg.delete()
    await update.message.reply_text(result, parse_mode=ParseMode.MARKDOWN)

# =============================================
# تشغيل البوت
# =============================================
def main():
    print("🚀 بدء تشغيل البوت...")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ البوت جاهز ويعمل...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
