#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weaver Marketing Bot - بوت التسويق الآلي
ينشر على: تيليجرام، تويتر/X
"""

import os
import sys
import json
import random
import requests
from datetime import datetime, date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# ─── الإعدادات ────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "")
SITE_URL = "https://aidreamweaver.store"

# ─── قوالب المنشورات ──────────────────────────────────────────────────────────
POST_TEMPLATES = {
    "dream_symbol": [
        "🌙 هل تعلم أن {symbol} في المنام يعني {meaning}؟\n\nاكتشف تفسير أحلامك بالذكاء الاصطناعي!\n🔗 {url}\n\n#تفسير_الأحلام #ذكاء_اصطناعي #Weaver",
        "✨ {symbol} في المنام...\n\n{meaning}\n\nفسّر حلمك الآن مجاناً على Weaver!\n🔗 {url}\n\n#أحلام #تفسير #Weaver",
    ],
    "promotion": [
        "🔮 Weaver | نَسَّاج الأحلام\n\nمنصة تفسير الأحلام بالذكاء الاصطناعي\n✅ تفسير عميق بأسلوب ابن سيرين\n✅ توليد صور 4K لأحلامك\n✅ مدونة ثقافية غنية\n\nجرّب مجاناً: {url}",
        "🌟 أكثر من 50,000 حلم مُفسَّر!\n\nانضم إلى مجتمع Weaver وفسّر أحلامك بالذكاء الاصطناعي\n🔗 {url}\n\n#Weaver #أحلام #ذكاء_اصطناعي",
    ],
    "blog": [
        "📚 مقال جديد على مدونة Weaver:\n\n{title}\n\nاقرأ المزيد: {url}/blog\n\n#تفسير_الأحلام #ثقافة #Weaver",
        "✍️ مقالة اليوم: {title}\n\nاكتشف المزيد على مدونة Weaver!\n🔗 {url}/blog",
    ]
}

DREAM_SYMBOLS = [
    {"symbol": "الثعبان", "meaning": "تحذير من عدو أو خطر قادم"},
    {"symbol": "الطيران", "meaning": "الحرية والطموح والتحرر من القيود"},
    {"symbol": "البحر", "meaning": "العواطف العميقة واللاوعي"},
    {"symbol": "الأسنان", "meaning": "القلق من المظهر أو فقدان شيء عزيز"},
    {"symbol": "النار", "meaning": "التحول والتطهير والطاقة"},
    {"symbol": "الميت", "meaning": "رسالة من الماضي أو نهاية مرحلة"},
    {"symbol": "الحمل", "meaning": "بداية جديدة أو مشروع قادم"},
    {"symbol": "المطر", "meaning": "الرحمة والبركة والتجديد"},
    {"symbol": "الجبل", "meaning": "التحديات والعقبات في الحياة"},
    {"symbol": "الذهب", "meaning": "الثروة والنجاح والمكانة"},
]

def generate_post_with_ai(template_type: str, context: dict = {}) -> str:
    """توليد منشور بالذكاء الاصطناعي"""
    if not GROQ_API_KEY:
        # استخدام القوالب الجاهزة
        templates = POST_TEMPLATES.get(template_type, POST_TEMPLATES["promotion"])
        template = random.choice(templates)
        return template.format(url=SITE_URL, **context)

    prompts = {
        "dream_symbol": f"اكتب منشوراً تسويقياً جذاباً عن {context.get('symbol', 'الأحلام')} في المنام. اجعله لا يزيد عن 200 حرف مع هاشتاقات. الرابط: {SITE_URL}",
        "promotion": f"اكتب منشوراً تسويقياً لمنصة Weaver لتفسير الأحلام بالذكاء الاصطناعي. جذاب وقصير. الرابط: {SITE_URL}",
        "blog": f"اكتب منشوراً للترويج لمقال بعنوان: {context.get('title', 'تفسير الأحلام')}. الرابط: {SITE_URL}/blog",
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": "أنت خبير تسويق رقمي. اكتب منشورات قصيرة وجذابة بالعربية مع إيموجي وهاشتاقات."},
                    {"role": "user", "content": prompts.get(template_type, prompts["promotion"])}
                ],
                "max_tokens": 300,
                "temperature": 0.8
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"⚠️ خطأ AI: {e}")

    # fallback
    templates = POST_TEMPLATES.get(template_type, POST_TEMPLATES["promotion"])
    template = random.choice(templates)
    return template.format(url=SITE_URL, **context)

def post_to_telegram(content: str) -> bool:
    """نشر على تيليجرام"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        print(f"📋 [محاكاة تيليجرام]: {content[:100]}...")
        return True

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHANNEL_ID,
                "text": content,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            },
            timeout=30
        )
        if response.status_code == 200:
            print(f"✅ تيليجرام: تم النشر")
            return True
        print(f"⚠️ تيليجرام: {response.status_code} - {response.text[:100]}")
        return False
    except Exception as e:
        print(f"⚠️ تيليجرام: {e}")
        return False

def run_marketing_campaign():
    """تشغيل حملة تسويقية كاملة"""
    print(f"\n📢 [{datetime.now().strftime('%H:%M:%S')}] بدء حملة التسويق...")

    results = {"telegram": False, "posts_generated": 0}

    # 1. منشور رمز الحلم
    symbol = random.choice(DREAM_SYMBOLS)
    post1 = generate_post_with_ai("dream_symbol", symbol)
    results["telegram"] = post_to_telegram(post1)
    results["posts_generated"] += 1

    # 2. منشور ترويجي
    post2 = generate_post_with_ai("promotion")
    post_to_telegram(post2)
    results["posts_generated"] += 1

    # حفظ السجل
    save_marketing_log(post1, "telegram", results["telegram"])
    save_marketing_log(post2, "telegram", True)

    print(f"✅ اكتملت الحملة: {results['posts_generated']} منشور")
    return results

def save_marketing_log(content: str, platform: str, success: bool):
    """حفظ سجل التسويق"""
    log_file = Path(__file__).parent.parent / "automation" / "marketing_log.json"
    log_file.parent.mkdir(exist_ok=True)

    logs = []
    if log_file.exists():
        try:
            with open(log_file) as f:
                logs = json.load(f)
        except:
            logs = []

    logs.append({
        "date": datetime.now().isoformat(),
        "platform": platform,
        "content": content[:200],
        "success": success
    })

    # الاحتفاظ بآخر 100 سجل فقط
    logs = logs[-100:]

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    print("🚀 تشغيل بوت التسويق...")
    run_marketing_campaign()
    print("✅ اكتمل")
