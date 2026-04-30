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
    summary = plain_content[:150].strip()

    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head><meta charset="UTF-8"><title>{title} | Weaver</title>
<style>
body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #0a0a1a; color: #e0e0ff; }}
.article {{ max-width: 800px; margin: 2rem auto; padding: 2rem; background: rgba(255,255,255,0.05); border-radius: 16px; }}
h1 {{ color: #a78bfa; }}
</style>
</head>
<body>
<nav><a href="{SITE_URL}" style="color:#a78bfa;">Weaver</a> | <a href="{SITE_URL}/blog">المدونة</a></nav>
<div class="article"><h1>{title}</h1><div>{content.replace(chr(10), '<br>')}</div></div>
</body></html>"""
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
    system = "أنت كاتب متخصص في تفسير الأحلام."
    prompt = f"اكتب مقالاً شاملاً عن: {title} (700-900 كلمة)"
    content = generate_with_groq(prompt, system, max_tokens=2000)
    if not content:
        content = f"<h2>{title}</h2><p>مقال عن {title} - سيتم تحديثه قريباً.</p>"

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
