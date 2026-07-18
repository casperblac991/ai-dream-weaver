"""
نظام إدارة المدونة ثنائية اللغة (عربي + إنجليزي)
يوفر هيكل موحد لجميع المقالات
"""

from datetime import datetime
from pathlib import Path
import json
from typing import Dict, List

class BlogPost:
    """نموذج موحد للمقالات ثنائية اللغة"""
    
    def __init__(self, slug: str, title_ar: str, title_en: str, 
                 content_ar: str, content_en: str, category: str = "تفسير أحلام"):
        self.slug = slug
        self.title_ar = title_ar
        self.title_en = title_en
        self.content_ar = content_ar
        self.content_en = content_en
        self.category = category
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.views = 0
        self.likes = 0
    
    def to_dict(self) -> Dict:
        """تحويل المقالة إلى قاموس"""
        return {
            "slug": self.slug,
            "title_ar": self.title_ar,
            "title_en": self.title_en,
            "content_ar": self.content_ar,
            "content_en": self.content_en,
            "category": self.category,
            "date": self.date,
            "views": self.views,
            "likes": self.likes
        }
    
    def to_html_ar(self) -> str:
        """تحويل المقالة إلى HTML بالعربية"""
        return f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title_ar} - Weaver</title>
    <style>
        body {{
            background: linear-gradient(135deg, #1a0033 0%, #2d0052 100%);
            color: #fff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 40px 20px;
            line-height: 1.8;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 40px;
        }}
        h1 {{
            color: #a78bfa;
            font-size: 32px;
            margin-bottom: 20px;
        }}
        .meta {{
            color: rgba(255, 255, 255, 0.6);
            font-size: 14px;
            margin-bottom: 30px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 20px;
        }}
        .content {{
            font-size: 16px;
            color: rgba(255, 255, 255, 0.9);
            line-height: 1.8;
        }}
        .content p {{
            margin-bottom: 20px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
            color: rgba(255, 255, 255, 0.5);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{self.title_ar}</h1>
        <div class="meta">
            <span>📅 {self.date}</span> | 
            <span>📂 {self.category}</span> |
            <span>👁️ {self.views} مشاهدة</span>
        </div>
        <div class="content">
            {self.content_ar}
        </div>
        <div class="footer">
            <p>🌙 Weaver - منصة تفسير الأحلام بالذكاء الاصطناعي</p>
            <p><a href="/blog" style="color: #a78bfa;">← العودة للمدونة</a></p>
        </div>
    </div>
</body>
</html>
"""
    
    def to_html_en(self) -> str:
        """تحويل المقالة إلى HTML بالإنجليزية"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title_en} - Weaver</title>
    <style>
        body {{
            background: linear-gradient(135deg, #1a0033 0%, #2d0052 100%);
            color: #fff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 40px 20px;
            line-height: 1.8;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 40px;
        }}
        h1 {{
            color: #a78bfa;
            font-size: 32px;
            margin-bottom: 20px;
        }}
        .meta {{
            color: rgba(255, 255, 255, 0.6);
            font-size: 14px;
            margin-bottom: 30px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 20px;
        }}
        .content {{
            font-size: 16px;
            color: rgba(255, 255, 255, 0.9);
            line-height: 1.8;
        }}
        .content p {{
            margin-bottom: 20px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
            color: rgba(255, 255, 255, 0.5);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{self.title_en}</h1>
        <div class="meta">
            <span>📅 {self.date}</span> | 
            <span>📂 {self.category}</span> |
            <span>👁️ {self.views} views</span>
        </div>
        <div class="content">
            {self.content_en}
        </div>
        <div class="footer">
            <p>🌙 Weaver - AI-Powered Dream Interpretation Platform</p>
            <p><a href="/blog" style="color: #a78bfa;">← Back to Blog</a></p>
        </div>
    </div>
</body>
</html>
"""

class BlogManager:
    """مدير المدونة - يدير حفظ وتحميل المقالات"""
    
    def __init__(self, blog_dir: str = "blog"):
        self.blog_dir = Path(blog_dir)
        self.blog_dir.mkdir(exist_ok=True)
        self.metadata_file = self.blog_dir / "metadata.json"
    
    def save_post(self, post: BlogPost) -> bool:
        """حفظ مقالة جديدة"""
        try:
            # حفظ ملف HTML بالعربية
            ar_file = self.blog_dir / f"{post.slug}_ar.html"
            with open(ar_file, 'w', encoding='utf-8') as f:
                f.write(post.to_html_ar())
            
            # حفظ ملف HTML بالإنجليزية
            en_file = self.blog_dir / f"{post.slug}_en.html"
            with open(en_file, 'w', encoding='utf-8') as f:
                f.write(post.to_html_en())
            
            # حفظ البيانات الوصفية
            self._save_metadata(post)
            
            return True
        except Exception as e:
            print(f"خطأ في حفظ المقالة: {e}")
            return False
    
    def _save_metadata(self, post: BlogPost):
        """حفظ البيانات الوصفية للمقالة"""
        metadata = {}
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        
        metadata[post.slug] = post.to_dict()
        
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def get_all_posts(self) -> List[Dict]:
        """الحصول على جميع المقالات"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return list(json.load(f).values())
        return []
    
    def get_post(self, slug: str, lang: str = "ar") -> str:
        """الحصول على مقالة معينة"""
        file_name = f"{slug}_{lang}.html"
        file_path = self.blog_dir / file_name
        
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None
