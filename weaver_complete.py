#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weaver Complete Bot - ملف واحد شامل
انسخ هذا الكود بالكامل في ملف واحد وارفعه على GitHub
"""

import os
import json
import random
import requests
import datetime
from pathlib import Path

# =========================================
# الإعدادات الأساسية
# =========================================
print("🚀 تشغيل بوت Weaver...")

# إنشاء المجلدات المطلوبة
Path("articles/arabic").mkdir(parents=True, exist_ok=True)
Path("articles/english").mkdir(parents=True, exist_ok=True)

# =========================================
# مواضيع جاهزة للمقالات (بدون API)
# =========================================
TOPICS = [
    {
        "ar": "الإمام محمد بن سيرين - شيخ المفسرين",
        "en": "Imam Ibn Sirin - The Master Interpreter",
        "cat_ar": "التراث الإسلامي",
        "cat_en": "Islamic Heritage",
        "era": "654-728 CE",
        "content_ar": """
الإمام محمد بن سيرين (654-728م) هو أشهر مفسر أحلام في التاريخ الإسلامي. 
كان من التابعين المعروفين بالورع والزهد.

منهجه في التفسير:
• لا يفسر الرؤيا إلا بعد الصلاة والاستخارة
• يسأل الرائي عن حاله قبل التفسير
• يعتمد على القرآن والسنة في تفسيره

أشهر تفسيراته:
- رؤية النبي ﷺ في المنام حق
- البحر يدل على الملك أو العالم
- الثعبان يدل على العدو
- الطيران يدل على السفر أو الموت
""",
        "content_en": """
Imam Muhammad Ibn Sirin (654-728 CE) is the most famous dream interpreter in Islamic history.

His methodology:
• Never interprets without prayer
• Asks about the dreamer's state
• Based on Quran and Sunnah

Famous interpretations:
• Seeing Prophet Muhammad is true
• Sea represents king or knowledge
• Snake represents enemy
• Flying represents travel or death
"""
    },
    {
        "ar": "بردية تشستر بيتي - أقدم دليل للأحلام",
        "en": "Chester Beatty Papyrus - Oldest Dream Manual",
        "cat_ar": "مصر القديمة",
        "cat_en": "Ancient Egypt",
        "era": "1275 BCE",
        "content_ar": """
بردية تشستر بيتي هي أقدم دليل معروف لتفسير الأحلام، يعود تاريخها إلى 1275 قبل الميلاد.

في مصر القديمة:
• كان الفراعنة يعتقدون أن الأحلام رسائل من الآلهة
• الكهنة كانوا المفسرين الرسميين
• كتبت الأحلام على البرديات في المعابد

أمثلة من التفسيرات الفرعونية:
- رؤية التمساح: تحذير من خطر
- رؤية النيل: خير وبركة
- رؤية الفرعون: ترقية في المنصب
""",
        "content_en": """
The Chester Beatty Papyrus is the oldest known dream manual, dating to 1275 BCE.

In Ancient Egypt:
• Pharaohs believed dreams were messages from gods
• Priests were official interpreters
• Dreams were recorded on papyrus in temples

Examples of Egyptian interpretations:
• Seeing crocodile: danger warning
• Seeing Nile: blessing and goodness
• Seeing Pharaoh: career promotion
"""
    },
    {
        "ar": "الألواح الطينية البابلية",
        "en": "Babylonian Clay Tablets",
        "cat_ar": "بلاد الرافدين",
        "cat_en": "Mesopotamia",
        "era": "2000 BCE",
        "content_ar": """
في بلاد الرافدين، كتبت الأحلام على ألواح طينية بالخط المسماري.

كان البابليون يعتقدون:
• أن الأحلام تنبؤات من الآلهة
• الكهنة يفسرون الأحلام للملوك
• بعض الأحلام كانت سبباً للحروب

أشهر الأحلام في التاريخ البابلي:
- حلم الملك كشتاريا
- أحلام جلجامش في الملحمة الشهيرة
""",
        "content_en": """
In Mesopotamia, dreams were written on clay tablets in cuneiform script.

Babylonians believed:
• Dreams were prophecies from gods
• Priests interpreted dreams for kings
• Some dreams caused wars

