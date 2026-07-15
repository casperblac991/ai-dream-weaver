#!/usr/bin/env python3
"""
🤖 Weaver AI Manager - الوكيل الذكي لإدارة المنصة والمستودع
=========================================================
يتولى:
- توليد المقالات والمحتوى
- إدارة منصات التواصل الاجتماعي
- دعم العملاء
- توليد التقارير
- إدارة المستودع
"""

import os
import sys
import json
import re
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import requests
from groq import Groq

# ============ الإعدادات ============
class Config:
    """إعدادات المنصة"""
    SITE_URL = "https://aidreamweaver.store"
    BLOG_DIR = "blog"
    
    # البحث عن المفاتيح من مصادر مختلفة
    @property
    def TELEGRAM_BOT_TOKEN(self):
        return os.environ.get("TELEGRAM_TOKEN", "") or os.environ.get("TELEGRAM_BOT_TOKEN", "")
    
    @property
    def TELEGRAM_CHANNEL_ID(self):
        return os.environ.get("TELEGRAM_CHANNEL_ID", "") or os.environ.get("_CHANNEL_ID", "")
    
    @property
    def GROQ_API_KEY(self):
        return os.environ.get("GROQ_API_KEY", "") or os.environ.get("GROQ_KEY", "") or os.environ.get("API_KEY", "")
    
    @property
    def OPENAI_API_KEY(self):
        return os.environ.get("OPENAI_API_KEY", "") or os.environ.get("OPENAI_KEY", "")

config = Config()


# ============ ذكاء اصطناعي ============
class WeaverAI:
    """محرك الذكاء الاصطناعي للمنصة"""
    
    def __init__(self):
        self.client = None
        key = config.GROQ_API_KEY
        if key:
            self.client = Groq(api_key=key)
            print(f"✅ Grover AI مُفعّل")
    
    async def chat(self, message: str, context: str = "") -> str:
        """الدردشة مع الذكاء الاصطناعي"""
        if not self.client:
            return "⚠️ الذكاء الاصطناعي غير متوفر - يرجى إعداد GROQ_API_KEY"
        
        system_prompt = f"""أنت مساعد ذكي متخصص في تفسير الأحلام وتحليلها.
المنصة: {config.SITE_URL}
السياق: {context}

أجب بوضوح وإيجاز."""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ خطأ: {str(e)}"
    
    async def generate_blog(self, topic: str, language: str = "ar") -> Dict[str, str]:
        """توليد مقال جديد"""
        if not self.client:
            return {"error": "GROQ_API_KEY غير موجود"}
        
        if language == "ar":
            prompt = f"""اكتب مقالاً كاملاً عن: {topic}
المقال должен يكون:
- 1500-2500 كلمة
- غني بالمعلومات
- يحتوي على روابط للمقالات ذات الصلة
- عنوان جذاب
- مقدمة وخلاصة
- نقاشات من الحضارات المختلفة (مصر، يونان، الإسلام)"""
        else:
            prompt = f"""Write a complete article about: {topic}
The article should be:
- 1500-2500 words
- Informative and engaging
- Include relevant links
- Compelling title, intro and conclusion
- Discuss different civilizations (Egypt, Greece, Islam)"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a professional content writer for a dream interpretation platform."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=4000
            )
            content = response.choices[0].message.content
            
            # استخراج العنوان
            title_match = re.search(r'[###](.+?)\n', content)
            title = title_match.group(1).strip() if title_match else topic
            
            return {
                "title": title,
                "content": content,
                "topic": topic,
                "language": language
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def interpret_dream(self, dream: str, user_id: int = 0) -> str:
        """تفسير الحلم"""
        if not self.client:
            return "⚠️ غير متوفر - يرجى إعداد GROQ_API_KEY"
        
        prompt = f"""Interpret this dream:
{dream}

Provide:
1. المعنى العام
2. التفسير من منظور مختلف civilizations:
   - مصر القديمة
   - يونان القديمة  
   - التفسير الإسلامي
   - التحليل النفسي (فرويد/يونج)
3. نصائح للحالم
4. روابط للمقالات ذات الصلة

Use Markdown وروابط لمنصة aidreamweaver.store"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are expert dream interpreter with knowledge of ancient civilizations, Islamic interpretation, and psychology."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ خطأ في التفسير: {str(e)}"


