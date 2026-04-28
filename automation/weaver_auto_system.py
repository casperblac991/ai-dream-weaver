#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weaver Auto System - نظام الأتمتة الشامل
يعمل على مدار الساعة بدون تدخل بشري
"""

import os
import sys
import json
import random
import requests
import schedule
import time
from datetime import datetime, date
from pathlib import Path

# إضافة المسار الجذري
sys.path.insert(0, str(Path(__file__).parent.parent))

# ─── الإعدادات ────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "")
TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET", "")
SITE_URL = "https://aidreamweaver.store"

# ─── مواضيع المدونة اليومية ───────────────────────────────────────────────────
BLOG_TOPICS = [
    # التراث الإسلامي
    {"title": "الإمام ابن سيرين وفن تفسير الأحلام", "cat": "التراث الإسلامي", "tags": "ابن سيرين,تفسير,إسلام"},
    {"title": "رؤية النبي ﷺ في المنام - الدلالات والأحكام", "cat": "التراث الإسلامي", "tags": "النبي,رؤيا,إسلام"},
    {"title": "الرؤيا الصادقة وأنواع الأحلام في الإسلام", "cat": "التراث الإسلامي", "tags": "رؤيا,أحلام,إسلام"},
    {"title": "كتاب تعطير الأنام في تفسير الأحلام للنابلسي", "cat": "التراث الإسلامي", "tags": "النابلسي,كتب,تفسير"},
    # الحضارات القديمة
    {"title": "بردية تشستر بيتي - أقدم دليل لتفسير الأحلام", "cat": "مصر القديمة", "tags": "مصر,فراعنة,تاريخ"},
    {"title": "أحلام الملك جلجامش في الملحمة البابلية", "cat": "بلاد الرافدين", "tags": "بابل,جلجامش,تاريخ"},
    {"title": "معابد أسكليبيوس ومعالجة الأمراض بالأحلام", "cat": "اليونان القديمة", "tags": "يونان,أسكليبيوس,علاج"},
    {"title": "الأحلام في الحضارة الهندية القديمة - الأوبانيشاد", "cat": "الحضارات القديمة", "tags": "هند,أوبانيشاد,فلسفة"},
    # علم النفس
    {"title": "نظرية فرويد في تفسير الأحلام", "cat": "علم النفس", "tags": "فرويد,نفس,تحليل"},
    {"title": "يونغ واللاوعي الجمعي في الأحلام", "cat": "علم النفس", "tags": "يونغ,لاوعي,نفس"},
    {"title": "الأحلام المتكررة - ماذا تعني؟", "cat": "علم النفس", "tags": "أحلام,متكررة,نفس"},
    # رموز شائعة
    {"title": "الثعبان في المنام - تفسيرات متعددة", "cat": "رموز الأحلام", "tags": "ثعبان,رموز,تفسير"},
    {"title": "الطيران في المنام - رمز الحرية والطموح", "cat": "رموز الأحلام", "tags": "طيران,حرية,رموز"},
    {"title": "البحر والماء في الأحلام - العمق العاطفي", "cat": "رموز الأحلام", "tags": "بحر,ماء,عواطف"},
    {"title": "رؤية الميت في المنام - دلالات وتفسيرات", "cat": "رموز الأحلام", "tags": "ميت,رؤيا,تفسير"},
    {"title": "الأسنان في المنام - من ابن سيرين إلى فرويد", "cat": "رموز الأحلام", "tags": "أسنان,رموز,تفسير"},
    {"title": "النار في المنام - رمز التحول والتطهير", "cat": "رموز الأحلام", "tags": "نار,تحول,رموز"},
    {"title": "الحمل والولادة في الأحلام", "cat": "رموز الأحلام", "tags": "حمل,ولادة,رموز"},
    # علمي
    {"title": "مرحلة REM والأحلام - ما يقوله العلم", "cat": "علم الأحلام", "tags": "REM,نوم,علم"},
    {"title": "الأحلام الواضحة (Lucid Dreams) - كيف تتحكم في أحلامك", "cat": "علم الأحلام", "tags": "أحلام واضحة,تحكم,نوم"},
    {"title": "لماذا ننسى أحلامنا؟ - تفسير علمي", "cat": "علم الأحلام", "tags": "نسيان,أحلام,علم"},
]

# ─── مواضيع التسويق ───────────────────────────────────────────────────────────
MARKETING_TOPICS = [
    "فسّر حلمك الآن بالذكاء الاصطناعي",
    "الثعبان في المنام - هل تعرف معناه؟",
    "أكثر من 50,000 حلم مُفسَّر على Weaver",
    "جرّب تفسير الأحلام مجاناً",
    "الطيران في المنام - رمز الحرية",
    "مدونة Weaver - موسوعة الأحلام",
    "تفسير الأحلام بأسلوب ابن سيرين",
    "البحر في المنام - ماذا يعني؟",
]

# ─── توليد المحتوى بالذكاء الاصطناعي ────────────────────────────────────────

def generate_with_groq(prompt: str, system: str = "", max_tokens: int = 1500) -> str:
    """توليد محتوى باستخدام Groq"""
    if not GROQ_API_KEY:
        print("⚠️ GROQ_API_KEY غير موجود")
        return ""

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama3-70b-8192",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": max_tokens
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        print(f"⚠️ Groq error: {response.status_code}")
        return ""
    except Exception as e:
        print(f"⚠️ Groq exception: {e}")
        return ""

# ─── نشر المدونة اليومية ─────────────────────────────────────────────────────

def generate_daily_blog():
    """توليد ونشر مقال يومي"""
    print(f"\n📝 [{datetime.now().strftime('%H:%M')}] توليد مقال يومي...")

    topic = random.choice(BLOG_TOPICS)
    title = topic["title"]

    system = "أنت كاتب متخصص في تفسير الأحلام والحضارات القديمة. اكتب مقالات شيقة وعلمية بالعربية الفصحى."
    prompt = f"""اكتب مقالاً شاملاً ومفصلاً عن: {title}

