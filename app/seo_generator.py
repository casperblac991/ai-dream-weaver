#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام SEO المتقدم - توليد صفحات الرموز تلقائياً
"""

import sqlite3
from datetime import datetime
from app.ai import interpret_dream, generate_blog_article

# قائمة الرموز الشهيرة في الأحلام
DREAM_SYMBOLS = {
    "الماء": {"searches": 15000, "difficulty": "easy"},
    "الثعبان": {"searches": 12000, "difficulty": "medium"},
    "الطيران": {"searches": 18000, "difficulty": "easy"},
    "الميت": {"searches": 25000, "difficulty": "hard"},
    "الذهب": {"searches": 8000, "difficulty": "easy"},
    "الحريق": {"searches": 9500, "difficulty": "medium"},
    "السقوط": {"searches": 11000, "difficulty": "easy"},
    "الحيوانات": {"searches": 7000, "difficulty": "medium"},
    "المنزل": {"searches": 6500, "difficulty": "easy"},
    "السفر": {"searches": 5500, "difficulty": "easy"},
    "الأسنان": {"searches": 14000, "difficulty": "medium"},
    "الدم": {"searches": 6000, "difficulty": "hard"},
    "الملابس": {"searches": 3500, "difficulty": "easy"},
    "الطعام": {"searches": 4200, "difficulty": "easy"},
    "الحرب": {"searches": 2800, "difficulty": "medium"},
    "الزواج": {"searches": 9800, "difficulty": "medium"},
    "الولادة": {"searches": 7200, "difficulty": "medium"},
    "الموت": {"searches": 13000, "difficulty": "hard"},
    "الجنة": {"searches": 5000, "difficulty": "hard"},
    "الجهنم": {"searches": 4500, "difficulty": "hard"},
}

def create_seo_table():
    """إنشاء جدول صفحات SEO"""
    conn = sqlite3.connect("app/weaver.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seo_pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            content TEXT,
            keywords TEXT,
            meta_description TEXT,
            views INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ جدول صفحات SEO جاهز")

def generate_seo_page(symbol: str):
    """توليد صفحة SEO لرمز معين"""
    slug = symbol.replace(" ", "-").lower()
    title = f"تفسير حلم {symbol} | Weaver"
    meta_description = f"اكتشف تفسير حلم {symbol} بالتفصيل حسب ابن سيرين والتحليل النفسي الحديث."
    keywords = f"تفسير حلم {symbol}, {symbol} في المنام, رؤية {symbol}"
    
    # توليد محتوى SEO غني
    content = f"""
    # تفسير حلم {symbol}
    
    ## مقدمة
    رؤية {symbol} في المنام من الرؤى التي تثير فضول الكثيرين. في هذا المقال، سنستعرض تفسيرات متعددة لهذا الرمز من منظور إسلامي وحديث.
    
    ## التفسير الإسلامي
    حسب تفسير ابن سيرين، رؤية {symbol} تشير إلى...
    
    ## التحليل النفسي
    من وجهة نظر فرويد وعلماء النفس الحديثين، يرمز {symbol} إلى...
    
    ## الحالات المختلفة
    - رؤية {symbol} بحالة جيدة: تشير إلى...
    - رؤية {symbol} بحالة سيئة: تعني...
    - التفاعل مع {symbol}: يدل على...
    
    ## الخلاصة
    تفسير رؤية {symbol} يعتمد على السياق والحالة الشخصية للرائي.
    """
    
    return {
        "symbol": symbol,
        "slug": slug,
        "title": title,
        "meta_description": meta_description,
        "keywords": keywords,
        "content": content
    }

def save_seo_page(page_data: dict):
    """حفظ صفحة SEO في قاعدة البيانات"""
    conn = sqlite3.connect("app/weaver.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO seo_pages 
            (symbol, slug, title, description, content, keywords, meta_description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            page_data["symbol"],
            page_data["slug"],
            page_data["title"],
            page_data.get("description", ""),
            page_data["content"],
            page_data["keywords"],
            page_data["meta_description"]
        ))
        conn.commit()
        return {"success": True, "symbol": page_data["symbol"]}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()

def generate_all_seo_pages():
    """توليد جميع صفحات SEO للرموز الشهيرة"""
    created = 0
    for symbol in DREAM_SYMBOLS.keys():
        page_data = generate_seo_page(symbol)
        result = save_seo_page(page_data)
        if result["success"]:
            created += 1
    
    return {
        "total_symbols": len(DREAM_SYMBOLS),
        "pages_created": created,
        "status": "completed"
    }

def get_seo_page(slug: str):
    """الحصول على صفحة SEO"""
    conn = sqlite3.connect("app/weaver.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT symbol, title, description, content, keywords, meta_description, views
        FROM seo_pages WHERE slug = ?
    """, (slug,))
    
    result = cursor.fetchone()
    
    if result:
        # تحديث عدد المشاهدات
        cursor.execute("UPDATE seo_pages SET views = views + 1 WHERE slug = ?", (slug,))
        conn.commit()
        
        return {
            "symbol": result[0],
            "title": result[1],
            "description": result[2],
            "content": result[3],
            "keywords": result[4],
            "meta_description": result[5],
            "views": result[6] + 1
        }
    
    conn.close()
    return None

def get_seo_stats():
    """الحصول على إحصائيات SEO"""
    conn = sqlite3.connect("app/weaver.db")
    cursor = conn.cursor()
    
    # عدد الصفحات
    cursor.execute("SELECT COUNT(*) FROM seo_pages")
    total_pages = cursor.fetchone()[0]
    
    # إجمالي المشاهدات
    cursor.execute("SELECT SUM(views) FROM seo_pages")
    total_views = cursor.fetchone()[0] or 0
    
    # أكثر الصفحات مشاهدة
    cursor.execute("""
        SELECT symbol, views FROM seo_pages 
        ORDER BY views DESC LIMIT 10
    """)
    top_pages = [{"symbol": row[0], "views": row[1]} for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "total_pages": total_pages,
        "total_views": total_views,
        "average_views_per_page": total_views / total_pages if total_pages > 0 else 0,
        "top_pages": top_pages
    }

def generate_sitemap():
    """توليد Sitemap لمحركات البحث"""
    conn = sqlite3.connect("app/weaver.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT slug, updated_at FROM seo_pages")
    pages = cursor.fetchall()
    conn.close()
    
    sitemap = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""
    
    for slug, updated_at in pages:
        sitemap += f"""
    <url>
        <loc>https://aidreamweaver.store/dream/{slug}</loc>
        <lastmod>{updated_at}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
"""
    
    sitemap += "</urlset>"
    return sitemap

if __name__ == "__main__":
    create_seo_table()
    result = generate_all_seo_pages()
    print(f"✅ تم إنشاء {result['pages_created']} صفحة SEO")