# ============ إدارة المحتوى ============
class ContentManager:
    """مدير المحتوى والمنشورات"""
    
    def __init__(self, blog_dir: str = config.BLOG_DIR):
        self.blog_dir = blog_dir
        os.makedirs(blog_dir, exist_ok=True)
    
    def save_article(self, article: Dict, filename: Optional[str] = None) -> str:
        """حفظ المقال"""
        if filename is None:
            # إنشاء اسم الملف من العنوان
            title = article.get("title", "article")
            slug = re.sub(r'[^\w\u0600-\u06FF]', '-', title.lower())
            slug = re.sub(r'-+', '-', slug).strip('-')
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"{date_str}-{slug}.html"
        
        filepath = os.path.join(self.blog_dir, filename)
        
        # إنشاء محتوى HTML
        html = self._create_html(article)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return filepath
    
    def _create_html(self, article: Dict) -> str:
        """إنشاء HTML للمقال"""
        title = article.get("title", "مقال جديد")
        content = article.get("content", "")
        
        # تحويل Markdown إلى HTML (تبسيط)
        content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
        content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
        content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
        content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
        content = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', content)
        content = re.sub(r'\n\n+', '</p><p>', content)
        
        lang = article.get("language", "ar")
        dir_attr = 'dir="rtl"' if lang == "ar" else 'dir="ltr"'
        
        html = f"""<!DOCTYPE html>
<html {dir_attr}>
<head>
    <meta charset="UTF-8">
    <title>{title} | Weaver</title>
    <meta name="description" content="{title}">
    <link rel="canonical" href="{config.SITE_URL}/{article.get('filename', 'article.html')}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{title}">
    <meta property="og:type" content="article">
</head>
<body>
    <article>
        <header>
            <h1>{title}</h1>
            <time>{datetime.now().strftime('%Y-%m-%d')}</time>
        </header>
        <div class="content">
            <p>{content}</p>
        </div>
        <footer>
            <a href="{config.SITE_URL}">الرئيسية</a> | 
            <a href="{config.SITE_URL}/blog.html">المدونة</a>
        </footer>
    </article>
</body>
</html>"""
        return html
    
    def get_blog_stats(self) -> Dict:
        """إحصائيات المدونة"""
        if not os.path.exists(self.blog_dir):
            return {"total_articles": 0}
        
        files = [f for f in os.listdir(self.blog_dir) if f.endswith('.html')]
        
        stats = {
            "total_articles": len(files),
            "last_update": datetime.now().isoformat()
        }
        
        return stats


# ============ إدارة وسائل التواصل ============
class SocialMediaManager:
    """مدير منصات التواصل الاجتماعي"""
    
    def __init__(self):
        self.telegram_token = config.TELEGRAM_BOT_TOKEN
        self.channel_id = config.TELEGRAM_CHANNEL_ID
    
    async def post_to_telegram(self, message: str, photo: Optional[str] = None) -> Dict:
        """النشر على تيليجرام"""
        if not self.telegram_token:
            return {"success": False, "error": "TELEGRAM_TOKEN غير موجود"}
        
        url = f"https://api.telegram.org/bot{self.telegram_token}"
        
        if photo:
            # نشر صورة مع نص
            files = {'photo': requests.get(photo).content} if photo.startswith('http') else None
            data = {
                'chat_id': self.channel_id,
                'caption': message[:1024],
                'parse_mode': 'HTML'
            }
            response = requests.post(f"{url}/sendPhoto", data=data, files=files)
        else:
            # نشر نص فقط
            data = {
                'chat_id': self.channel_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }
            response = requests.post(f"{url}/sendMessage", data=data)
        
        result = response.json()
        return {"success": result.get("ok", False), "response": result}
    
    async def broadcast(self, message: str, users: List[int]) -> Dict:
        """إرسال لجميع المستخدمين"""
        if not self.telegram_token:
            return {"success": False, "error": "TELEGRAM_TOKEN غير موجود"}
        
        url = f"https://api.telegram.org/bot{self.telegram_token}"
        results = []
        
        for user_id in users:
            try:
                data = {
                    'chat_id': user_id,
                    'text': message,
                    'parse_mode': 'HTML'
                }
                r = requests.post(f"{url}/sendMessage", data=data)
                results.append({"user": user_id, "success": r.json().get("ok", False)})
            except Exception as e:
                results.append({"user": user_id, "error": str(e)})
        
        return {"success": True, "results": results}
    
    def create_campaign_post(self, topic: str, article: Dict) -> str:
        """إنشاء منشور للحملة"""
        title = article.get("title", "")
        link = f"{config.SITE_URL}/{article.get('filename', '')}"
        
        message = f"""🔮 {title}

{topic}

👉 {link}

#الأحلام #التفسير #حضارات"""

        return message


# ============ دعم العملاء ============
class CustomerSupport:
    """نظام دعم العملاء"""
    
    def __init__(self):
        self.ai = WeaverAI()
        # تخزين مؤقت للمستخدمين
        self.sessions: Dict[int, Dict] = {}
    
    async def handle_message(self, user_id: int, message: str) -> str:
        """معالجة رسالة العميل"""
        # الحصول على أو إنشاء جلسة
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                "messages": [],
                "last_dream": None
            }
        
        session = self.sessions[user_id]
        
        # التحقق إذا كان المستخدم يسأل عن حلم
        is_dream = any(word in message.lower() for word in 
                     ["حلم", "dream", "رأيت", "saw", "في المنام"])
        
        if is_dream:
            session["last_dream"] = message
            response = await self.ai.interpret_dream(message, user_id)
            # إضافة روابط مفيدة
            response += f"""

🤖 جرب حلمك المجاني: {config.SITE_URL}/app/analyze"""
            return response
        
        # إجابة على سؤال عام
        context = f"上次梦境: {session.get('last_dream', 'None')}"
        response = await self.ai.chat(message, context)
        
        return response
    
    def end_session(self, user_id: int):
        """إنهاء الجلسة"""
        if user_id in self.sessions:
            del self.sessions[user_id]


