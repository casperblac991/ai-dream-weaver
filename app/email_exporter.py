"""
نظام استخراج الإيميلات وتنسيقها للحملات الإعلانية
(Email Exporter for Marketing Campaigns)
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import sqlite3

class EmailExporter:
    """أداة استخراج الإيميلات من قاعدة البيانات"""
    
    def __init__(self, db_path: str = "weaver.db"):
        self.db_path = db_path
        self.export_dir = Path("exports")
        self.export_dir.mkdir(exist_ok=True)
    
    def get_all_emails(self) -> List[Dict]:
        """استخراج جميع الإيميلات من قاعدة البيانات"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # استخراج الإيميلات من جدول المستخدمين
            cursor.execute("SELECT id, email, username, created_at FROM users WHERE email IS NOT NULL")
            users = [dict(row) for row in cursor.fetchall()]
            
            # استخراج الإيميلات من جدول المشتركين في النشرة البريدية
            cursor.execute("SELECT id, email, subscribed_at FROM newsletter_subscribers WHERE email IS NOT NULL")
            subscribers = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                "users": users,
                "subscribers": subscribers,
                "total": len(users) + len(subscribers)
            }
        except Exception as e:
            print(f"❌ خطأ في استخراج الإيميلات: {e}")
            return {"users": [], "subscribers": [], "total": 0}
    
    def export_to_csv(self, filename: str = None) -> str:
        """تصدير الإيميلات إلى ملف CSV"""
        if not filename:
            filename = f"emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = self.export_dir / filename
        
        try:
            emails_data = self.get_all_emails()
            
            # دمج جميع الإيميلات
            all_emails = []
            
            for user in emails_data["users"]:
                all_emails.append({
                    "email": user["email"],
                    "name": user["username"],
                    "type": "user",
                    "registered_date": user["created_at"]
                })
            
            for subscriber in emails_data["subscribers"]:
                all_emails.append({
                    "email": subscriber["email"],
                    "name": "مشترك",
                    "type": "subscriber",
                    "registered_date": subscriber["subscribed_at"]
                })
            
            # كتابة الملف
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["email", "name", "type", "registered_date"])
                writer.writeheader()
                writer.writerows(all_emails)
            
            print(f"✅ تم تصدير {len(all_emails)} إيميل إلى {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"❌ خطأ في تصدير CSV: {e}")
            return None
    
    def export_to_json(self, filename: str = None) -> str:
        """تصدير الإيميلات إلى ملف JSON"""
        if not filename:
            filename = f"emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.export_dir / filename
        
        try:
            emails_data = self.get_all_emails()
            
            # إعداد البيانات للتصدير
            export_data = {
                "export_date": datetime.now().isoformat(),
                "total_emails": emails_data["total"],
                "users": emails_data["users"],
                "subscribers": emails_data["subscribers"]
            }
            
            # كتابة الملف
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ تم تصدير {emails_data['total']} إيميل إلى {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"❌ خطأ في تصدير JSON: {e}")
            return None
    
    def export_for_facebook(self, filename: str = None) -> str:
        """تصدير الإيميلات بصيغة Facebook Pixel"""
        if not filename:
            filename = f"facebook_emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = self.export_dir / filename
        
        try:
            emails_data = self.get_all_emails()
            
            # جمع الإيميلات الفريدة
            unique_emails = set()
            for user in emails_data["users"]:
                unique_emails.add(user["email"].lower())
            for subscriber in emails_data["subscribers"]:
                unique_emails.add(subscriber["email"].lower())
            
            # كتابة الملف بصيغة Facebook
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Email"])
                for email in unique_emails:
                    writer.writerow([email])
            
            print(f"✅ تم تصدير {len(unique_emails)} إيميل لـ Facebook إلى {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"❌ خطأ في تصدير Facebook: {e}")
            return None
    
    def export_for_instagram(self, filename: str = None) -> str:
        """تصدير الإيميلات بصيغة Instagram Business"""
        # نفس صيغة Facebook
        return self.export_for_facebook(filename or f"instagram_emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    
    def export_for_google_ads(self, filename: str = None) -> str:
        """تصدير الإيميلات بصيغة Google Ads"""
        if not filename:
            filename = f"google_ads_emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = self.export_dir / filename
        
        try:
            emails_data = self.get_all_emails()
            
            # جمع الإيميلات الفريدة
            unique_emails = set()
            for user in emails_data["users"]:
                unique_emails.add(user["email"].lower())
            for subscriber in emails_data["subscribers"]:
                unique_emails.add(subscriber["email"].lower())
            
            # كتابة الملف بصيغة Google Ads
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Email"])
                for email in unique_emails:
                    writer.writerow([email])
            
            print(f"✅ تم تصدير {len(unique_emails)} إيميل لـ Google Ads إلى {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"❌ خطأ في تصدير Google Ads: {e}")
            return None
    
    def get_email_statistics(self) -> Dict:
        """الحصول على إحصائيات الإيميلات"""
        emails_data = self.get_all_emails()
        
        return {
            "total_emails": emails_data["total"],
            "total_users": len(emails_data["users"]),
            "total_subscribers": len(emails_data["subscribers"]),
            "export_date": datetime.now().isoformat(),
            "export_formats_available": [
                "CSV (عام)",
                "JSON (عام)",
                "Facebook Pixel",
                "Instagram Business",
                "Google Ads"
            ]
        }
    
    def export_all_formats(self) -> Dict[str, str]:
        """تصدير الإيميلات بجميع الصيغ"""
        exports = {}
        
        print("🚀 جاري تصدير الإيميلات بجميع الصيغ...")
        
        # CSV
        csv_path = self.export_to_csv()
        if csv_path:
            exports["csv"] = csv_path
        
        # JSON
        json_path = self.export_to_json()
        if json_path:
            exports["json"] = json_path
        
        # Facebook
        fb_path = self.export_for_facebook()
        if fb_path:
            exports["facebook"] = fb_path
        
        # Google Ads
        ga_path = self.export_for_google_ads()
        if ga_path:
            exports["google_ads"] = ga_path
        
        print(f"\n✅ تم تصدير الإيميلات بنجاح!")
        print(f"📁 المسار: {self.export_dir}")
        
        return exports

# دالة للاستخدام من خارج الملف
def export_emails_for_campaigns():
    """تصدير الإيميلات للحملات الإعلانية"""
    exporter = EmailExporter()
    
    # الحصول على الإحصائيات
    stats = exporter.get_email_statistics()
    print("\n📊 إحصائيات الإيميلات:")
    print(f"   إجمالي الإيميلات: {stats['total_emails']}")
    print(f"   المستخدمون: {stats['total_users']}")
    print(f"   المشتركون: {stats['total_subscribers']}")
    
    # تصدير بجميع الصيغ
    exports = exporter.export_all_formats()
    
    return exports

if __name__ == "__main__":
    export_emails_for_campaigns()
