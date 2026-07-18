"""
البوت الموحد - Single Unified Bot
بوت واحد فقط يدير كل شيء بدون تعارضات
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class SingleUnifiedBot:
    """بوت موحد واحد يدير كل عمليات المنصة"""
    
    def __init__(self):
        self.db_path = "weaver.db"
        self.blog_dir = Path("blog_posts")
        self.exports_dir = Path("exports")
        self.blog_dir.mkdir(exist_ok=True)
        self.exports_dir.mkdir(exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """إنشاء جداول قاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول المستخدمين
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                password TEXT,
                language TEXT DEFAULT 'ar',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول المشتركين
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS newsletter_subscribers (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE,
                language TEXT DEFAULT 'ar',
                subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول المقالات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blog_posts (
                id INTEGER PRIMARY KEY,
                title_ar TEXT,
                title_en TEXT,
                content_ar TEXT,
                content_en TEXT,
                post_id TEXT UNIQUE,
                language TEXT DEFAULT 'ar_en',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("✅ تم تهيئة قاعدة البيانات")
    
    def create_blog_post(self, title_ar, title_en, content_ar, content_en):
        """إنشاء مقالة جديدة بلغتين"""
        try:
            logger.info(f"📝 إنشاء مقالة: {title_ar}")
            
            post_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO blog_posts (title_ar, title_en, content_ar, content_en, post_id)
                VALUES (?, ?, ?, ?, ?)
            """, (title_ar, title_en, content_ar, content_en, post_id))
            conn.commit()
            conn.close()
            
            logger.info(f"✅ تم إنشاء المقالة: {post_id}")
            return post_id
        except Exception as e:
            logger.error(f"❌ خطأ: {str(e)}")
            return None
    
    def get_all_blog_posts(self):
        """جلب جميع المقالات"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM blog_posts ORDER BY created_at DESC")
            posts = cursor.fetchall()
            conn.close()
            return posts
        except Exception as e:
            logger.error(f"❌ خطأ: {str(e)}")
            return []
    
    def export_emails(self):
        """استخراج الإيميلات للحملات"""
        try:
            logger.info("📧 استخراج الإيميلات...")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # جلب الإيميلات
            cursor.execute("SELECT email FROM users")
            user_emails = [row[0] for row in cursor.fetchall()]
            
            cursor.execute("SELECT email FROM newsletter_subscribers")
            subscriber_emails = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            all_emails = user_emails + subscriber_emails
            
            if not all_emails:
                logger.warning("⚠️ لا توجد إيميلات")
                return {}
            
            # حفظ الإيميلات
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # CSV
            csv_file = self.exports_dir / f"emails_{timestamp}.csv"
            with open(csv_file, 'w', encoding='utf-8') as f:
                f.write("البريد الإلكتروني\n")
                for email in all_emails:
                    f.write(f"{email}\n")
            
            # Facebook
            fb_file = self.exports_dir / f"facebook_{timestamp}.csv"
            with open(fb_file, 'w', encoding='utf-8') as f:
                for email in all_emails:
                    f.write(f"{email}\n")
            
            # Google Ads
            ga_file = self.exports_dir / f"google_ads_{timestamp}.csv"
            with open(ga_file, 'w', encoding='utf-8') as f:
                for email in all_emails:
                    f.write(f"{email}\n")
            
            logger.info(f"✅ تم استخراج {len(all_emails)} إيميل")
            return {
                "csv": str(csv_file),
                "facebook": str(fb_file),
                "google_ads": str(ga_file),
                "count": len(all_emails)
            }
        except Exception as e:
            logger.error(f"❌ خطأ: {str(e)}")
            return {}
    
    def get_statistics(self):
        """الحصول على إحصائيات المنصة"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users")
            users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM newsletter_subscribers")
            subscribers = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM blog_posts")
            posts = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "المستخدمون": users,
                "المشتركون": subscribers,
                "المقالات": posts,
                "إجمالي الإيميلات": users + subscribers
            }
        except Exception as e:
            logger.error(f"❌ خطأ: {str(e)}")
            return {}
    
    def run_daily_tasks(self):
        """تشغيل المهام اليومية"""
        logger.info("\n" + "="*50)
        logger.info("🚀 بدء المهام اليومية")
        logger.info("="*50)
        
        # 1. إنشاء مقالة
        self.create_blog_post(
            "تفسير الأحلام",
            "Dream Interpretation",
            "محتوى عن تفسير الأحلام بالعربية",
            "Content about dream interpretation in English"
        )
        
        # 2. استخراج الإيميلات
        emails = self.export_emails()
        
        # 3. الإحصائيات
        stats = self.get_statistics()
        
        logger.info("\n📊 الإحصائيات:")
        for key, value in stats.items():
            logger.info(f"   {key}: {value}")
        
        logger.info("\n" + "="*50)
        logger.info("✅ اكتملت المهام اليومية")
        logger.info("="*50 + "\n")
        
        return {
            "status": "نجح",
            "إحصائيات": stats,
            "إيميلات": emails.get("count", 0)
        }


# تشغيل البوت
if __name__ == "__main__":
    bot = SingleUnifiedBot()
    bot.run_daily_tasks()