# ============ توليد التقارير ============
class ReportGenerator:
    """مولد التقارير"""
    
    def __init__(self):
        self.ai = WeaverAI()
    
    async def generate_daily_report(self) -> str:
        """توليد التقرير اليومي"""
        stats = self._get_stats()
        
        report = f"""# 📊 تقرير منصة Weaver - {datetime.now().strftime('%Y-%m-%d')}

## إحصائيات اليوم
- المقالات: {stats.get('articles', 0)}
- المستخدمين النشطين: {stats.get('users', 0)}
- أحلام مفسرة: {stats.get('dreams', 0)}

## أهم المقالات
{self._get_top_articles()}

---
🤖 Generated by Weaver AI"""
        
        return report
    
    def _get_stats(self) -> Dict:
        """جلب الإحصائيات - يمكن توسيعها"""
        return {
            "articles": 0,
            "users": 0,
            "dreams": 0
        }
    
    def _get_top_articles(self) -> str:
        """أ热门 المقالات"""
        return "- لا توجد بيانات بعد"


# ============ المنسق الرئيسي ============
class WeaverManager:
    """المنسق الرئيسي لجميع الوظائف"""
    
    def __init__(self):
        self.ai = WeaverAI()
        self.content = ContentManager()
        self.social = SocialMediaManager()
        self.support = CustomerSupport()
        self.reports = ReportGenerator()
    
    async def run_daily_automation(self):
        # استدعاء المنسق المركزي للمزامنة
        import subprocess
        subprocess.Popen(["python3", "sync_all.py"])
        """تشغيل الأتمتة اليومية"""
        print("🤖 بدء الأتمتة اليومية...")
        
        # 1. توليد مقال جديد
        topic = "رموز الأحلام في الحضارات المختلفة"
        article = await self.ai.generate_blog(topic)
        
        if "error" not in article:
            # حفظ المقال
            filepath = self.content.save_article(article)
            print(f"✅ تم حفظ المقال: {filepath}")
            
            # 2. النشر على تيليجرام
            post = self.social.create_campaign_post(topic, article)
            result = await self.social.post_to_telegram(post)
            print(f"📱 نتيجة النشر: {result}")
        
        # 3. توليد تقرير
        report = await self.reports.generate_daily_report()
        print(f"📊 التقرير: {report[:200]}...")
        
        return "✅ أكملت الأتمتة بنجاح"
    
    async def handle_telegram_update(self, update: Dict) -> str:
        """معالجة تحديث تيليجرام"""
        message = update.get("message", {})
        text = message.get("text", "")
        user_id = message.get("from", {}).get("id", 0)
        
        if not text:
            return ""
        
        # التحقق من الأوامر
        if text.startswith("/start"):
            return f"""🔮 أهلاً بك في Weaver!

اكتب حلمك وسأفسره لك...
أو استخدم /help للمساعدة"""

        elif text.startswith("/help"):
            return """📚 الأوامر:
/start - بدء جديد
/help - المساعدة
/stats - الإحصائيات
/analyze <حلم> - تحليل حلم"""

        elif text.startswith("/stats"):
            stats = self.content.get_blog_stats()
            return f"""📊 الإحصائيات:
- المقالات: {stats['total_articles']}"""

        elif text.startswith("/analyze "):
            dream = text[10:]  # استخراج الحلم
            return await self.ai.interpret_dream(dream, user_id)
        
        # معالجة رسالة عادية
        return await self.support.handle_message(user_id, text)


# ============ نقطة الدخول ============
async def main():
    """النقطة الرئيسية"""
    import argparse
    
    parser = argparse.ArgumentParser(description="🤖 Weaver AI Manager")
    parser.add_argument("--daily", action="store_true", help="تشغيل الأتمتة اليومية")
    parser.add_argument("--chat", type=str, help="دردشة مع الذكاء الاصطناعي")
    parser.add_argument("--interpret", type=str, help="تفسير حلم")
    parser.add_argument("--generate-blog", type=str, help="توليد مقال")
    parser.add_argument("--post", type=str, help="نشر على تيليجرام")
    parser.add_argument("--report", action="store_true", help="توليد تقرير")
    
    args = parser.parse_args()
    
    manager = WeaverManager()
    
    if args.daily:
        print(await manager.run_daily_automation())
    
    elif args.chat:
        result = await manager.ai.chat(args.chat)
        print(result)
    
    elif args.interpret:
        result = await manager.ai.interpret_dream(args.interpret)
        print(result)
    
    elif args.generate_blog:
        result = await manager.ai.generate_blog(args.generate_blog)
        if "error" not in result:
            path = manager.content.save_article(result)
            print(f"✅ تم حفظ: {path}")
        else:
            print(f"❌ خطأ: {result['error']}")
    
    elif args.post:
        result = await manager.social.post_to_telegram(args.post)
        print(f"📱 {result}")
    
    elif args.report:
        result = await manager.reports.generate_daily_report()
        print(result)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())