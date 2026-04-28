#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weaver Email System - نظام البريد الإلكتروني
إدارة المشتركين وإرسال النشرات البريدية
"""

import os
import sys
import json
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# ─── الإعدادات ────────────────────────────────────────────────────────────────
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "noreply@aidreamweaver.store")
FROM_NAME = "Weaver | نَسَّاج"
SITE_URL = "https://aidreamweaver.store"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# ─── قوالب البريد الإلكتروني ─────────────────────────────────────────────────

EMAIL_TEMPLATE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #f0f0ff; margin: 0; padding: 0; }}
        .container {{ max-width: 600px; margin: 2rem auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #1a0a2e, #7c3aed); padding: 2rem; text-align: center; }}
        .header h1 {{ color: #a78bfa; font-size: 1.8rem; margin-bottom: 0.5rem; }}
        .header p {{ color: #ccc; font-size: 0.9rem; }}
        .content {{ padding: 2rem; color: #333; line-height: 1.8; }}
        .content h2 {{ color: #7c3aed; margin-bottom: 1rem; }}
        .content p {{ margin-bottom: 1rem; }}
        .cta-btn {{ display: inline-block; background: linear-gradient(135deg, #7c3aed, #a78bfa); color: white; padding: 1rem 2rem; border-radius: 8px; text-decoration: none; font-weight: bold; margin: 1rem 0; }}
        .footer {{ background: #f8f8ff; padding: 1.5rem 2rem; text-align: center; color: #888; font-size: 0.85rem; border-top: 1px solid #eee; }}
        .footer a {{ color: #7c3aed; text-decoration: none; }}
        .dream-box {{ background: linear-gradient(135deg, rgba(124,58,237,0.1), rgba(167,139,250,0.1)); border: 1px solid rgba(124,58,237,0.3); border-radius: 12px; padding: 1.5rem; margin: 1.5rem 0; }}
        .dream-symbol {{ font-size: 2rem; margin-bottom: 0.5rem; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✨ Weaver | نَسَّاج</h1>
            <p>منصة تفسير الأحلام بالذكاء الاصطناعي</p>
        </div>
        <div class="content">
            {content}
        </div>
        <div class="footer">
            <p>© 2025 Weaver | نَسَّاج</p>
            <p><a href="{site_url}">زيارة الموقع</a> | <a href="{site_url}/blog">المدونة</a> | <a href="{unsubscribe_url}">إلغاء الاشتراك</a></p>
        </div>
    </div>
</body>
</html>"""

WELCOME_EMAIL_CONTENT = """
<h2>🌙 مرحباً {name}!</h2>
<p>شكراً لانضمامك إلى مجتمع <strong>Weaver | نَسَّاج</strong> - منصة تفسير الأحلام بالذكاء الاصطناعي.</p>

<div class="dream-box">
    <div class="dream-symbol">🔮</div>
    <p><strong>ما الذي ينتظرك؟</strong></p>
    <ul>
        <li>✅ تفسير أحلامك بأسلوب ابن سيرين والذكاء الاصطناعي</li>
        <li>✅ مقالات ثقافية يومية عن الأحلام والحضارات</li>
        <li>✅ توليد صور فنية لأحلامك</li>
        <li>✅ مجتمع من عشاق تفسير الأحلام</li>
    </ul>
</div>

<p>ابدأ رحلتك الآن وفسّر أول حلم لك مجاناً!</p>
<a href="{site_url}/app/analyze" class="cta-btn">🌙 فسّر حلمك الآن</a>

<p style="color:#888;font-size:0.9rem;">إذا كان لديك أي سؤال، تواصل معنا عبر <a href="https://t.me/aidreamweaver_bot">بوت تيليجرام</a></p>
"""

NEWSLETTER_CONTENT = """
<h2>📚 نشرة Weaver الأسبوعية</h2>
<p>مرحباً {name}! إليك أبرز ما نشرناه هذا الأسبوع:</p>

<div class="dream-box">
    <p><strong>🌙 رمز الأسبوع: {symbol}</strong></p>
    <p>{meaning}</p>
</div>

<h3>📝 أحدث المقالات:</h3>
{articles_html}

<p>فسّر أحلامك الآن بالذكاء الاصطناعي!</p>
<a href="{site_url}/app/analyze" class="cta-btn">🔮 جرّب مجاناً</a>
"""

