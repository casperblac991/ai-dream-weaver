#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weaver (نَسَّاج) - تشغيل المنصة والبوت معاً v3.0
"""
import os
import threading
import uvicorn
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from app.main import app as fastapi_app

PORT = int(os.environ.get('PORT', 10000))
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")

# --- بوت تيليجرام ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌙 *مرحباً بك في بوت Weaver*\n\n"
        "أرسل لي حلمك وسأفسره لك بالذكاء الاصطناعي.\n"
        "أو زر موقعنا: https://aidreamweaver.store",
        parse_mode="Markdown"
    )

def run_telegram_bot():
    if not TELEGRAM_TOKEN:
        print("⚠️ TELEGRAM_TOKEN غير موجود، سيتم تشغيل الموقع فقط.")
        return
    
    print("🚀 بدء تشغيل بوت تيليجرام...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    print("✅ البوت جاهز ويعمل...")
    application.run_polling(drop_pending_updates=True)

# --- تشغيل المنصة ---
if __name__ == "__main__":
    # تشغيل البوت في خيط منفصل
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    
    # تشغيل تطبيق FastAPI (المنصة)
    print(f"🚀 بدء تشغيل المنصة على المنفذ {PORT}...")
    uvicorn.run(fastapi_app, host="0.0.0.0", port=PORT)
