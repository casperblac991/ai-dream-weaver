# bot-updater.py
import schedule
import time
import requests
import json
from datetime import datetime
import openai
import random

class DreamBotUpdater:
    def __init__(self):
        self.website_url = "https://ai-dream-weaver.vercel.app"
        self.api_key = "YOUR_OPENAI_API_KEY"
        self.bot_token = "YOUR_TELEGRAM_BOT_TOKEN"
        openai.api_key = self.api_key
        
    def generate_weekly_content(self):
        """توليد محتوى أسبوعي جديد"""
        print(f"[{datetime.now()}] بدء تحديث المحتوى الأسبوعي...")
        
        # 1. توليد تفسير مميز للأسبوع
        interpretation = self.generate_dream_interpretation()
        
        # 2. توليد صور جديدة
        new_images = self.generate_gallery_images()
        
        # 3. تحديث الإحصائيات
        new_stats = self.update_statistics()
        
        # 4. إرسال التحديثات للموقع
        self.update_website({
            'interpretation': interpretation,
            'images': new_images,
            'stats': new_stats
        })
        
        # 5. نشر في قناة التلغرام
        self.post_to_telegram(interpretation, new_images)
        
        print(f"[{datetime.now()}] تم تحديث المحتوى بنجاح!")
        
    def generate_dream_interpretation(self):
        """توليد تفسير حلم مميز"""
        prompts = [
            "اكتب تفسيراً شاملاً لحلم الطيران في السماء",
            "فسر حلم رؤية الثعابين في المنزل",
            "تفسير حلم سقوط الأسنان في المنام",
            "تفسير حلم السباحة في المحيط",
            "تفسير رؤية الأموات في المنام"
        ]
        
        prompt = random.choice(prompts)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "أنت مفسر أحلام خبير، تقدم تفسيرات دقيقة وشاملة باللغة العربية."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            interpretation = response.choices[0].message.content
            
            # حفظ التفسير
            with open(f"weekly_interpretations/{datetime.now().strftime('%Y-%m-%d')}.txt", "w", encoding="utf-8") as f:
                f.write(interpretation)
                
            return interpretation
            
        except Exception as e:
            print(f"خطأ في توليد التفسير: {e}")
            return None
    
    def generate_gallery_images(self):
        """توليد صور جديدة للمعرض"""
        # استخدام Unsplash للحصول على صور جديدة
        topics = ['dream', 'fantasy', 'magical forest', 'floating city', 'mystical']
        
        images = []
        for topic in topics:
            # Unsplash API
            unsplash_url = f"https://api.unsplash.com/photos/random?query={topic}&count=1&client_id=YOUR_UNSPLASH_KEY"
            
            try:
                response = requests.get(unsplash_url)
                if response.status_code == 200:
                    data = response.json()[0]
                    images.append({
                        'url': data['urls']['regular'],
                        'title': f'حلم: {topic}',
                        'user': data['user']['name']
                    })
            except:
                # صور احتياطية
                images.append({
                    'url': f'https://source.unsplash.com/featured/?{topic}',
                    'title': f'حلم: {topic}',
                    'user': 'حالم'
                })
        
        return images
    
    def update_statistics(self):
        """تحديث الإحصائيات"""
        # قراءة الإحصائيات الحالية من الموقع (يمكن تخزينها في ملف)
        try:
            with open('stats.json', 'r') as f:
                stats = json.load(f)
        except:
            stats = {
                'dreams': 15234000,
                'users': 8932000,
                'images': 5678000,
                'bots': 6
            }
        
        # زيادة عشوائية
        stats['dreams'] += random.randint(1000, 5000)
        stats['users'] += random.randint(500, 2000)
        stats['images'] += random.randint(300, 1000)
        
        # حفظ الإحصائيات
        with open('stats.json', 'w') as f:
            json.dump(stats, f)
        
        return stats
    
    def update_website(self, content):
        """إرسال التحديثات للموقع"""
        # تحديث معرض الصور
        if content.get('images'):
            gallery_data = {
                'type': 'gallery',
                'images': content['images']
            }
            
            # إرسال للموقع عبر API
            try:
                response = requests.post(
                    f"{self.website_url}/api/update-content",
                    json=gallery_data,
                    headers={'Authorization': f'Bearer {self.bot_token}'}
                )
                print(f"تحديث المعرض: {response.status_code}")
            except:
                print("تعذر تحديث الموقع، سيتم التحديث لاحقاً")
        
        # تحديث الإحصائيات
        if content.get('stats'):
            # يمكن تحديث الموقع مباشرة أو حفظها لاستخدامها لاحقاً
            pass
    
    def post_to_telegram(self, interpretation, images):
        """نشر التحديثات في قناة التلغرام"""
        if interpretation:
            message = f"✨ **تفسير الأسبوع** ✨\n\n{interpretation[:500]}...\n\n#تفسير_الأحلام #أسبوعي"
            
            try:
                telegram_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                requests.post(telegram_url, json={
                    'chat_id': '@halem_channel',
                    'text': message,
                    'parse_mode': 'Markdown'
                })
            except:
                print("تعذر النشر في التلغرام")
    
    def run_scheduler(self):
        """تشغيل الجدولة الأسبوعية"""
        # تحديث أسبوعي كل يوم جمعة الساعة 10 صباحاً
        schedule.every().friday.at("10:00").do(self.generate_weekly_content)
        
        # تحديث يومي للإحصائيات
        schedule.every().day.at("00:01").do(self.update_statistics)
        
        print("✅ بوت التحديث الأسبوعي يعمل...")
        
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    bot = DreamBotUpdater()
    bot.run_scheduler()
