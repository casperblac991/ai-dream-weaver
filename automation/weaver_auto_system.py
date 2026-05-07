#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weaver Auto System - نظام الأتمتة الشامل (نسخة مستقرة)
"""

import os
import sys
import random
import requests
import schedule
import time
from datetime import datetime, date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from app.database import init_db
    from app.models import save_blog_post, log_marketing, reset_daily_dreams, get_platform_stats
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    print("⚠️ قاعدة البيانات غير متاحة")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "")
SITE_URL = "https://aidreamweaver.store"

BLOG_TOPICS = [
    {"title": "الإمام ابن سيرين وفن تفسير الأحلام", "cat": "التراث الإسلامي", "tags": "ابن سيرين,تفسير"},
    {"title": "رؤية النبي ﷺ في المنام", "cat": "التراث الإسلامي", "tags": "النبي,رؤيا"},
    {"title": "الثعبان في المنام", "cat": "رموز الأحلام", "tags": "ثعبان,رموز"},
]

MARKETING_TOPICS = ["فسّر حلمك بالذكاء الاصطناعي", "جرّب تفسير الأحلام مجاناً"]

def generate_with_groq(prompt, system="", max_tokens=1500):
    if not GROQ_API_KEY:
        return ""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={"model": "llama3-70b-8192", "messages": messages, "temperature": 0.7, "max_tokens": max_tokens},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
    except Exception:
        pass
    return ""

# -------------------------------------------------------------------
# دالة تحديث blog.html (مع استيراد مؤجل لـ BeautifulSoup)
# -------------------------------------------------------------------
def update_main_blog_page(article_info):
    """يضيف المقال الجديد إلى blog.html - استيراد bs4 يحدث هنا فقط"""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("⚠️ BeautifulSoup غير مثبتة، لن يتم تحديث blog.html")
        return

    blog_index_path = Path(__file__).parent.parent / "blog.html"
    if not blog_index_path.exists():
        print("⚠️ blog.html غير موجود")
        return

    try:
        with open(blog_index_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
    except Exception as e:
        print(f"⚠️ خطأ قراءة blog.html: {e}")
        return

    container = soup.find("div", class_="blog-posts") or soup.find("div", id="blog-posts") or soup.find("main")
    if not container:
        print("⚠️ لم يتم العثور على حاوية المقالات")
        return

    new_card = soup.new_tag("div", **{"class": "blog-card"})
    if article_info.get("image"):
        img = soup.new_tag("img", src=article_info["image"], alt=article_info["title"])
        new_card.append(img)

    h3 = soup.new_tag("h3")
    h3.string = article_info["title"]
    new_card.append(h3)

    p_date = soup.new_tag("p", **{"class": "date"})
    p_date.string = article_info["date"]
    new_card.append(p_date)

    p_sum = soup.new_tag("p", **{"class": "summary"})
    summary = article_info["summary"][:150] + "..." if len(article_info["summary"]) > 150 else article_info["summary"]
    p_sum.string = summary
    new_card.append(p_sum)

    link = soup.new_tag("a", href=article_info["url"], **{"class": "read-more"})
    link.string = "اقرأ المزيد"
    new_card.append(link)

    container.insert(0, new_card)

    with open(blog_index_path, "w", encoding="utf-8") as f:
        f.write(str(soup))
    print(f"✅ تم تحديث blog.html بإضافة: {article_info['title']}")

def save_blog_as_html(title, content, topic):
    blog_dir = Path(__file__).parent.parent / "blog"
    blog_dir.mkdir(exist_ok=True)
    slug = title.replace(" ", "-").replace("،", "").replace("؟", "")[:50]
    filename = f"{slug}-{date.today().strftime('%Y%m%d')}.html"
    plain_content = content.replace("<br>", " ").replace("\n", " ").replace("  ", " ")
    summary = plain_content[:200].strip()
    
    # Get related posts for the article
    related = [
        {"title": "الإمام ابن سيرين: إمام المفسرين", "url": "#ibnsireen"},
        {"title": "الأحلام في مصر القديمة", "url": "#egypt"},
        {"title": "معجم الرموز", "url": "#dictionary"},
    ]
    related_html = "\n".join([f'<li><a href="{r["url"]}">📖 {r["title"]}</a></li>' for r in related])
    
    # Get current date in Arabic
    arabic_months = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
    current_date = date.today()
    arabic_date = f"{current_date.day} {arabic_months[current_date.month-1]} {current_date.year}"
    
    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | مدونة حالم</title>
    <meta name="description" content="{summary[:150]}">
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800;900&family=Cairo:wght@300;400;600;700;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --gold: #f0c060;
            --gold-light: #fde68a;
            --deep: #0a0514;
            --purple: #1e0a3c;
            --violet: #2d1060;
            --accent: #7c3aed;
            --accent2: #a855f7;
            --pink: #ec4899;
            --cyan: #06b6d4;
            --text: #e2d9f3;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Tajawal', sans-serif;
            background: var(--deep);
            color: var(--text);
            line-height: 1.9;
        }}
        
        .bg-layer {{
            position: fixed; inset: 0; z-index: -1;
            background: radial-gradient(ellipse at 20% 50%, #1e0a3c 0%, transparent 60%),
                        radial-gradient(ellipse at 80% 20%, #0c0a3e 0%, transparent 50%),
                        #050210;
        }}
        
        nav {{
            padding: 1.2rem 3rem;
            display: flex; justify-content: space-between; align-items: center;
            background: rgba(5, 2, 16, 0.8);
            border-bottom: 1px solid rgba(124, 58, 237, 0.2);
        }}
        
        .logo a {{
            font-family: 'Cairo', sans-serif; font-size: 1.8rem; font-weight: 900;
            background: linear-gradient(135deg, var(--gold), var(--accent2));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            text-decoration: none;
        }}
        
        .nav-links {{
            display: flex; gap: 2rem; list-style: none;
        }}
        
        .nav-links a {{
            color: rgba(226, 217, 243, 0.7);
            text-decoration: none;
        }}
        
        .lang-toggle {{
            padding: 0.5rem 1rem;
            background: rgba(124, 58, 237, 0.2);
            border-radius: 20px;
            color: var(--gold);
            font-size: 0.9rem;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .article-header {{
            text-align: center;
            margin: 3rem 0;
        }}
        
        .article-title {{
            font-family: 'Cairo', sans-serif;
            font-size: 2.5rem;
            background: linear-gradient(135deg, var(--gold), var(--accent2));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }}
        
        .article-meta {{
            color: rgba(226, 217, 243, 0.5);
            font-size: 0.95rem;
        }}
        
        .article-content {{
            background: rgba(255, 255, 255, 0.02);
            border-radius: 20px;
            padding: 2.5rem;
            border: 1px solid rgba(124, 58, 237, 0.2);
        }}
        
        .article-content h2 {{
            color: var(--gold);
            font-family: 'Cairo', sans-serif;
            margin: 2.5rem 0 1rem;
            font-size: 1.5rem;
        }}
        
        .article-content p {{
            margin-bottom: 1.5rem;
            font-size: 1.1rem;
        }}
        
        .article-content ul {{
            margin: 1rem 0 1rem 2rem;
        }}
        
        .article-content li {{
            margin-bottom: 0.5rem;
        }}
        
        .related-posts {{
            margin-top: 3rem;
            padding: 2rem;
            background: rgba(124, 58, 237, 0.1);
            border-radius: 15px;
        }}
        
        .related-posts h3 {{
            color: var(--gold);
            margin-bottom: 1rem;
        }}
        
        .related-posts ul {{
            list-style: none;
        }}
        
        .related-posts li {{
            margin-bottom: 0.5rem;
        }}
        
        .related-posts a {{
            color: var(--text);
            text-decoration: none;
        }}
        
        .related-posts a:hover {{
            color: var(--gold);
        }}
        
        footer {{
            background: rgba(5, 2, 16, 0.8);
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            padding: 3rem 2rem;
            text-align: center;
            margin-top: 3rem;
        }}
    </style>
</head>
<body>
    <div class="bg-layer"></div>
    
    <nav>
        <div class="logo"><a href="{SITE_URL}">حالم</a></div>
        <ul class="nav-links">
            <li><a href="{SITE_URL}">الرئيسية</a></li>
            <li><a href="{SITE_URL}/blog.html">المدونة</a></li>
            <li><a href="{SITE_URL}/#pricing">الأسعار</a></li>
            <li><a href="https://t.me/aidreamweaver_bot">البوت</a></li>
        </ul>
        <span class="lang-toggle">🇸🇦 🇬🇧</span>
    </nav>
    
    <div class="container">
        <article>
            <div class="article-header">
                <h1 class="article-title">{title}</h1>
                <div class="article-meta">📅 {arabic_date} • 🕒 8 دقائق قراءة • 🏛️ {topic.get('cat', 'الحضارات')}</div>
            </div>
            
            <div class="article-content">
                {content.replace(chr(10), '</p><p>')}
            </div>
            
            <div class="related-posts">
                <h3>مقالات ذات صلة</h3>
                <ul>
                    {related_html}
                </ul>
            </div>
        </article>
    </div>
    
    <footer>
        <div style="margin-bottom: 1rem;">
            <a href="{SITE_URL}" style="color: var(--gold); text-decoration: none; margin: 0 1rem;">الرئيسية</a>
            <a href="{SITE_URL}/blog.html" style="color: var(--gold); text-decoration: none; margin: 0 1rem;">المدونة</a>
            <a href="https://t.me/aidreamweaver_bot" style="color: var(--gold); text-decoration: none; margin: 0 1rem;">البوت</a>
        </div>
        <p>© 2026 حالم - منصة الأحلام الذكية</p>
    </footer>
</body>
</html>"""
    with open(blog_dir / filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ تم حفظ ملف HTML: {filename}")

    update_main_blog_page({
        "title": title,
        "date": date.today().strftime("%Y-%m-%d"),
        "summary": summary,
        "url": f"/blog/{filename}",
        "image": None
    })

def generate_daily_blog():
    print(f"\n📝 توليد مقال يومي...")
    topic = random.choice(BLOG_TOPICS)
    title = topic["title"]
    
    # Enhanced prompt for better bilingual content
    system = """أنت كاتب متخصص في تفسير الأحلام والتراث الإسلامي.
اكتب مقالاً شاملاً ومفصلاً (800-1200 كلمة) يتضمن:
1. مقدمة جذابة عن الموضوع
2. شرح تفصيلي للتاريخ والسياق
3. أمثلة من مصادر موثوقة (ابن سيرين، بردية تشيستر بيتي، الخ)
4. تفسيرات رمزية متعددة
5. خاتمة ونصائح للقراء
6. اكتب كل فقرة بالعربية ثم الإنجليزية (ازدواجية的语言)
استخدم لغة عربية فصيحة مع عناوين فرعية h2."""
    
    prompt = f"""اكتب مقالاً شاملاً بالتفصيل عن: {title}

المتطلبات:
- 800-1200 كلمة
- ازدواجية: كل فقرة بالعربية ثم الإنجليزية
- عناوين فرعية (h2) لتنظيم المحتوى
- أمثلة تاريخية موثوقة
- رموز الأحلام وتفسيراتها
- مصادر من التراث العربي والإسلامي والغربي""
    
    content = generate_with_groq(prompt, system, max_tokens=3500)
    if not content:
        content = f"""<h2>مقدمة</h2><p>مقال شامل عن {title} - سيتم تحديثه قريباً.</p>"""

    if DB_AVAILABLE:
        try:
            init_db()
            slug = title.replace(" ", "-")[:60] + f"-{date.today().strftime('%Y%m%d')}"
            save_blog_post(title=title, content=content, slug=slug, category=topic["cat"], author="نَسَّاج AI", language="ar", tags=topic.get("tags", ""))
            print("✅ حفظ في قاعدة البيانات")
        except Exception as e:
            print(f"⚠️ خطأ قاعدة بيانات: {e}")

    save_blog_as_html(title, content, topic)
    return title, content

def post_to_telegram(content):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        return False
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHANNEL_ID, "text": content, "parse_mode": "HTML"},
            timeout=30
        )
        print("✅ تم النشر على تيليجرام")
        return True
    except Exception:
        return False

def run_daily_marketing():
    print("\n📢 تشغيل التسويق...")
    topic = random.choice(MARKETING_TOPICS)
    post_content = f"🌙 {topic}\nفسّر أحلامك بالذكاء الاصطناعي!\n🔗 {SITE_URL}\n#تفسير_الأحلام #Weaver"
    post_to_telegram(post_content)
    if DB_AVAILABLE:
        try:
            log_marketing("telegram", post_content, "sent")
        except Exception:
            pass
    print("✅ تم التسويق")

def reset_daily_counters():
    print("\n🔄 إعادة تعيين العدادات...")
    if DB_AVAILABLE:
        try:
            reset_daily_dreams()
            print("✅ تم إعادة تعيين العدادات")
        except Exception as e:
            print(f"⚠️ خطأ: {e}")

def generate_daily_report():
    print("\n📊 توليد التقرير اليومي...")
    if DB_AVAILABLE:
        try:
            stats = get_platform_stats()
            report = f"""📊 تقرير Weaver - {date.today()}
👥 المستخدمون: {stats.get('total_users', 0)}
🌙 الأحلام: {stats.get('total_dreams', 0):,}
📧 المشتركون: {stats.get('total_subscribers', 0)}
🔗 {SITE_URL}"""
            post_to_telegram(report)
        except Exception as e:
            print(f"⚠️ خطأ في التقرير: {e}")

def setup_schedule():
    schedule.every().day.at("08:00").do(generate_daily_blog)
    schedule.every().day.at("10:00").do(run_daily_marketing)
    schedule.every().day.at("15:00").do(run_daily_marketing)
    schedule.every().day.at("20:00").do(run_daily_marketing)
    schedule.every().day.at("00:00").do(reset_daily_counters)
    schedule.every().day.at("21:00").do(generate_daily_report)

def run_once():
    print("🚀 تشغيل مرة واحدة...")
    generate_daily_blog()
    run_daily_marketing()
    generate_daily_report()
    print("✅ اكتملت المهام")

def run_continuous():
    print("🚀 تشغيل مستمر...")
    setup_schedule()
    generate_daily_blog()
    run_daily_marketing()
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    if "--once" in sys.argv:
        run_once()
    else:
        run_continuous()
