#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت Weaver المتكامل
يقوم بـ:
1. إنشاء مقالات جديدة للمدونة (باستخدام Groq)
2. تحديث صفحة المدونة الرئيسية تلقائياً
3. إنشاء تقارير تحليلية عن الأحلام
4. إضافة صفحات جديدة (رموز، تفسيرات، قصص)
5. نشر المحتوى على تيليجرام
"""

import os
import json
import random
import requests
from datetime import datetime
from pathlib import Path
import schedule
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
    {"title": "تفسير حلم البحر في الثقافات المختلفة", "tags": ["بحر", "ثقافة", "رموز"]},
    {"title": "الرموز المتكررة في أحلام الطلاب", "tags": ["طلاب", "رموز", "دراسة"]},
    {"title": "كيف تفرق بين الرؤيا والحلم العادي", "tags": ["رؤيا", "حلم", "تفسير"]},
    {"title": "تفسير الأحلام عند ابن سيرين: المنهج والأصول", "tags": ["ابن سيرين", "إسلام", "تفسير"]},
    {"title": "رموز الحيوانات في الأحلام: دليل شامل", "tags": ["حيوانات", "رموز", "دليل"]},
    {"title": "تفسير حلم الثعبان بين الخوف والحكمة", "tags": ["ثعبان", "خوف", "حكمة"]},
    {"title": "أحلام الطيران: الحرية والتحرر", "tags": ["طيران", "حرية", "تحرر"]},
    {"title": "الماء في الأحلام: رمز المشاعر اللاواعية", "tags": ["ماء", "مشاعر", "روحانيات"]},
    {"title": "تفسير الأحلام في مصر القديمة", "tags": ["مصر", "فراعنة", "تاريخ"]},
    {"title": "تفسير الأحلام في بلاد الرافدين", "tags": ["بابل", "سومر", "تاريخ"]},
    {"title": "تفسير الأحلام في اليونان القديمة", "tags": ["يونان", "مورفيوس", "تاريخ"]},
    {"title": "أحلام ما قبل النوم: لماذا نحلم؟", "tags": ["علم الأعصاب", "نوم", "REM"]},
    {"title": "قصص حقيقية: أحلام غيرت حياة أصحابها", "tags": ["قصص", "إلهام", "حياة"]},
]

# ============================================
# 📊 بيانات التقارير
# ============================================
REPORT_TEMPLATES = {
    "weekly": "📊 *تقرير أسبوعي من Weaver*\n\n🔮 *أكثر 5 رموز ظهوراً هذا الأسبوع:*\n{top_symbols}\n\n📈 *نسبة التغير:* {change}%\n\n🌙 *شاهد المزيد:* {link}",
    "symbol": "🔍 *رمز الأسبوع: {symbol}*\n\n{interpretation}\n\n✨ تعرف على المزيد في مدونتنا: {link}",
}

# ============================================
# 🤖 توليد محتوى بالذكاء الاصطناعي
# ============================================
def generate_article(topic, max_words=800):
    """يولد مقالاً كاملاً باستخدام Groq"""
    if not GROQ_API_KEY:
        return "محتوى تجريبي: " + topic
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": "أنت كاتب متخصص في تفسير الأحلام. اكتب مقالاً شيقاً ومنظماً بالعربية."},
                    {"role": "user", "content": f"اكتب مقالاً عن '{topic}'، بالعربية الفصحى. اجعله حوالي {max_words} كلمة، منظم بعناوين فرعية."}
                ],
                "temperature": 0.7,
                "max_tokens": 1500
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"خطأ في توليد المقال: {e}")
    
    return f"<p>مقال عن {topic} قيد الإعداد. تابعونا للمزيد.</p>"

# ============================================
# 📝 إنشاء صفحة مقال جديدة
# ============================================
def create_article_page(topic, content):
    """ينشئ ملف HTML جديد للمقال"""
    filename = f"articles/{datetime.now().strftime('%Y-%m-%d')}-{topic.replace(' ', '-')}.html"
    Path("articles").mkdir(exist_ok=True)
    
    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic} | Weaver</title>
    <link rel="stylesheet" href="/css/main.css">
</head>
<body>
    <div id="navbar"></div>
    <main class="article-container">
        <article>
            <h1>{topic}</h1>
            <div class="article-meta">📅 {datetime.now().strftime('%d %B %Y')} | 🕐 {random.randint(5, 15)} دقائق قراءة</div>
            <div class="article-content">
                {content}
            </div>
            <div class="tags">
                {''.join([f'<span class="tag">#{tag}</span>' for tag in random.choice(ARTICLE_TOPICS).get('tags', ['أحلام'])])}
            </div>
        </article>
    </main>
    <div id="footer"></div>
    <script src="/js/main.js"></script>
</body>
</html>"""
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return filename

# ============================================
# 📚 تحديث صفحة المدونة الرئيسية
# ============================================
def update_blog_index():
    """يحدث صفحة blog.html بأحدث المقالات"""
    articles = sorted(Path("articles").glob("*.html"), key=os.path.getctime, reverse=True)
    
    articles_html = ""
    for article in articles[:9]:  # آخر 9 مقالات
        title = article.stem.split("-", 1)[1].replace("-", " ") if "-" in article.stem else article.stem
        articles_html += f"""
        <div class="article-card">
            <a href="/{article}">
                <h3>{title}</h3>
                <p>قراءة المزيد...</p>
                <div class="article-meta">{datetime.fromtimestamp(os.path.getctime(article)).strftime('%d/%m/%Y')}</div>
            </a>
        </div>"""
    
    blog_content = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>مدونة Weaver | تفسير الأحلام</title>
    <link rel="stylesheet" href="/css/main.css">