DREAM_SYMBOLS = [
    {"symbol": "الثعبان 🐍", "meaning": "يرمز إلى تحذير من عدو خفي أو خطر قادم. في التراث الإسلامي يدل على العدو."},
    {"symbol": "الطيران ✈️", "meaning": "يرمز إلى الحرية والطموح والتحرر من القيود. بشارة بالنجاح والتقدم."},
    {"symbol": "البحر 🌊", "meaning": "يرمز إلى العواطف العميقة واللاوعي. قد يدل على الملك أو العلم."},
    {"symbol": "النار 🔥", "meaning": "يرمز إلى التحول والتطهير والطاقة الداخلية. قد تكون بشارة أو تحذيراً."},
    {"symbol": "الذهب 🥇", "meaning": "يرمز إلى الثروة والنجاح والمكانة الاجتماعية. بشارة بالخير."},
]

# ─── إرسال البريد الإلكتروني ─────────────────────────────────────────────────

def send_email(to_email: str, to_name: str, subject: str, html_content: str) -> bool:
    """إرسال بريد إلكتروني"""
    if not SMTP_USER or not SMTP_PASS:
        print(f"📧 [محاكاة] إرسال إلى {to_email}: {subject}")
        return True

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg['To'] = f"{to_name} <{to_email}>"

        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(FROM_EMAIL, to_email, msg.as_string())

        print(f"✅ تم الإرسال إلى: {to_email}")
        return True
    except Exception as e:
        print(f"⚠️ خطأ في الإرسال إلى {to_email}: {e}")
        return False

def send_welcome_email(email: str, name: str = "عزيزي المشترك"):
    """إرسال بريد الترحيب"""
    content = WELCOME_EMAIL_CONTENT.format(
        name=name or "عزيزي المشترك",
        site_url=SITE_URL
    )
    html = EMAIL_TEMPLATE.format(
        subject="مرحباً في Weaver | نَسَّاج 🌙",
        content=content,
        site_url=SITE_URL,
        unsubscribe_url=f"{SITE_URL}/unsubscribe?email={email}"
    )
    return send_email(email, name, "مرحباً في Weaver | نَسَّاج 🌙", html)

def send_weekly_newsletter():
    """إرسال النشرة الأسبوعية لجميع المشتركين"""
    print(f"\n📧 [{datetime.now().strftime('%H:%M')}] إرسال النشرة الأسبوعية...")

    try:
        from app.database import init_db
        from app.models import get_all_subscribers, get_blog_posts
        init_db()

        subscribers = get_all_subscribers()
        posts = get_blog_posts(limit=3)
        symbol = random.choice(DREAM_SYMBOLS)

        articles_html = ""
        for post in posts:
            articles_html += f'<p>📖 <a href="{SITE_URL}/blog/{post["slug"]}" style="color:#7c3aed;">{post["title"]}</a></p>'

        sent_count = 0
        for sub in subscribers:
            content = NEWSLETTER_CONTENT.format(
                name=sub.get("name") or "عزيزي المشترك",
                symbol=symbol["symbol"],
                meaning=symbol["meaning"],
                articles_html=articles_html,
                site_url=SITE_URL
            )
            html = EMAIL_TEMPLATE.format(
                subject=f"🌙 نشرة Weaver الأسبوعية - {date.today().strftime('%Y/%m/%d')}",
                content=content,
                site_url=SITE_URL,
                unsubscribe_url=f"{SITE_URL}/unsubscribe?email={sub['email']}"
            )
            if send_email(sub["email"], sub.get("name", ""), f"🌙 نشرة Weaver الأسبوعية", html):
                sent_count += 1

        print(f"✅ تم إرسال النشرة إلى {sent_count}/{len(subscribers)} مشترك")
        return sent_count
    except Exception as e:
        print(f"⚠️ خطأ في النشرة: {e}")
        return 0

def export_subscribers_csv():
    """تصدير قائمة المشتركين كـ CSV"""
    try:
        from app.database import init_db
        from app.models import get_all_subscribers
        init_db()

        subscribers = get_all_subscribers()
        csv_file = Path(__file__).parent.parent / "data" / "subscribers.csv"
        csv_file.parent.mkdir(exist_ok=True)

        with open(csv_file, "w", encoding="utf-8") as f:
            f.write("email,name,source,subscribed_at\n")
            for sub in subscribers:
                f.write(f"{sub['email']},{sub.get('name','')},{sub.get('source','')},{sub.get('subscribed_at','')}\n")

        print(f"✅ تم تصدير {len(subscribers)} مشترك إلى {csv_file}")
        return str(csv_file)
    except Exception as e:
        print(f"⚠️ خطأ في التصدير: {e}")
        return None

if __name__ == "__main__":
    import sys
    if "--welcome" in sys.argv:
        # اختبار بريد الترحيب
        send_welcome_email("test@example.com", "مستخدم تجريبي")
    elif "--newsletter" in sys.argv:
        send_weekly_newsletter()
    elif "--export" in sys.argv:
        export_subscribers_csv()
    else:
        print("الاستخدام: python email_system.py --welcome | --newsletter | --export")
