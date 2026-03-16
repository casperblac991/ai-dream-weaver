#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

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

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

if not TELEGRAM_TOKEN:
    print("❌ TELEGRAM_TOKEN غير موجود!")
    exit(1)

print(f"✅ TELEGRAM_TOKEN found: {TELEGRAM_TOKEN[:10]}...")
print(f"✅ GEMINI_API_KEY: {'موجود' if GEMINI_API_KEY else 'غير موجود'}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌙 *مرحباً بك في بوت Weaver*\n\n"
        "أرسل لي حلمك وسأفسره لك.",
        parse_mode="Markdown"
    )

def main():
    print("🚀 بدء تشغيل البوت...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("✅ البوت جاهز ويعمل...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
