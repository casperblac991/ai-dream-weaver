#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weaver (نَسَّاج) - بوت تيليجرام المتكامل
v4.0 مع handlers كاملة
"""
import os
import sys
import threading
import asyncio
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# الإعدادات
PORT = int(os.environ.get('PORT', 10000))
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
api_url = os.environ.get("API_URL", "https://aidreamweaver.store")

# ============================================
# handlers البوت
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start command"""
    await update.message.reply_text(
        "🌙 *مرحباً بك في نَسَّاج*\n\n"
        "🔮 منصة تفسير الأحلام بالذكاء الاصطناعي\n\n"
        "*الأوامر:*\n"
        "/start -_start_\n"
        "/dream <حلمك> - تفسير الحلم\n"
        "/stats - إحصائيات المنصة\n"
        "/help - المساعدة\n\n"
        "_أرسل لي حلمك وسأفسره لك!_",
        parse_mode="Markdown"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مساعدة"""
    await update.message.reply_text(
        "🔮 *مساعدة نَسَّاج*\n\n"
        "• /dream <نص> - فسّر حلمك\n"
        "• أرسل الحلم مباشرة - فسّر تلقائي\n"
        "• /stats - إحصائيات\n"
        "• /blog - أحدث المقالات\n\n"
        "_جرب:_ `/dream رأيت ثعباناً`",
        parse_mode="Markdown"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إحصائيات"""
    try:
        r = requests.get(f"{api_url}/api/stats", timeout=10)
        if r.ok:
            s = r.json()
            await update.message.reply_text(
                f"📊 *إحصائيات نَسَّاج*\n\n"
                f"👥 {s.get('users', 0)} مستخدم\n"
                f"🌙 {s.get('dreams', 0)} حلم مُفسَّر\n"
                f"📈 {s.get('views', 0)} مشاهدة",
                parse_mode="Markdown"
            )
    except Exception as e:
        await update.message.reply_text("⚠️ تعذر جلب الإحصائيات")

async def interpret_dream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تفسير الأحلام"""
    text = update.message.text.strip()
    
    # تخطي الأوامر
    if text.startswith('/'):
        return
    
    # إزالة /dream إن وُجد
    if text.lower().startswith('/dream'):
        text = text.split(' ', 1)[1] if ' ' in text else ""
    
    if len(text) < 3:
        await update.message.reply_text("✍️ أرسل لي حلمك:\n/dream رأيت...")
        return
    
    try:
        await update.message.reply_text("🔮 جاري التفسير...")
        r = requests.post(
            f"{api_url}/api/interpret",
            json={"dream": text, "style": "islamic", "language": "ar"},
            timeout=60
        )
        if r.ok:
            result = r.json()
            interp = result.get("interpretation", "")[:4000]
            if interp:
                await update.message.reply_text(interp, parse_mode="Markdown")
            else:
                await update.message.reply_text("⚠️ لم يتم التفسير")
        else:
            await update.message.reply_text(f"⚠️ خطأ: {r.status_code}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ {str(e)[:200]}")

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"❌ Error: {context.error}")

# ============================================
# تشغيل البوت
# ============================================

def main():
    if not TELEGRAM_TOKEN:
        print("⚠️ TELEGRAM_TOKEN مفقود!")
        print("أضفه في متغيرات البيئة")
        sys.exit(1)
    
    print(f"🤖 تشغيل بوت تيليجرام...")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # تسجيل handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("dream", interpret_dream))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, interpret_dream))
    
    app.add_error_handler(error)
    
    print("✅ البوت يعمل! /start أرسل")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
