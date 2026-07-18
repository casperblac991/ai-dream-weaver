#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 المنسق المركزي لمزامنة جميع البوتات والوكلاء في نَسَّاج الأحلام
Weaver Central Sync Manager
"""
import os
import subprocess
import threading
import time
import schedule
from datetime import datetime

# قائمة البوتات والوكلاء المطلوب مزامنتها
AGENTS = [
    {"name": "Telegram Bot", "file": "all_bots.py", "type": "persistent"},
    {"name": "Civilization Reports Bot", "file": "civilization_bot.py", "type": "scheduled", "interval": "daily"},
    {"name": "Daily Blog Bot", "file": "daily_blog_bot.py", "type": "scheduled", "interval": "daily"},
    {"name": "Social Media Automation", "file": "social_media_automation.py", "type": "scheduled", "interval": "daily"},
    {"name": "AI Product Bot", "file": "bots/product_bot.py", "type": "scheduled", "interval": "weekly"}
]

def run_agent(file_path):
    """تشغيل وكيل معين"""
    print(f"🚀 [STARTING] {file_path}...")
    try:
        # استخدام python3 لتشغيل الوكيل
        subprocess.Popen(["python3", file_path])
    except Exception as e:
        print(f"❌ [ERROR] Failed to start {file_path}: {e}")

def sync_all():
    """مزامنة وتشغيل جميع الوكلاء"""
    print("="*50)
    print(f"🔄 [SYNC] Starting Central Synchronization at {datetime.now()}")
    print("="*50)
    
    for agent in AGENTS:
        if agent["type"] == "persistent":
            # تشغيل البوتات المستمرة في خيوط منفصلة أو عمليات خلفية
            run_agent(agent["file"])
        elif agent["type"] == "scheduled":
            # جدولة البوتات التي تعمل بشكل دوري
            if agent["interval"] == "daily":
                schedule.every().day.at("00:00").do(run_agent, agent["file"])
            elif agent["interval"] == "weekly":
                schedule.every().monday.at("01:00").do(run_agent, agent["file"])
            print(f"📅 [SCHEDULED] {agent['name']} set for {agent['interval']} execution.")

    print("="*50)
    print("✅ [SYNC] All agents synchronized and scheduled.")
    print("="*50)

if __name__ == "__main__":
    sync_all()
    
    # استمرار التشغيل لمتابعة الجدولة
    while True:
        schedule.run_pending()
        time.sleep(60)