المقال يجب أن يتضمن:
## مقدمة
[مقدمة جذابة تشوّق القارئ]

## الخلفية التاريخية
[معلومات تاريخية وثقافية]

## التفسيرات والدلالات
[تفسيرات مختلفة من مصادر متعددة]

## الرموز والمعاني
[شرح الرموز المرتبطة بالموضوع]

## الخاتمة
[خلاصة مفيدة]

الطول: 700-900 كلمة. الأسلوب: علمي شيق."""

    content = generate_with_groq(prompt, system, max_tokens=2000)
    if not content:
        content = f"<h2>{title}</h2><p>مقال عن {title} - قيد التحديث</p>"

    # حفظ في قاعدة البيانات
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from app.database import init_db
        from app.models import save_blog_post
        init_db()

        slug = title.replace(" ", "-").replace("،", "").replace("؟", "").replace("ﷺ", "")[:60]
        slug = f"{slug}-{date.today().strftime('%Y%m%d')}"

        save_blog_post(
            title=title,
            content=content,
            slug=slug,
            category=topic["cat"],
            author="نَسَّاج AI",
            language="ar",
            tags=topic.get("tags", "")
        )
        print(f"✅ تم حفظ المقال: {title[:50]}")
    except Exception as e:
        print(f"⚠️ خطأ في حفظ المقال: {e}")

    # حفظ كملف HTML أيضاً
    save_blog_as_html(title, content, topic)
    return title, content

def save_blog_as_html(title: str, content: str, topic: dict):
    """حفظ المقال كملف HTML"""
    blog_dir = Path(__file__).parent.parent / "blog"
    blog_dir.mkdir(exist_ok=True)

    slug = title.replace(" ", "-").replace("،", "").replace("؟", "")[:50]
    filename = f"{slug}-{date.today().strftime('%Y%m%d')}.html"

    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Weaver نَسَّاج</title>
    <meta name="description" content="{content[:150]}">
    <meta property="og:title" content="{title}">
    <meta property="og:url" content="{SITE_URL}/blog/{slug}">
    <link rel="stylesheet" href="../css/main.css">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #0a0a1a; color: #e0e0ff; }}
        .article {{ max-width: 800px; margin: 2rem auto; padding: 2rem; background: rgba(255,255,255,0.05); border-radius: 16px; }}
        h1 {{ color: #a78bfa; font-size: 2rem; margin-bottom: 1rem; }}
        h2 {{ color: #7c3aed; margin-top: 2rem; }}
        p {{ line-height: 1.8; margin-bottom: 1rem; }}
        .meta {{ color: #888; font-size: 0.9rem; margin-bottom: 2rem; }}
        .tag {{ background: #7c3aed; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.8rem; margin: 0.2rem; display: inline-block; }}
    </style>
</head>
<body>
    <nav style="background:#1a0a2e;padding:1rem 2rem;display:flex;justify-content:space-between;align-items:center;">
        <a href="{SITE_URL}" style="color:#a78bfa;text-decoration:none;font-size:1.2rem;">✨ Weaver | نَسَّاج</a>
        <a href="{SITE_URL}/blog" style="color:#ccc;text-decoration:none;">← المدونة</a>
    </nav>
    <div class="article">
        <h1>{title}</h1>
        <div class="meta">
            ✍️ نَسَّاج AI | 📅 {date.today().strftime('%Y/%m/%d')} | 🏷️ {topic.get('cat', '')}
        </div>
        <div class="tags">
            {''.join([f'<span class="tag">{t}</span>' for t in topic.get('tags', '').split(',')])}
        </div>
        <div class="content" style="margin-top:2rem;">
            {content.replace(chr(10), '<br>')}
        </div>
        <div style="margin-top:3rem;padding:1.5rem;background:rgba(124,58,237,0.2);border-radius:12px;text-align:center;">
            <p>🔮 فسّر أحلامك بالذكاء الاصطناعي الآن!</p>
            <a href="{SITE_URL}/app/register" style="background:#7c3aed;color:white;padding:0.8rem 2rem;border-radius:8px;text-decoration:none;">جرّب مجاناً</a>
        </div>
    </div>
</body>
</html>"""

    with open(blog_dir / filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ تم حفظ ملف HTML: {filename}")

# ─── النشر على تيليجرام ───────────────────────────────────────────────────────

def post_to_telegram(content: str, channel_id: str = None):
    """نشر على تيليجرام"""
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ TELEGRAM_TOKEN غير موجود")
        return False

    target = channel_id or TELEGRAM_CHANNEL_ID
    if not target:
        print("⚠️ TELEGRAM_CHANNEL_ID غير موجود")
        return False

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": target,
                "text": content,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            },
            timeout=30
        )
        if response.status_code == 200:
            print(f"✅ تم النشر على تيليجرام")
            return True
        print(f"⚠️ خطأ تيليجرام: {response.text[:200]}")
        return False
    except Exception as e:
        print(f"⚠️ خطأ تيليجرام: {e}")
        return False