Famous Babylonian dreams:
• King Kashtaria's dream
• Gilgamesh's dreams in the epic
"""
    },
    {
        "ar": "معابد أسكليبيوس في اليونان",
        "en": "Asklepieia Temples in Greece",
        "cat_ar": "اليونان القديمة",
        "cat_en": "Ancient Greece",
        "era": "500 BCE",
        "content_ar": """
في اليونان القديمة، بنيت معابد أسكليبيوس للشفاء بالأحلام.

كيف كان يتم العلاج:
1. ينام المريض في المعبد
2. يأتيه حلم بالشفاء
3. الكهنة يفسرون الحلم
4. يصفون العلاج المناسب

اعتقد اليونانيون أن إله الأحلام مورفيوس يظهر في المنام على شكل إنسان.
""",
        "content_en": """
In Ancient Greece, Asklepieia temples were built for healing through dreams.

Healing process:
1. Patient sleeps in temple
2. Receives healing dream
3. Priests interpret the dream
4. Prescribe treatment

Greeks believed Morpheus, god of dreams, appears in human form.
"""
    },
    {
        "ar": "نظرية فرويد في تفسير الأحلام",
        "en": "Freud's Dream Theory",
        "cat_ar": "علم الأحلام",
        "cat_en": "Dream Science",
        "era": "1900 CE",
        "content_ar": """
سيغموند فرويد، مؤسس التحليل النفسي، كتب كتاب "تفسير الأحلام" عام 1900.

نظريته تقول:
• الأحلام "طريق ملكي" إلى اللاوعي
• الأحلام تحقق رغبات مكبوتة
• الرموز في الأحلام لها دلالات جنسية

انتقدت نظريته لاحقاً لكنها غيرت فهمنا للأحلام.
""",
        "content_en": """
Sigmund Freud, founder of psychoanalysis, wrote "The Interpretation of Dreams" in 1900.

His theory states:
• Dreams are "royal road" to unconscious
• Dreams fulfill repressed wishes
• Symbols have sexual meanings

