#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت Weaver المتكامل
يقوم بـ:
1. إنشاء مقالات جديدة للمدونة (باستخدام Groq)
2. تحديث صفحة المدونة الرئيسية تلقائياً
3. إضافة المقالات الجديدة إلى صفحة blog-simple.html
4. نشر المحتوى على تيليجرام برابط صحيح

print("🔑 GROQ_API_KEY موجود:", "نعم" if os.environ.get("GROQ_API_KEY") else "لا")
"""

import os
import json
import random
import requests
from datetime import datetime
from pathlib import Path
import time

# ============================================
# 🔐 المفاتيح
# ============================================
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "@weaver_dreams")

# ============================================
# 📚 موضوعات المقالات
# ============================================
ARTICLE_TOPICS = [
    {"title_ar": "تفسير حلم البحر في الثقافات المختلفة", "title_en": "Sea Dream in Different Cultures", "tags": ["بحر", "ثقافة"]},
    {"title_ar": "الرموز المتكررة في أحلام الطلاب", "title_en": "Recurring Symbols in Students' Dreams", "tags": ["طلاب", "رموز"]},
    {"title_ar": "كيف تفرق بين الرؤيا والحلم العادي", "title_en": "How to Distinguish Vision from Ordinary Dream", "tags": ["رؤيا", "حلم"]},
    {"title_ar": "تفسير الأحلام عند ابن سيرين: المنهج والأصول", "title_en": "Ibn Sirin: Methodology of Dream Interpretation", "tags": ["ابن سيرين", "إسلام"]},
    {"title_ar": "رموز الحيوانات في الأحلام: دليل شامل", "title_en": "Animal Symbols in Dreams: Complete Guide", "tags": ["حيوانات", "رموز"]},
    {"title_ar": "تفسير حلم الثعبان بين الخوف والحكمة", "title_en": "Snake Dream: Between Fear and Wisdom", "tags": ["ثعبان", "خوف"]},
    {"title_ar": "أحلام الطيران: الحرية والتحرر", "title_en": "Flying Dreams: Freedom and Liberation", "tags": ["طيران", "حرية"]},
    {"title_ar": "الماء في الأحلام: رمز المشاعر اللاواعية", "title_en": "Water in Dreams: Symbol of Subconscious Feelings", "tags": ["ماء", "مشاعر"]},
    {"title_ar": "تفسير الأحلام في مصر القديمة", "title_en": "Dream Interpretation in Ancient Egypt", "tags": ["مصر", "فراعنة"]},
    {"title_ar": "تفسير الأحلام في بلاد الرافدين", "title_en": "Dream Interpretation in Mesopotamia", "tags": ["بابل", "سومر"]},
    {"title_ar": "تفسير الأحلام في اليونان القديمة", "title_en": "Dream Interpretation in Ancient Greece", "tags": ["يونان", "مورفيوس"]},
    {"title_ar": "أحلام ما قبل النوم: لماذا نحلم؟", "title_en": "Pre-sleep Dreams: Why Do We Dream?", "tags": ["نوم", "علم الأعصاب"]},
]

# ============================================
# 🤖 توليد محتوى بالذكاء الاصطناعي
# ============================================
def generate_article(topic_ar, max_words=600):
    """يولد مقالاً كاملاً باستخدام Groq"""
    if not GROQ_API_KEY:
        return "محتوى تجريبي: " + topic_ar
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": "أنت كاتب متخصص في تفسير الأحلام. اكتب مقالاً شيقاً ومنظماً بالعربية."},
                    {"role": "user", "content": f"اكتب مقالاً عن '{topic_ar}'، بالعربية الفصحى. اجعله حوالي {max_words} كلمة، منظم بعناوين فرعية."}
                ],
                "temperature": 0.7,
                "max_tokens": 1200
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"خطأ في توليد المقال: {e}")
    
    return f"<p>مقال عن {topic_ar} قيد الإعداد. تابعونا للمزيد.</p>"

# ============================================
# 📝 إنشاء صفحة مقال جديدة
# ============================================
def create_article_page(topic_ar, topic_en, content):
    """ينشئ ملف HTML جديد للمقال"""
    # إنشاء اسم ملف صالح
    safe_title = topic_ar.replace(' ', '-').replace('؟', '').replace(':', '').replace('/', '-').replace('،', '')
    filename = f"{datetime.now().strftime('%Y-%m-%d')}-{safe_title}.html"
    
    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic_ar} | Weaver</title>
    <link rel="stylesheet" href="css/main.css">
    <style>
        body {{ font-family: 'Tajawal', sans-serif; background: #0a0a1a; color: #e2d9f3; line-height: 1.8; padding: 2rem; max-width: 800px; margin: auto; }}
        h1 {{ color: #f0c060; border-bottom: 1px solid #7c3aed; padding-bottom: 1rem; }}
        .article-meta {{ color: #888; font-size: 0.9rem; margin: 1rem 0; }}
        .article-content {{ margin-top: 2rem; }}
        .back-link {{ display: inline-block; margin-top: 2rem; color: #f0c060; text-decoration: none; }}
    </style>
</head>
<body>
    <h1>{topic_ar}</h1>
    <div class="article-meta">📅 {datetime.now().strftime('%d %B %Y')} | 🕐 {random.randint(5, 12)} دقائق قراءة</div>
    <div class="article-content">
        {content}
    </div>
    <a href="/blog-simple.html" class="back-link">← العودة للمدونة</a>
</body>
</html>"""
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return filename