# ─── التسويق اليومي ───────────────────────────────────────────────────────────

def run_daily_marketing():
    """تشغيل حملة التسويق اليومية"""
    print(f"\n📢 [{datetime.now().strftime('%H:%M')}] تشغيل التسويق اليومي...")

    topic = random.choice(MARKETING_TOPICS)

    # توليد منشور تسويقي
    system = "أنت خبير تسويق رقمي. اكتب منشوراً جذاباً وقصيراً لمنصة Weaver لتفسير الأحلام."
    prompt = f"""اكتب منشوراً تسويقياً عن: {topic}
الرابط: {SITE_URL}
يجب أن يكون:
- قصير وجذاب (لا يزيد عن 200 حرف)
- يحتوي على إيموجي مناسبة
- يشجع على زيارة الموقع
- يحتوي على هاشتاقات عربية مناسبة"""

    post_content = generate_with_groq(prompt, system, max_tokens=300)
    if not post_content:
        post_content = f"🌙 {topic}\n\nفسّر أحلامك بالذكاء الاصطناعي!\n🔗 {SITE_URL}\n\n#تفسير_الأحلام #ذكاء_اصطناعي #Weaver"

    # النشر على تيليجرام
    post_to_telegram(post_content)

    # حفظ في سجل التسويق
    try:
        from app.models import log_marketing
        log_marketing("telegram", post_content, "sent")
    except Exception as e:
        print(f"⚠️ خطأ في حفظ سجل التسويق: {e}")

    print(f"✅ تم التسويق: {post_content[:80]}...")

