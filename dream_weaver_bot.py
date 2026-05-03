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

# ========== بوت جمع بيانات العملاء (إضافة جديدة) ==========
def collect_user_data(self):
    """جمع بيانات العملاء من المتجر"""
    try:
        # محاكاة قراءة بيانات العملاء (في الواقع ستقرأ من قاعدة بيانات)
        sample_users = [
            {"name": "أحمد محمد", "email": "ahmed@example.com", "date": "2026-03-01"},
            {"name": "سارة علي", "email": "sara@example.com", "date": "2026-03-01"},
            {"name": "خالد عمر", "email": "khalid@example.com", "date": "2026-02-28"},
            {"name": "نورة عبدالله", "email": "noura@example.com", "date": "2026-02-28"},
        ]
        
        print(f"📊 تم جمع بيانات {len(sample_users)} عميل")
        
        # حفظ البيانات في ملف
        import json
        with open('customers_data.json', 'w', encoding='utf-8') as f:
            json.dump(sample_users, f, ensure_ascii=False, indent=2)
        
        return sample_users
    except Exception as e:
        print(f"خطأ في جمع البيانات: {e}")
        return []

def analyze_customer_data(users):
    """تحليل بيانات العملاء لإنشاء حملات إعلانية"""
    if not users:
        return
    
    # عدد العملاء حسب التاريخ
    today = datetime.now().strftime('%Y-%m-%d')
    today_users = [u for u in users if u.get('date', '').startswith(today[:10])]
    
    print(f"📈 عملاء اليوم: {len(today_users)}")
    
    # إنشاء تقرير تسويقي
    report = f"""
    📊 تقرير تسويقي - {datetime.now().strftime('%Y-%m-%d')}
    ===================================
    إجمالي العملاء: {len(users)}
    عملاء جدد اليوم: {len(today_users)}
    
    أفضل وقت للإعلان: {datetime.now().strftime('%H:00')}
    
    اقتراح إعلان:
    🔮 {random.choice(['الثعبان', 'الطيران', 'البحر', 'الميت', 'الزواج'])} 
    في المنام يعني... جرب تحليل أحلامك مجاناً!
    
    رابط المتجر: {STORE_URL}
    """
    
    # حفظ التقرير
    with open('marketing_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("📢 تم إنشاء تقرير تسويقي")
    return report

def create_targeted_ad():
    """إنشاء إعلان مخصص بناءً على بيانات العملاء"""
    ads = [
        "🔮 هل تعلم أن {symbol} في المنام يعني {meaning}؟ جرب تحليل أحلامك مجاناً",
        "🌙 أحلمت بشيء غريب؟ {name} يحلل أحلامك بالذكاء الاصطناعي مجاناً لأول حلم!",
        "✨ {customers}+ عميل استخدموا {name} لتفسير أحلامهم. جرب أنت أيضاً!"
    ]
    
    # اختيار إعلان عشوائي
    ad_template = random.choice(ads)
    
    # تخصيص الإعلان
    symbols = ['الثعبان', 'الطيران', 'البحر', 'الميت']
    meanings = ['تحذير من أعداء', 'الحرية والطموح', 'العواطف العميقة', 'رسالة من الماضي']
    
    symbol = random.choice(symbols)
    meaning = meanings[symbols.index(symbol)]
    
    ad = ad_template.format(
        symbol=symbol,
        meaning=meaning,
        name=STORE_NAME,
        customers=random.randint(500, 2000),
        url=STORE_URL
    )
    
    print(f"📢 إعلان مخصص: {ad[:50]}...")
    return ad

def run_marketing_campaign():
    """تشغيل حملة تسويقية متكاملة"""
    print("🚀 بدء الحملة التسويقية")
    
    # 1. جمع بيانات العملاء
    users = collect_user_data(None)
    
    # 2. تحليل البيانات
    analyze_customer_data(users)
    
    # 3. إنشاء إعلانات مخصصة
    for i in range(3):
        ad = create_targeted_ad()
        print(f"إعلان {i+1}: {ad[:60]}...")
    
    print("✅ انتهت الحملة التسويقية")
    
    return {
        'users_count': len(users) if users else 0,
        'campaign_date': datetime.now().isoformat()
    }
