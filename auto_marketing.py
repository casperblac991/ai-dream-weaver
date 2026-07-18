#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت التسويق الآلي لـ Weaver
يعمل يومياً بدون تدخل
"""

import os
import random
import requests
import json
from datetime import datetime
import schedule
import time

# ============================================
# 🔐 المفاتيح (ضعها في Environment Variables)
# ============================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# قائمة المحتوى الجاهز (إذا فشل الذكاء الاصطناعي)
FALLBACK_CONTENT = [
    "🌙 هل تساءلت يومًا ماذا يعني حلمك؟ Weaver يفسر أحلامك بالذكاء الاصطناعي",
    "✨ الطيران في المنام يرمز للحرية. جرب تفسير حلمك على Weaver",
    "📚 اكتشف تفسير الأحلام في مصر القديمة على مدونة Weaver",
    "🤖 الذكاء الاصطناعي الآن يفسر أحلامك! جرب Weaver مجاناً",
    "🐍 حلمت بثعبان؟ تعرف على معناه في ثقافات العالم المختلفة على Weaver",
    "🌊 البحر في المنام: رمز للمشاعر اللاواعية. فسر حلمك مع Weaver",
    "🔥 النار في الأحلام تدل على التحول. اكتشف المزيد على منصة Weaver",
    "🕊️ الطيران والحرية: قصص حقيقية لأحلام غيرت حياة أصحابها"
]

# ============================================
# 🤖 توليد محتوى جديد بالذكاء الاصطناعي
# ============================================
def generate_content(topic):
    """يولد محتوى جديد باستخدام Groq"""
    if not GROQ_API_KEY:
        return random.choice(FALLBACK_CONTENT)
    
    try:
        import requests
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": "أنت مساعد تسويق متخصص. اكتب منشوراً قصيراً وجذاباً بالعربية لمنصة تفسير الأحلام Weaver. اجعله لا يزيد عن 280 حرفاً."},
                    {"role": "user", "content": f"اكتب منشوراً عن: {topic}"}
                ]
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"خطأ في توليد المحتوى: {e}")
    
    return random.choice(FALLBACK_CONTENT)

# ============================================
# 📢 نشر على تويتر (X)
# ============================================
def post_to_twitter(content):
    """ينشر تغريدة على تويتر"""
    if not TWITTER_BEARER_TOKEN:
        print("⚠️ Twitter token غير موجود")
        return False
    
    try:
        # هذه دالة مبسطة – تحتاج تفعيل API تويتر
        print(f"📢 [تويتر] {content[:100]}...")
        # في الواقع تحتاج تفعيل API تويتر V2
        return True
    except Exception as e:
        print(f"❌ خطأ في تويتر: {e}")
        return False

# ============================================
# 📢 نشر على تيليجرام (قناة أو مجموعة)
# ============================================
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "@aidreamweaver")

def post_to_telegram(content):
    """ينشر في قناة تيليجرام"""
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ Telegram token غير موجود")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        response = requests.post(url, json={
            "chat_id": TELEGRAM_CHANNEL_ID,
            "text": f"{content}\n\n🌙 جرب تفسير حلمك: https://aidreamweaver.store/app/analyze",
            "parse_mode": "HTML"
        }, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ [تيليجرام] نشر: {content[:50]}...")
            return True
        else:
            print(f"❌ فشل نشر تيليجرام: {response.text}")
            return False
    except Exception as e:
        print(f"❌ خطأ في تيليجرام: {e}")
        return False

# ============================================
# 📝 تحديث المدونة بمقال جديد
# ============================================
def generate_blog_article():
    """يولد مقالاً جديداً للمدونة"""
    topics = [
        "تفسير حلم البحر في الثقافات المختلفة",
        "الرموز المتكررة في أحلام الطلاب",
        "كيف تفرق بين الرؤيا والحلم العادي",
        "تفسير الأحلام عند ابن سيرين",
        "رموز الحيوانات في الأحلام"
    ]
    
    topic = random.choice(topics)
    article = generate_content(f"مقال كامل عن {topic}")
    
    # حفظ المقال في ملف
    filename = f"articles/{datetime.now().strftime('%Y-%m-%d')}-{topic.replace(' ', '-')}.html"
    os.makedirs("articles", exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>{topic} | Weaver</title>
</head>
<body>
    <h1>{topic}</h1>
    <p>{article}</p>
    <a href="/">العودة للرئيسية</a>
</body>
</html>""")
    
    print(f"✅ [مدونة] تم إنشاء مقال: {filename}")
    return filename

# ============================================
# 📧 إرسال تقرير يومي (عبر تيليجرام)
# ============================================
def send_daily_report(stats):
    """يرسل تقرير الأداء اليومي"""
    report = f"""📊 *تقرير Weaver اليومي*
📅 {datetime.now().strftime('%Y-%m-%d')}

📈 *الأداء*
• مستخدمون نشطون: {stats.get('active_users', 'جاري التحديث')}
• مشاهدات: {stats.get('views', 'جاري التحديث')}
• منشورات جديدة: {stats.get('posts', 0)}

🔮 *نشاط اليوم*
• تغريدات: {stats.get('tweets', 0)}
• منشورات تيليجرام: {stats.get('telegram_posts', 0)}
• مقالات جديدة: {stats.get('articles', 0)}

🌙 *رابط المنصة*
https://aidreamweaver.store/app/analyze
"""
    
    post_to_telegram(report)

# ============================================
# 🚀 المهمة الرئيسية (تشغيل يومياً)
# ============================================
def daily_marketing_task():
    """المهمة التي تشغل كل يوم"""
    print(f"\n🚀 بدء المهمة اليومية: {datetime.now()}")
    
    stats = {
        "tweets": 0,
        "telegram_posts": 0,
        "articles": 0,
        "posts": 0
    }
    
    # 1. نشر على تويتر (3 تغريدات)
    topics = ["تفسير الأحلام", "رموز الأحلام", "قصة حلم ملهمة"]
    for topic in topics:
        content = generate_content(topic)
        if post_to_twitter(content):
            stats["tweets"] += 1
        time.sleep(5)  # انتظار بين المنشورات
    
    # 2. نشر على تيليجرام (منشوران)
    for i in range(2):
        content = generate_content("منشور ترويجي")
        if post_to_telegram(content):
            stats["telegram_posts"] += 1
        time.sleep(3)
    
    # 3. إنشاء مقال جديد للمدونة
    if generate_blog_article():
        stats["articles"] += 1
    
    stats["posts"] = stats["tweets"] + stats["telegram_posts"] + stats["articles"]
    
    # 4. إرسال التقرير
    send_daily_report(stats)
    
    print(f"✅ انتهت المهمة بنجاح! نشر {stats['posts']} محتوى")

# ============================================
# 🕐 جدولة المهام
# ============================================
def schedule_daily():
    """جدولة المهام اليومية"""
    schedule.every().day.at("08:00").do(daily_marketing_task)  # 8 صباحاً
    schedule.every().day.at("18:00").do(daily_marketing_task)  # 6 مساءً
    
    print("✅ تم جدولة المهام: 8:00 و 18:00")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# ============================================
# ▶️ تشغيل البوت
# ============================================
if __name__ == "__main__":
    print("🧠 بوت التسويق الآلي لـ Weaver")
    print(f"📅 بدء التشغيل: {datetime.now()}")
    
    # تشغيل مرة واحدة للاختبار
    daily_marketing_task()
    
    # أو تشغيل الجدولة (علّق السطر أعلاه وافتح هذا)
    # schedule_daily()
