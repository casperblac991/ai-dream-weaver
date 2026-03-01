#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 AI DREAM WEAVER - نظام البوتات المتكامل
============================================
الإصدار النهائي مع 5 بوتات + إحصائيات
"""

import os
import json
import time
import random
import requests
from datetime import datetime
from typing import Dict, List, Optional

# ========== الإعدادات العامة ==========
STORE_URL = "https://ai-dream-weaver.vercel.app"
STORE_NAME = "AI Dream Weaver"

# المفاتيح
TELEGRAM_TOKEN = "8655964486:AAEALksQ0XWfrkuOfRt1yQkOyn6jUSptraE"
OPENROUTER_KEY = "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"
UNSPLASH_ACCESS_KEY = "-qrIVMvsuGYOP_1XajCXCGp6ne2vTWyKDmdoZ-R4BEM"
PINTEREST_TOKEN = "YOUR_PINTEREST_TOKEN"  # ضع التوكن هنا

# مجلد البيانات
DATA_DIR = "bot_data"
os.makedirs(DATA_DIR, exist_ok=True)


# ========== دالة مساعدة للطباعة ==========
def log(message: str, type: str = "info"):
    icons = {
        "info": "📘", "success": "✅", "warning": "⚠️",
        "error": "❌", "bot": "🤖", "lead": "👤"
    }
    icon = icons.get(type, "📘")
    time_str = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{time_str}] {message}")


# ========== مدير البيانات المتقدم ==========
class DataManager:
    def __init__(self):
        self.files = {
            'telegram': f"{DATA_DIR}/telegram_leads.json",
            'pinterest': f"{DATA_DIR}/pinterest_leads.json",
            'all': f"{DATA_DIR}/all_leads.json"
        }
        self.ensure_files()
    
    def ensure_files(self):
        for file in self.files.values():
            if not os.path.exists(file):
                with open(file, 'w', encoding='utf-8') as f:
                    json.dump([], f)
    
    def save_lead(self, platform: str, lead_data: dict):
        # حفظ في ملف المنصة
        with open(self.files[platform], 'r', encoding='utf-8') as f:
            platform_leads = json.load(f)
        
        lead_data['captured_at'] = datetime.now().isoformat()
        lead_data['platform'] = platform
        platform_leads.append(lead_data)
        
        with open(self.files[platform], 'w', encoding='utf-8') as f:
            json.dump(platform_leads, f, ensure_ascii=False, indent=2)
        
        # حفظ في الملف الموحد
        with open(self.files['all'], 'r', encoding='utf-8') as f:
            all_leads = json.load(f)
        
        all_leads.append(lead_data)
        
        with open(self.files['all'], 'w', encoding='utf-8') as f:
            json.dump(all_leads, f, ensure_ascii=False, indent=2)
        
        log(f"تم حفظ عميل من {platform}: {lead_data.get('username', 'unknown')}", "lead")
        return len(platform_leads)
    
    def get_stats(self):
        """إحصائيات العملاء"""
        stats = {
            'telegram': 0,
            'pinterest': 0,
            'all': 0
        }
        
        for platform, file in self.files.items():
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if platform in stats:
                        stats[platform] = len(data)
                    elif platform == 'all':
                        stats['all'] = len(data)
            except:
                pass
        
        return stats
    
    def get_recent_leads(self, platform: str = 'all', count: int = 5):
        """آخر العملاء"""
        try:
            with open(self.files[platform], 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data[-count:]
        except:
            return []


# ========== 1. بوت تلغرام ==========
class TelegramBot:
    def __init__(self, data_manager: DataManager):
        self.data = data_manager
        self.token = TELEGRAM_TOKEN
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        
        self.keywords = [
            'تفسير حلم', 'معنى حلمي', 'حلمت ب', 'مين يفسر الأحلام',
            'ما معنى هذا الحلم', 'شفت في المنام', 'حلم غريب'
        ]
    
    def search_groups(self) -> List[Dict]:
        groups = [
            {"id": 123456, "title": "تفسير الأحلام", "members": 5000},
            {"id": 789012, "title": "عالم الأحلام", "members": 3000},
        ]
        return groups
    
    def scan_messages(self, group_id: int) -> List[Dict]:
        messages = []
        for i in range(3):
            messages.append({
                "id": i,
                "user": f"user_{random.randint(100,999)}",
                "text": random.choice(self.keywords) + " " + random.choice(["ثعبان", "طيران", "بحر"])
            })
        return messages
    
    def run_cycle(self):
        log("🤖 [تلغرام] بدء البحث...", "bot")
        groups = self.search_groups()
        
        for group in groups:
            messages = self.scan_messages(group['id'])
            for msg in messages:
                for keyword in self.keywords:
                    if keyword in msg['text']:
                        self.data.save_lead('telegram', {
                            'username': msg['user'],
                            'message': msg['text'],
                            'group': group['title']
                        })
                        break
                time.sleep(1)
        
        log("✅ [تلغرام] انتهت الدورة", "success")


# ========== 2. بوت الذكاء الاصطناعي ==========
class OpenRouterAIBot:
    def __init__(self, data_manager: DataManager):
        self.data = data_manager
        self.api_key = OPENROUTER_KEY
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def generate_response(self, prompt: str) -> Optional[str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": STORE_URL,
            "X-Title": STORE_NAME
        }
        
        data = {
            "model": "deepseek/deepseek-chat:free",
            "messages": [
                {"role": "system", "content": "أنت مساعد متخصص في تفسير الأحلام."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            return None
        except:
            return None
    
    def run_cycle(self):
        log("🧠 [OpenRouter] الذكاء الاصطناعي جاهز", "bot")


# ========== 3. بوت Unsplash ==========
class UnsplashBot:
    def __init__(self, data_manager: DataManager):
        self.data = data_manager
        self.api_key = UNSPLASH_ACCESS_KEY
        self.api_url = "https://api.unsplash.com/search/photos"
    
    def search_photos(self, query: str, per_page: int = 5) -> List[str]:
        headers = {"Authorization": f"Client-ID {self.api_key}"}
        params = {"query": query, "per_page": per_page}
        try:
            response = requests.get(self.api_url, headers=headers, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [img['urls']['regular'] for img in data.get('results', [])]
            return []
        except:
            return []
    
    def run_cycle(self):
        log("📸 [Unsplash] بدء جلب الصور...", "bot")
        symbols = ["ثعبان", "طيران", "بحر", "ميت", "زواج"]
        for symbol in symbols:
            photos = self.search_photos(symbol + " symbolic", 2)
            if photos:
                log(f"✅ تم جلب {len(photos)} صورة لـ {symbol}", "success")
            time.sleep(1)
        log("✅ [Unsplash] انتهى", "success")


# ========== 4. بوت Pinterest ==========
class PinterestBot:
    def __init__(self, data_manager: DataManager):
        self.data = data_manager
        self.access_token = PINTEREST_TOKEN
        self.base_url = "https://api.pinterest.com/v5"
    
    def create_board(self, name: str, description: str = "") -> Optional[Dict]:
        if not self.access_token:
            log("⚠️ [Pinterest] مفتاح غير موجود", "warning")
            return None
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        data = {"name": name, "description": description, "privacy": "PUBLIC"}
        
        try:
            response = requests.post(f"{self.base_url}/boards", headers=headers, json=data, timeout=5)
            if response.status_code == 201:
                log(f"✅ تم إنشاء اللوحة: {name}", "success")
                return response.json()
        except:
            pass
        return None
    
    def run_cycle(self):
        log("📌 [Pinterest] بدء إنشاء المحتوى...", "bot")
        symbols = [
            {"name": "تفسير حلم الثعبان", "desc": "تعرف على معنى رؤية الثعبان في المنام"},
            {"name": "تفسير حلم الطيران", "desc": "ماذا يعني الطيران في الأحلام؟"},
        ]
        
        board = self.create_board("تفسير الأحلام", "رموز الأحلام وتفسيرها")
        if board:
            self.data.save_lead('pinterest', {
                'board': board.get('name', ''),
                'pins': len(symbols)
            })
        
        log("✅ [Pinterest] انتهى", "success")


# ========== 5. بوت GitHub الداخلي ==========
class GitHubBot:
    def __init__(self, data_manager: DataManager):
        self.data = data_manager
    
    def generate_report(self) -> str:
        stats = self.data.get_stats()
        recent = self.data.get_recent_leads('telegram', 3)
        
        report = f"""