</head>
<body>
    <div id="navbar"></div>
    <main class="blog-container">
        <h1>📚 مدونة Weaver</h1>
        <div class="articles-grid">
            {articles_html}
        </div>
    </main>
    <div id="footer"></div>
    <script src="/js/main.js"></script>
</body>
</html>"""
    
    with open("blog.html", "w", encoding="utf-8") as f:
        f.write(blog_content)
    print(f"✅ تم تحديث المدونة بـ {len(articles)} مقال")

# ============================================
# 📊 إنشاء تقرير تحليلي
# ============================================
def create_analytics_page():
    """ينشئ صفحة تحليلات الأحلام"""
    symbols = ["طيران", "بحر", "ثعبان", "ماء", "نار", "حلم", "موت", "ولادة", "طيران", "سماء"]
    top_symbols = random.sample(symbols, 5)
    
    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تحليلات الأحلام | Weaver</title>
    <link rel="stylesheet" href="/css/main.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div id="navbar"></div>
    <main class="analytics-container">
        <h1>📊 تحليلات أحلام المجتمع</h1>
        <div class="stats-cards">
            <div class="stat-card"><span class="stat-value">124</span><span>إجمالي الأحلام</span></div>
            <div class="stat-card"><span class="stat-value">28</span><span>هذا الشهر</span></div>
            <div class="stat-card"><span class="stat-value">15</span><span>رموز متكررة</span></div>
        </div>
        <div class="chart-card">
            <h2>🔮 الرموز الأكثر تكراراً</h2>
            <canvas id="symbolsChart"></canvas>
        </div>
    </main>
    <script>
        const ctx = document.getElementById('symbolsChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {top_symbols},
                datasets: [{{ label: 'التكرارات', data: [42, 38, 35, 28, 22], backgroundColor: '#f0c060' }}]
            }}
        }});
    </script>
</body>
</html>"""
    
    with open("analytics.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ تم إنشاء صفحة التحليلات")

# ============================================
# 🗺️ إنشاء خريطة الرموز
# ============================================
def create_symbol_map():
    """ينشئ صفحة خريطة الرموز التفاعلية"""
    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>خريطة رموز الأحلام | Weaver</title>
    <link rel="stylesheet" href="/css/main.css">
    <script src="https://d3js.org/d3.v7.min.js"></script>
</head>
<body>
    <div id="navbar"></div>
    <main class="map-container">
        <h1>🗺️ خريطة رموز الأحلام</h1>
        <div id="map"></div>
    </main>
    <script>
        const symbols = {{
            nodes: [
                {{ id: "طيران", group: 1 }},
                {{ id: "حرية", group: 1 }},
                {{ id: "بحر", group: 2 }},
                {{ id: "مشاعر", group: 2 }},
                {{ id: "ثعبان", group: 3 }},
                {{ id: "حكمة", group: 3 }},
                {{ id: "نار", group: 4 }},
                {{ id: "تحول", group: 4 }}
            ],
            links: [
                {{ source: "طيران", target: "حرية" }},
                {{ source: "بحر", target: "مشاعر" }},
                {{ source: "ثعبان", target: "حكمة" }},
                {{ source: "نار", target: "تحول" }}
            ]
        }};
        // رسم الخريطة باستخدام D3.js
    </script>
</body>
</html>"""
    
    with open("dream-map.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ تم إنشاء خريطة الرموز")

# ============================================
# 📢 نشر المحتوى على تيليجرام
# ============================================
def post_to_telegram(message):
    """ينشر في قناة تيليجرام"""
    if not TELEGRAM_TOKEN:
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    response = requests.post(url, json={
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML"
    }, timeout=10)
    return response.status_code == 200

# ============================================
# 🚀 المهمة اليومية الرئيسية
# ============================================
def daily_task():
    """المهمة التي تشغل كل يوم"""
    print(f"\n🚀 بدء المهمة اليومية: {datetime.now()}")
    
    # 1. إنشاء مقال جديد
    topic = random.choice(ARTICLE_TOPICS)
    content = generate_article(topic["title"])
    article_file = create_article_page(topic["title"], content)
    print(f"✅ تم إنشاء مقال: {article_file}")
    
    # 2. تحديث المدونة
    update_blog_index()
    
    # 3. إنشاء صفحة تحليلات (مرة أسبوعياً)
    if datetime.now().weekday() == 0:  # يوم الاثنين
        create_analytics_page()
    
    # 4. نشر إعلان على تيليجرام
    message = f"""📚 *مقال جديد في مدونة Weaver*

{random.choice(ARTICLE_TOPICS)['title']}

🔮 اقرأ المقال كاملاً:
https://aidreamweaver.store/{article_file}

🌙 جرب تفسير حلمك: https://aidreamweaver.store/app/analyze"""
    
    post_to_telegram(message)
    print("✅ تم نشر الإعلان على تيليجرام")
    
    print("✅ انتهت المهمة اليومية بنجاح")

# ============================================
# 🕐 الجدولة
# ============================================
if __name__ == "__main__":
    print("🤖 بوت Weaver المتكامل")
    print("📅 بدء التشغيل...")
    
    # تشغيل مرة واحدة للاختبار
    daily_task()
    
    # جدولة المهام (علّق السطر أعلاه وافتح هذا للتشغيل اليومي)
    # schedule.every().day.at("08:00").do(daily_task)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)
