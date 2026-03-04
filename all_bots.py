#!/usr/bin/env python3
import os
import logging
import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

openai.api_key = OPENAI_API_KEY
openai.base_url = "https://openrouter.ai/api/v1"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً! أرسل لي حلمك وسأفسره بالذكاء الاصطناعي.")

async def interpret_dream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dream = update.message.text
    await update.message.reply_text("🔮 جاري التفسير...")
    
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت مفسر أحلام متخصص باللغة العربية."},
                {"role": "user", "content": f"فسر هذا الحلم: {dream}"}
            ]
        )
        interpretation = response.choices[0].message.content
        await update.message.reply_text(f"✨ {interpretation}")
    except Exception as e:
        await update.message.reply_text("❌ حدث خطأ. حاول مرة أخرى.")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, interpret_dream))
    app.run_polling()

if __name__ == '__main__':
    main()