# ─── إعادة تعيين العدادات اليومية ────────────────────────────────────────────

def reset_daily_counters():
    """إعادة تعيين عدادات الأحلام اليومية"""
    print(f"\n🔄 [{datetime.now().strftime('%H:%M')}] إعادة تعيين العدادات اليومية...")
    try:
        from app.models import reset_daily_dreams
        reset_daily_dreams()
        print("✅ تم إعادة تعيين العدادات")
    except Exception as e:
        print(f"⚠️ خطأ: {e}")

# ─── تقرير يومي ───────────────────────────────────────────────────────────────

def generate_daily_report():
    """توليد تقرير يومي"""
    print(f"\n📊 [{datetime.now().strftime('%H:%M')}] توليد التقرير اليومي...")
    try:
        from app.models import get_platform_stats, get_all_subscribers
        stats = get_platform_stats()
        subscribers = get_all_subscribers()

        report = f"""📊 تقرير Weaver اليومي - {date.today().strftime('%Y/%m/%d')}

👥 المستخدمون: {stats['total_users']}
🌙 الأحلام المفسرة: {stats['total_dreams']:,}
📧 المشتركون: {stats['total_subscribers']}
📝 مقالات المدونة: {stats['total_posts']}
👁️ المشاهدات اليوم: {stats['today_views']}

🔗 {SITE_URL}"""

        post_to_telegram(report)
        print("✅ تم إرسال التقرير اليومي")
    except Exception as e:
        print(f"⚠️ خطأ في التقرير: {e}")

# ─── الجدولة الزمنية ─────────────────────────────────────────────────────────

def setup_schedule():
    """إعداد الجدولة الزمنية"""
    # مقال يومي - الساعة 8 صباحاً
    schedule.every().day.at("08:00").do(generate_daily_blog)
    # تسويق - 3 مرات يومياً
    schedule.every().day.at("10:00").do(run_daily_marketing)
    schedule.every().day.at("15:00").do(run_daily_marketing)
    schedule.every().day.at("20:00").do(run_daily_marketing)
    # إعادة تعيين العدادات - منتصف الليل
    schedule.every().day.at("00:00").do(reset_daily_counters)
    # تقرير يومي - الساعة 9 مساءً
    schedule.every().day.at("21:00").do(generate_daily_report)

    print("✅ تم إعداد الجدولة الزمنية")
    print("📅 المهام المجدولة:")
    print("  - 08:00: مقال يومي")
    print("  - 10:00, 15:00, 20:00: تسويق")
    print("  - 00:00: إعادة تعيين العدادات")
    print("  - 21:00: تقرير يومي")

# ─── نقطة الدخول ─────────────────────────────────────────────────────────────

def run_once():
    """تشغيل مرة واحدة (للاختبار أو GitHub Actions)"""
    print("🚀 تشغيل نظام الأتمتة مرة واحدة...")
    generate_daily_blog()
    run_daily_marketing()
    generate_daily_report()
    print("✅ اكتملت المهام")

def run_continuous():
    """تشغيل مستمر على مدار الساعة"""
    print("🚀 تشغيل نظام الأتمتة المستمر...")
    setup_schedule()

    # تشغيل فوري عند البدء
    generate_daily_blog()
    run_daily_marketing()

    print("\n⏰ النظام يعمل... اضغط Ctrl+C للإيقاف")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    import sys
    if "--once" in sys.argv:
        run_once()
    else:
        run_continuous()
