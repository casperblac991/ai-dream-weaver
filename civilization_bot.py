#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌍 بوت موسوعة الحضارات - يولد تقريراً يومياً عن حضارة قديمة وطقوس تفسير الأحلام
يعمل تلقائياً كل يوم على PythonAnywhere أو GitHub Actions
"""

import os
import json
import requests
import random
from datetime import datetime
from typing import Dict, List
import schedule
import time

# ========== الإعدادات ==========
OPENROUTER_KEY = os.environ.get('OPENROUTER_KEY', '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')
UNSPLASH_KEY = os.environ.get('UNSPLASH_ACCESS_KEY', '-qrIVMvsuGYOP_1XajCXCGp6ne2vTWyKDmdoZ-R4BEM')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '8655964486:AAEALksQ0XWfrkuOfRt1yQkOyn6jUSptraE')

# قائمة الحضارات (كل يوم يشتغل على واحدة)
CIVILIZATIONS = [
    {
        "id": "mesopotamia",
        "name": "بلاد الرافدين (سومر، بابل، آشور)",
        "period": "3100 ق.م - 600 ق.م",
        "keywords": "dream interpretation Mesopotamia, Babylonian dream rituals, Gilgamesh dreams"
    },
    {
        "id": "egypt",
        "name": "مصر القديمة",
        "period": "3000 ق.م - 30 ق.م",
        "keywords": "ancient Egyptian dream interpretation, Chester Beatty papyrus, Egyptian dream temples"
    },
    {
        "id": "greece",
        "name": "اليونان القديمة",
        "period": "800 ق.م - 200 م",
        "keywords": "Greek dream interpretation, Asclepius temples, Artemidorus Oneirocritica"
    },
    {
        "id": "rome",
        "name": "روما القديمة",
        "period": "500 ق.م - 400 م",
        "keywords": "Roman dream interpretation, Cicero De Divinatione"
    },
    {
        "id": "china",
        "name": "الصين القديمة",
        "period": "500 ق.م - 1000 م",
        "keywords": "ancient Chinese dream interpretation, Zhuangzi butterfly dream, Taoist dream rituals"
    },
    {
        "id": "india",
        "name": "الهند القديمة",
        "period": "1500 ق.م - 500 م",
        "keywords": "ancient Indian dream interpretation, Atharvaveda dreams, Hindu dream rituals"
    },
    {
        "id": "mesoamerica",
        "name": "حضارة المايا",
        "period": "2000 ق.م - 1500 م",
        "keywords": "Mayan dream interpretation, Mesoamerican dream rituals, Maya calendar dreams"
    },
    {
        "id": "inca",
        "name": "حضارة الإنكا",
        "period": "1200 - 1572 م",
        "keywords": "Inca dream interpretation, Andean dream rituals"
    },
    {
        "id": "persia",
        "name": "بلاد فارس (الإمبراطورية الأخمينية)",
        "period": "550 - 330 ق.م",
        "keywords": "Persian dream interpretation, Zoroastrian dreams, Avesta dreams"
    },
    {
        "id": "canaan",
        "name": "الحضارة الكنعانية والأوغاريتية",
        "period": "1500 - 1200 ق.م",
        "keywords": "Canaanite dream interpretation, Ugaritic tablets, El dreams"
    }
]

class CivilizationReportBot:
    """بوت يولد تقارير يومية عن حضارات العالم"""
    
    def __init__(self):
        self.reports_dir = "reports"
        os.makedirs(self.reports_dir, exist_ok=True)
        self.index_file = f"{self.reports_dir}/index.json"
        self.load_index()
    
    def load_index(self):
        """تحميل فهرس التقارير"""
        if os.path.exists(self.index_file):
            with open(self.index_file, 'r', encoding='utf-8') as f:
                self.index = json.load(f)
        else:
            self.index = {
                "total_reports": 0,
                "last_update": None,
                "reports": []
            }
    
    def save_index(self):
        """حفظ فهرس التقارير"""
        self.index["last_update"] = datetime.now().isoformat()
        self.index["total_reports"] = len(self.index["reports"])
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def search_web_for_info(self, civilization: Dict) -> str:
        """
        البحث عن معلومات عن الحضارة (محاكاة - في النسخة الكاملة نستخدم البحث API)
        ولكن هنا نعتمد على ذكاء OpenRouter لأنه يملك معرفة مسبقة
        """
        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""
        اكتب تقريراً شاملاً عن تفسير الأحلام في {civilization['name']} ({civilization['period']}).
        
        يجب أن يتضمن التقرير:
        1. مقدمة عن الحضارة واهتمامها بالأحلام
        2. طقوس تفسير الأحلام (كيف كانوا يحصلون على الأحلام؟ هل كانوا ينامون في المعابد؟)
        3. المعتقدات المرتبطة (هل اعتبروا الأحلام رسائل من الآلهة؟ من الأسلاف؟)
        4. أشهر الأحلام المسجلة في هذه الحضارة
        5. أشهر المفسرين أو الكهنة المتخصصين
        6. الرموز الشائعة في أحلامهم وتفسيرها
        7. التشابه مع حضارات أخرى (إن وجد)
        8. خاتمة وتأثير هذه التقاليد على الحضارات اللاحقة
        
        اجعل التقرير غنياً بالمعلومات التاريخية الدقيقة. استشهد بالمصادر إن أمكن.
        اكتب بأسلوب أكاديمي سلس. حوالي 1000-1500 كلمة.
        
        المطلوب: نص التقرير فقط (بدون JSON، بدون تعليمات).
        """
        
        data = {
            "model": "deepseek/deepseek-chat:free",  # نموذج مجاني
            "messages": [
                {"role": "system", "content": "أنت مؤرخ متخصص في حضارات العالم القديم وطقوس تفسير الأحلام. لديك موسوعة ضخمة من المعلومات."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                return content
            else:
                print(f"خطأ OpenRouter: {response.status_code}")
                return self.get_fallback_text(civilization)
        except Exception as e:
            print(f"استثناء: {e}")
            return self.get_fallback_text(civilization)
    
    def get_fallback_text(self, civilization: Dict) -> str:
        """نص احتياطي إذا فشل الذكاء الاصطناعي"""
        return f"""
        # {civilization['name']} - طقوس تفسير الأحلام

        {civilization['name']} من أعظم الحضارات التي اهتمت بتفسير الأحلام ({civilization['period']}).

        ## طقوس تفسير الأحلام
        كان الكهنة المختصون يقومون بطقوس خاصة لاستقبال الأحلام وتفسيرها. من أشهر الطقوس النوم في المعابد المقدسة طلباً للرؤيا.

        ## المعتقدات
        اعتقدوا أن الأحلام رسائل من الآلهة أو من الأسلاف الراحلين.

        ## أشهر الأحلام
        وردت أحلام كثيرة في نصوصهم المقدسة وألواحهم الطينية.

        ## التأثير
        أثرت هذه الحضارة على الحضارات المجاورة في طرق تفسير الأحلام.
        """
    
    def generate_image_prompt(self, civilization: Dict) -> str:
        """توليد كلمات مفتاحية لصورة التقرير"""
        return f"{civilization['name']} ancient civilization dream interpretation ritual painting"
    
    def search_unsplash_image(self, query: str) -> str:
        """البحث عن صورة من Unsplash"""
        if not UNSPLASH_KEY:
            return "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400"
        
        try:
            url = f"https://api.unsplash.com/search/photos?query={query}&per_page=5"
            headers = {"Authorization": f"Client-ID {UNSPLASH_KEY}"}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['results']:
                    return data['results'][0]['urls']['regular']
        except:
            pass
        return "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400"
    
    def create_pdf(self, title: str, content: str, image_url: str, civilization: Dict) -> str:
        """
        إنشاء ملف PDF (في هذه المرحلة ننشئ HTML ونحوله لاحقاً)
        ولكن للبساطة، سننشئ ملف HTML منسق
        """
        filename = f"{civilization['id']}_{datetime.now().strftime('%Y%m%d')}.html"
        filepath = f"{self.reports_dir}/{filename}"
        
        html_template = f"""<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - نَسَّاج الأحلام</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #0a0f1e; color: white; line-height: 1.8; padding: 40px; }}
        .report-container {{ max-width: 900px; margin: 0 auto; background: rgba(255,255,255,0.05); border: 2px solid #ffd700; border-radius: 30px; padding: 40px; }}
        h1 {{ color: #ffd700; font-size: 2.5em; }}
        h2 {{ color: #ff00ff; margin: 30px 0 15px; }}
        .cover-image {{ width: 100%; max-height: 400px; object-fit: cover; border-radius: 20px; margin: 20px 0; border: 2px solid #ffd700; }}
        .date {{ color: #00ffff; margin: 10px 0 30px; }}
        p {{ margin: 15px 0; }}
        .footer {{ margin-top: 50px; text-align: center; color: #ffd700; }}
    </style>
</head>
<body>
    <div class="report-container">
        <h1>{title}</h1>
        <div class="date">📅 {datetime.now().strftime('%Y-%m-%d')} | 🏛️ {civilization['period']}</div>
        <img src="{image_url}" alt="{title}" class="cover-image">
        <div class="content">
            {content.replace(chr(10), '<br>')}
        </div>
        <div class="footer">
            <p>🔮 نَسَّاج الأحلام - موسوعة تفسير الأحلام عبر الحضارات</p>
            <p>https://ai-dream-weaver.vercel.app/reports/{filename}</p>
        </div>
    </div>
</body>
</html>"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        return filename
    
    def update_website_reports_list(self, filename: str, title: str):
        """تحديث قائمة التقارير في الموقع"""
        report_entry = {
            "id": filename.replace('.html', ''),
            "title": title,
            "date": datetime.now().isoformat(),
            "file": filename
        }
        
        self.index["reports"].append(report_entry)
        self.save_index()
        
        print(f"✅ تم إضافة التقرير: {title}")
    
    def notify_telegram(self, title: str, filename: str):
        """إرسال إشعار على تلغرام"""
        if not TELEGRAM_TOKEN:
            return
        
        try:
            message = f"🔮 *تقرير جديد في نَسَّاج الأحلام*\n\n📚 {title}\n\n🔗 https://ai-dream-weaver.vercel.app/reports/{filename}"
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            data = {
                "chat_id": "@nasaj_ahlam",  # أو معرف قناتك
                "text": message,
                "parse_mode": "Markdown"
            }
            requests.post(url, json=data, timeout=5)
        except:
            pass
    
    def generate_daily_report(self):
        """توليد تقرير اليوم"""
        # اختيار حضارة (إما دورياً أو عشوائياً)
        today_index = datetime.now().timetuple().tm_yday % len(CIVILIZATIONS)
        civilization = CIVILIZATIONS[today_index]
        
        print(f"🚀 بدء توليد تقرير عن: {civilization['name']}")
        
        # البحث عن المعلومات
        content = self.search_web_for_info(civilization)
        
        # البحث عن صورة
        image_query = self.generate_image_prompt(civilization)
        image_url = self.search_unsplash_image(image_query)
        
        # إنشاء التقرير
        title = f"{civilization['name']} - طقوس تفسير الأحلام"
        filename = self.create_pdf(title, content, image_url, civilization)
        
        # تحديث الفهرس
        self.update_website_reports_list(filename, title)
        
        # إرسال إشعار
        self.notify_telegram(title, filename)
        
        print(f"🎉 تم الانتهاء من تقرير: {filename}")
        return filename
    
    def run_daily(self):
        """تشغيل البوت يومياً"""
        print("=" * 50)
        print("🌍 بوت موسوعة الحضارات - بدء الدورة اليومية")
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 50)
        
        self.generate_daily_report()
        
        print("✅ اكتملت الدورة اليومية")
        print("=" * 50)


# ========== التشغيل الرئيسي ==========
if __name__ == "__main__":
    import sys
    
    print("""
    ╔═══════════════════════════════════════════╗
    ║  🌍 موسوعة الحضارات - بوت التقارير اليومي ║
    ║         يصنع تقريراً جديداً كل يوم        ║
    ╚═══════════════════════════════════════════╝
    """)
    
    bot = CivilizationReportBot()
    
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        # تشغيل لمرة واحدة
        bot.generate_daily_report()
    else:
        # تشغيل دائم
        print("🚀 البوت سيعمل يومياً عند الساعة 00:00")
        
        # تشغيل فوري للتجربة
        bot.generate_daily_report()
        
        # جدولة يومية
        schedule.every().day.at("00:00").do(bot.generate_daily_report)
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # فحص كل دقيقة