His theory was later criticized but changed our understanding of dreams.
"""
    }
]

# =========================================
# إنشاء المقالات
# =========================================
def create_articles():
    """إنشاء مقالة عشوائية"""
    
    topic = random.choice(TOPICS)
    today = datetime.datetime.now().strftime("%Y%m%d")
    date_display = datetime.datetime.now().strftime("%b %d, %Y")
    
    print(f"📚 إنشاء مقالة: {topic['ar']}")
    
    # ===== المقالة العربية =====
    filename_ar = f"articles/arabic/{today}-{topic['ar'][:30]}.html"
    
    html_ar = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic['ar']} - Weaver</title>
    <meta name="description" content="{topic['ar']} - {topic['cat_ar']}">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Tajawal', sans-serif;
            background: #0a0514;
            color: #e2d9f3;
            line-height: 1.8;
            padding: 2rem;
        }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #f0c060; font-size: 2.5rem; margin-bottom: 1rem; }}
        .meta {{ color: #a855f7; margin-bottom: 2rem; }}
        .content {{
            background: rgba(30,10,60,0.3);
            padding: 2rem;
            border-radius: 20px;
            border: 1px solid #7c3aed;
        }}
        .footer {{
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #7c3aed;
            text-align: center;
        }}
        a {{ color: #f0c060; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{topic['ar']}</h1>
        <div class="meta">
            <span>📅 {date_display}</span> | 
            <span>🏷️ {topic['cat_ar']}</span> | 
            <span>⏱️ 8 دقائق قراءة</span>
        </div>
        
        <div class="content">
            {topic['content_ar']}
        </div>
        
        <div class="footer">
            <p>© 2026 Weaver - منصة تفسير الأحلام بالذكاء الاصطناعي</p>
            <p>🤖 بوت تيليجرام: @aidreamweaver_bot</p>
            <a href="https://aidreamweaver.store">🔗 العودة للمدونة</a>
        </div>
    </div>
</body>
</html>"""
    
    with open(filename_ar, "w", encoding="utf-8") as f:
        f.write(html_ar)
    print(f"✅ تم إنشاء: {filename_ar}")
    
    # ===== المقالة الإنجليزية =====
    filename_en = f"articles/english/{today}-{topic['ar'][:30]}-eng.html"
    
    html_en = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic['en']} - Weaver</title>
    <meta name="description" content="{topic['en']} - {topic['cat_en']}">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', sans-serif;
            background: #0a0514;
            color: #e2d9f3;
            line-height: 1.8;
            padding: 2rem;
        }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #f0c060; font-size: 2.5rem; margin-bottom: 1rem; }}
        .meta {{ color: #a855f7; margin-bottom: 2rem; }}
        .content {{
            background: rgba(30,10,60,0.3);
            padding: 2rem;
            border-radius: 20px;
            border: 1px solid #7c3aed;
        }}
        .footer {{
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #7c3aed;
            text-align: center;
        }}
        a {{ color: #f0c060; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{topic['en']}</h1>
        <div class="meta">
            <span>📅 {date_display}</span> | 
            <span>🏷️ {topic['cat_en']}</span> | 
            <span>⏱️ 8 min read</span>
        </div>
        
        <div class="content">
            {topic['content_en']}
        </div>
        
        <div class="footer">
            <p>© 2026 Weaver - AI Dream Interpretation Platform</p>
            <p>🤖 Telegram Bot: @aidreamweaver_bot</p>
            <a href="https://aidreamweaver.store">🔗 Back to Blog</a>
        </div>
    </div>
</body>
</html>"""
    
    with open(filename_en, "w", encoding="utf-8") as f:
        f.write(html_en)
    print(f"✅ تم إنشاء: {filename_en}")
    
    return filename_ar, filename_en

# =========================================
# تحديث ملفات المدونة
# =========================================
def update_blog_files():
    """تحديث صفحات المدونة"""
    
    print("📝 تحديث ملفات المدونة...")
    
    # تحديث blog.html لو كان موجوداً
    if os.path.exists("blog.html"):
        with open("blog.html", "a", encoding="utf-8") as f:
            f.write(f"\n<!-- آخر تحديث: {datetime.datetime.now()} -->\n")
    
    # تحديث blog-eng.html لو كان موجوداً
    if os.path.exists("blog-eng.html"):
        with open("blog-eng.html", "a", encoding="utf-8") as f:
            f.write(f"\n<!-- Last update: {datetime.datetime.now()} -->\n")
    
    print("✅ تم تحديث المدونة")

# =========================================
# ملف GitHub Actions (اختياري)
# =========================================
def create_github_workflow():
    """إنشاء ملف GitHub Actions"""
    
    workflow = """.github/workflows/daily_blog.yml"""
    
    content = """name: تحديث المدونة اليومي

on:
  schedule:
    - cron: '0 3 * * *'
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install requests
      - run: python weaver_complete.py
      - run: |
          git config user.name "Weaver Bot"
          git config user.email "bot@aidreamweaver.store"
          git add articles/ *.html
          git commit -m "تحديث المدونة" || exit 0
          git push"""
    
    Path(".github/workflows").mkdir(parents=True, exist_ok=True)
    with open(".github/workflows/daily_blog.yml", "w") as f:
        f.write(content)
    print("✅ تم إنشاء ملف GitHub Actions")

# =========================================
# التشغيل الرئيسي
# =========================================
if __name__ == "__main__":
    print("=" * 50)
    print("🚀 WEAVER COMPLETE BOT - ملف واحد شامل")
    print("=" * 50)
    print()
    
    # إنشاء المجلدات
    print("📁 إنشاء المجلدات...")
    Path("articles/arabic").mkdir(parents=True, exist_ok=True)
    Path("articles/english").mkdir(parents=True, exist_ok=True)
    print("✅ المجلدات جاهزة")
    print()
    
    # إنشاء المقالات
    create_articles()
    print()
    
    # تحديث المدونة
    update_blog_files()
    print()
    
    # إنشاء workflow (اختياري)
    if not os.path.exists(".github/workflows"):
        create_github_workflow()
    print()
    
    print("=" * 50)
    print("🎉 تم كل شيء بنجاح!")
    print("=" * 50)
    print()
    print("📂 المجلدات التي تم إنشاؤها:")
    print("   - articles/arabic/     (للمقالات العربية)")
    print("   - articles/english/    (للمقالات الإنجليزية)")
    print("   - .github/workflows/   (للتشغيل التلقائي)")
    print()
    print("🤖 بوت تيليجرام: @aidreamweaver_bot")
    print("🌐 الموقع: aidreamweaver.store")
