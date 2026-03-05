import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً! أرسل لي حلمك وسأفسره.")

async def interpret_dream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dream = update.message.text
    await update.message.reply_text("🔮 جاري التفسير...")
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"فسر هذا الحلم بالعربية: {dream}")
        await update.message.reply_text(f"✨ {response.text}")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, interpret_dream))
    app.run_polling()

if __name__ == '__main__':
    main()