# ============================================
# 📚 تحديث صفحة blog-simple.html
# ============================================
def update_simple_blog(article_title_ar, article_title_en, article_file, article_date):
    """يحدث صفحة blog-simple.html بإضافة المقال الجديد"""
    simple_blog_path = Path("blog-simple.html")
    
    if not simple_blog_path.exists():
        print("⚠️ blog-simple.html غير موجود")
        return
    
    with open(simple_blog_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "const articles = [" in content:
        new_article = f'    {{ title_ar: "{article_title_ar}", title_en: "{article_title_en}", date: "{article_date}", file: "{article_file}" }},'
        
        lines = content.split('\n')
        new_lines = []
        added = False
        for line in lines:
            new_lines.append(line)
            if "const articles = [" in line and not added:
                new_lines.append(new_article)
                added = True
        
        new_content = '\n'.join(new_lines)
        with open(simple_blog_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✅ تم تحديث blog-simple.html بالمقال: {article_title_ar}")
    else:
        print("⚠️ لم يتم العثور على قائمة articles في blog-simple.html")

# ============================================
# 📢 نشر المحتوى على تيليجرام (بالرابط الصحيح)
# ============================================
def post_to_telegram(article_title_ar, article_file):
    """ينشر في قناة تيليجرام"""
    if not TELEGRAM_TOKEN:
        return
    
    # الرابط الصحيح للمقال
    article_url = f"https://aidreamweaver.store/{article_file}"
    
    message = f"""📚 *مقال جديد في مدونة Weaver*

🔮 *{article_title_ar}*

✨ اقرأ المقال كاملاً:
{article_url}

🌙 جرب تفسير حلمك: https://aidreamweaver.store/app/analyze"""
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={
            "chat_id": TELEGRAM_CHANNEL_ID,
            "text": message,
            "parse_mode": "Markdown"
        }, timeout=10)
        if response.status_code == 200:
            print("✅ تم نشر الإعلان على تيليجرام")
        else:
            print(f"⚠️ فشل نشر تيليجرام: {response.text}")
    except Exception as e:
        print(f"⚠️ خطأ في تيليجرام: {e}")

# ============================================
# 🚀 المهمة اليومية الرئيسية
# ============================================
def daily_task():
    """المهمة التي تشغل كل يوم"""
    print(f"\n🚀 بدء المهمة اليومية: {datetime.now()}")
    
    # اختيار موضوع عشوائي
    topic = random.choice(ARTICLE_TOPICS)
    print(f"📝 الموضوع: {topic['title_ar']}")
    
    # 1. توليد المحتوى
    content = generate_article(topic["title_ar"])
    
    # 2. إنشاء ملف المقال
    article_file = create_article_page(topic["title_ar"], topic["title_en"], content)
    print(f"✅ تم إنشاء مقال: {article_file}")
    
    # 3. تحديث صفحة blog-simple.html
    today = datetime.now().strftime("%Y-%m-%d")
    update_simple_blog(topic["title_ar"], topic["title_en"], article_file, today)
    
    # 4. نشر على تيليجرام (بالرابط الصحيح)
    post_to_telegram(topic["title_ar"], article_file)
    
    print("✅ انتهت المهمة اليومية بنجاح")

# ============================================
# 🕐 التشغيل
# ============================================
if __name__ == "__main__":
    print("🤖 بوت Weaver المتكامل")
    print("📅 بدء التشغيل...")
    daily_task()
