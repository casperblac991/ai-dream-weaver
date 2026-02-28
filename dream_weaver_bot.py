#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 AI Dream Weaver Bot - نسخة GitHub
======================================
"""

import os
import time
import random
import requests
from datetime import datetime

# ========== الإعدادات ==========
STORE_URL = "https://ai-dream-weaver.vercel.app"
STORE_NAME = "AI Dream Weaver"

# ========== قاموس الرموز ==========
SYMBOLS = {
    'arabic': [
        {'symbol': 'الثعبان', 'meaning': 'تحذير من أعداء خفيين'},
        {'symbol': 'الطيران', 'meaning': 'الحرية والطموح'},
        {'symbol': 'البحر', 'meaning': 'العواطف العميقة'},
        {'symbol': 'الميت', 'meaning': 'رسالة من الماضي'}
    ]
}

# ========== قوالب الإعلانات ==========
AD_TEMPLATES = {
    'arabic': [
        "🔮 {symbol} في المنام يعني {meaning}! \n\nاكتشف تفسير أحلامك بالذكاء الاصطناعي في {url} مجاناً",
        "🌙 أحلمت بشيء غريب؟ {name} يحلل أحلامك بالذكاء الاصطناعي خلال ثوانٍ! {url}"
    ]
}

class GitHubBot:
    """البوت المصمم للتشغيل على GitHub Actions"""
    
    def __init__(self):
        self.url = STORE_URL
        self.name = STORE_NAME
        self.key = os.environ.get('OPENAI_API_KEY', '')
        
        if not self.key:
            print("⚠️ تنبيه: مفتاح OpenAI غير موجود")
        else:
            print("✅ مفتاح OpenAI موجود")
    
    def log(self, msg):
        now = datetime.now().strftime('%H:%M:%S')
        print(f"[{now}] {msg}")
    
    def find_customers(self):
        """محاكاة البحث عن عملاء"""
        self.log("جاري البحث عن عملاء محتملين...")
        customers = []
        
        for i in range(3):
            customers.append({
                'id': i,
                'question': random.choice([
                    'تفسير حلم الثعبان',
                    'حلمت أنني أطير',
                    'ما معنى البحر في المنام'
                ])
            })
        
        self.log(f"✅ وجدت {len(customers)} عميل محتمل")
        return customers
    
    def reply_to_customers(self, customers):
        """الرد على العملاء"""
        for c in customers:
            reply = f"مرحباً! يمكنك تحليل حلمك مجاناً على {self.url}"
            self.log(f"الرد على سؤال: {c['question']}")
            time.sleep(1)
        
        return len(customers)
    
    def create_ad(self):
        """صنع إعلان جديد"""
        symbol = random.choice(SYMBOLS['arabic'])
        template = random.choice(AD_TEMPLATES['arabic'])
        
        ad = template.format(
            symbol=symbol['symbol'],
            meaning=symbol['meaning'],
            url=self.url,
            name=self.name
        )
        
        self.log(f"✅ تم صنع إعلان جديد")
        print(f"\n📢 الإعلان:\n{ad}\n")
        return ad
    
    def run(self):
        """تشغيل البوت"""
        print("\n" + "="*50)
        print("🤖 AI Dream Weaver Bot بدأ العمل")
        print("="*50)
        
        # 1. البحث عن عملاء
        customers = self.find_customers()
        replied = self.reply_to_customers(customers)
        
        # 2. صنع إعلان
        self.create_ad()
        
        # 3. إحصائيات
        print("\n" + "="*50)
        print(f"✅ تم الرد على {replied} عملاء")
        print("✅ تم صنع إعلان جديد")
        print("="*50)

if __name__ == "__main__":
    bot = GitHubBot()
    bot.run()