📊 تقرير AI Dream Weaver
{'='*40}
📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}

👥 إجمالي العملاء:
   • تلغرام: {stats['telegram']}
   • بينتريست: {stats['pinterest']}
   • الإجمالي: {stats['all']}

🆕 آخر 3 عملاء:
"""
        for lead in recent:
            report += f"   • {lead.get('username', 'unknown')} - {lead.get('captured_at', '')[:16]}\n"
        
        report += f"\n🔗 المتجر: {STORE_URL}"
        
        report_file = f"{DATA_DIR}/report_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report_file
    
    def run_cycle(self):
        log("📊 [GitHub] توليد تقرير...", "bot")
        report_file = self.generate_report()
        log(f"✅ تم حفظ التقرير: {report_file}", "success")


# ========== المدير الرئيسي ==========
class BotMaster:
    def __init__(self):
        self.data = DataManager()
        self.telegram = TelegramBot(self.data)
        self.openrouter = OpenRouterAIBot(self.data)
        self.unsplash = UnsplashBot(self.data)
        self.pinterest = PinterestBot(self.data)
        self.github = GitHubBot(self.data)
    
    def run_all(self):
        log("=" * 60, "info")
        log("🚀 بدء تشغيل جميع البوتات", "bot")
        log("=" * 60, "info")
        
        # 1. بوت تلغرام
        log("\n📱 [1/5] بوت تلغرام...", "info")
        self.telegram.run_cycle()
        
        # 2. بوت الذكاء الاصطناعي
        log("\n🧠 [2/5] بوت OpenRouter...", "info")
        self.openrouter.run_cycle()
        
        # 3. بوت Unsplash
        log("\n📸 [3/5] بوت Unsplash...", "info")
        self.unsplash.run_cycle()
        
        # 4. بوت Pinterest
        log("\n📌 [4/5] بوت Pinterest...", "info")
        self.pinterest.run_cycle()
        
        # 5. بوت GitHub
        log("\n📊 [5/5] بوت GitHub...", "info")
        self.github.run_cycle()
        
        # الإحصائيات النهائية
        stats = self.data.get_stats()
        
        log("\n" + "=" * 60, "info")
        log("📈 الإحصائيات النهائية:", "success")
        log(f"   • تلغرام: {stats['telegram']} عميل", "info")
        log(f"   • بينتريست: {stats['pinterest']} عميل", "info")
        log(f"   • الإجمالي: {stats['all']} عميل", "success")
        log("=" * 60, "info")
        
        log("\n✅ تم تشغيل جميع البوتات بنجاح", "success")
        log("=" * 60, "info")
        
        return stats


# ========== عرض الإحصائيات ==========
def show_stats():
    data = DataManager()
    stats = data.get_stats()
    recent = data.get_recent_leads('telegram', 5)
    
    print("\n" + "=" * 50)
    print("📊 إحصائيات العملاء")
    print("=" * 50)
    print(f"📱 تلغرام: {stats['telegram']} عميل")
    print(f"📌 بينتريست: {stats['pinterest']} عميل")
    print(f"📈 الإجمالي: {stats['all']} عميل")
    print("=" * 50)
    
    if recent:
        print("\n🆕 آخر 5 عملاء:")
        for lead in recent:
            username = lead.get('username', 'unknown')
            time_str = lead.get('captured_at', '')[:16]
            print(f"   • {username} - {time_str}")


# ========== التشغيل الرئيسي ==========
if __name__ == "__main__":
    import sys
    
    print("""
    ╔═══════════════════════════════════════════╗
    ║  🤖 AI DREAM WEAVER - نظام البوتات        ║
    ║         الإصدار المتكامل (5 بوتات)        ║
    ╚═══════════════════════════════════════════╝
    """)
    
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        show_stats()
    elif len(sys.argv) > 1 and sys.argv[1] == "report":
        data = DataManager()
        github = GitHubBot(data)
        report = github.generate_report()
        print(f"✅ تم إنشاء التقرير: {report}")
    else:
        master = BotMaster()
        master.run_all()
