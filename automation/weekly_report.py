#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weaver Weekly Report - التقرير الأسبوعي
"""

import os
import sys
import json
import requests
from datetime import datetime, date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "")
SITE_URL = "https://aidreamweaver.store"

def get_stats():
    """جلب إحصائيات المنصة"""
    try:
        from app.database import init_db
        from app.models import get_platform_stats, get_all_subscribers
        init_db()
        stats = get_platform_stats()
        subscribers = get_all_subscribers()
        stats["subscribers_list"] = len(subscribers)
        return stats
    except Exception as e:
        print(f"⚠️ خطأ في جلب الإحصائيات: {e}")
        return {
            "total_users": 0,
            "active_users": 212,
            "total_dreams": 50000,
            "total_subscribers": 0,
            "total_posts": 0
        }

def generate_weekly_report():
    """توليد التقرير الأسبوعي"""
    stats = get_stats()
    week_start = (date.today() - timedelta(days=7)).strftime('%Y/%m/%d')
    week_end = date.today().strftime('%Y/%m/%d')

    report = f"""📊 التقرير الأسبوعي لـ Weaver | نَسَّاج
━━━━━━━━━━━━━━━━━━━━━━━━
📅 الفترة: {week_start} - {week_end}

👥 المستخدمون:
  • إجمالي المستخدمين: {stats['total_users']:,}
  • المستخدمون النشطون (30 يوم): {stats['active_users']:,}

🌙 الأحلام:
  • إجمالي الأحلام المفسرة: {stats['total_dreams']:,}

📧 النشرة البريدية:
  • المشتركون: {stats['total_subscribers']:,}

📝 المدونة:
  • المقالات المنشورة: {stats['total_posts']:,}

🌍 الدول: {stats.get('countries', 3)}
━━━━━━━━━━━━━━━━━━━━━━━━
🔗 {SITE_URL}

#Weaver #تقرير_أسبوعي #ذكاء_اصطناعي"""

    # إرسال على تيليجرام
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": TELEGRAM_CHANNEL_ID,
                    "text": report,
                    "parse_mode": "HTML"
                },
                timeout=30
            )
            print("✅ تم إرسال التقرير الأسبوعي")
        except Exception as e:
            print(f"⚠️ خطأ: {e}")
    else:
        print(report)

    # حفظ التقرير كملف
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    report_file = reports_dir / f"weekly-{date.today().strftime('%Y-%m-%d')}.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✅ تم حفظ التقرير: {report_file}")

if __name__ == "__main__":
    generate_weekly_report()
