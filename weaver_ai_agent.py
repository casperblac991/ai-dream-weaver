#!/usr/bin/env python3
"""
🤖 Weaver AI Agent - الوكيل الشامل للأتمتة بالذكاء الاصطناعي
=====================================================
يتولى:
1. توليد المقالات والمحتوى (باستخدام NVIDIA NIM)
2. النشر على منصات التواصل الاجتماعي
3. دعم العملاء (ردود ذكية)
4. توليد التقارير
5. إصلاح المشاكل
6. إدارة المستودع

الاتصال: localhost:8082 (Free Claude Code Proxy)
"""

import os
import sys
import json
import re
import asyncio
import requests
from datetime import datetime
from typing import Optional, Dict, List, Any

# ============================================
# ⚙️ الإعدادات
# ============================================
class Config:
    """إعدادات المنصة"""
    SITE_URL = "https://aidreamweaver.store"
    BLOG_DIR = "blog"
    
    # Free Claude Code Proxy
    PROXY_URL = os.environ.get("PROXY_URL", "http://localhost:8082")
    PROXY_AUTH = os.environ.get("PROXY_AUTH", "freecc")
    
    # مفاتيح الخارجية
    @property
    def TELEGRAM_TOKEN(self):
        return os.environ.get("TELEGRAM_TOKEN", "") or os.environ.get("TELEGRAM_BOT_TOKEN", "")
    
    @property
    def TELEGRAM_CHANNEL(self):
        return os.environ.get("TELEGRAM_CHANNEL_ID", "") or os.environ.get("CHANNEL", "")
    
    @property
    def DISCORD_WEBHOOK(self):
        return os.environ.get("DISCORD_WEBHOOK", "") or os.environ.get("DISCORD_URL", "")

config = Config()

# ============================================
# 🧠 محرك الذكاء الاصطناعي (NVIDIA NIM)
# ============================================
class NIMClient:
    """عميل NVIDIA NIM عبر Free Claude Code Proxy"""
    
    def __init__(self):
        self.url = config.PROXY_URL
        self.auth = config.PROXY_AUTH
        self.model = "claude-3-5-sonnet-20241022"
        print(f"✅ NIM Client مُفعّل: {self.url}")
    
    def _call(self, prompt: str, system: str = "", max_tokens: int = 2000) -> str:
        """إرسال طلب للذكاء الاصطناعي"""
        headers = {
            "Authorization": f"Bearer {self.auth}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system:
            messages.append({"role": "user", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{self.url}/v1/messages",
                headers=headers,
                json=data,
                timeout=120
            )
            
            if response.status_code == 200:
                # استخراج النص من SSE
                text = ""
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            try:
                                d = json.loads(line[6:])
                                if d.get("type") == "content_block_delta":
                                    delta = d.get("delta", {})
                                    if delta.get("type") == "text_delta":
                                        text += delta.get("text", "")
                            except:
                                pass
                return text
            else:
                return f"❌ خطأ: {response.status_code} - {response.text[:200]}"
        except Exception as e:
            return f"❌ استثناء: {str(e)}"
    
    def chat(self, message: str) -> str:
        """دردشة عادية"""
        system = """أنت مساعد ذكي متخصص في تفسير الأحلام وتحليلها.
المنصة: aidreamweaver.store
أجب بوضوح وإيجاز بالعربية."""
        return self._call(message, system)
    
    def generate_article(self, topic: str) -> Dict[str, str]:
        """توليد مقال جديد"""
        prompt = f"""اكتب مقالاً كاملاً ومفصلاً عن: {topic}

المقال يجب أن يكون:
- 1500-2500 كلمة
- غني بالمعلومات التاريخية
- يحتوي على أمثلة من مختلف الحضارات (مصر القديمة، يونان،罗马، الإسلام)
- منظم بعناوين فرعية
- له مقدمة وخلاصة
- يحتوي على روابط للمقالات ذات الصلة على المنصة

أستخدم اللغة العربية الفصحى."""

        content = self._call(prompt, max_tokens=4000)
        
        # استخراج العنوان
        title = topic
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 5:
                title = line
                break
        
        return {
            "title": title,
            "content": content,
            "topic": topic,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
    
    def interpret_dream(self, dream: str) -> str:
        """تفسير الحلم"""
        prompt = f"""فسر هذا الحلم: {dream}

قدم:
1. المعنى العام للت Dreams
2. التفسير من منظور الحضارات المختلفة:
   - مصر القديمة
   - اليونان القديمة
   - التفسير الإسلامي
   - التحليل النفسي (فرويد/يونج)
3. نصائح للحالم
4. روابط للمقالات ذات الصلة على aidreamweaver.store

أجب بالعربية."""

        return self._call(prompt, max_tokens=3000)
    
    def fix_code(self, code: str, error: str) -> str:
        """إصلاح الكود"""
        prompt = f"""هذا الكود به خطأ: {error}

الكود:
```{code}
```

قدم الكود المصحح مع شرح."""
        
        fixed = self._call(prompt, "You are a Python expert. Fix the code errors.", max_tokens=2000)
        return fixed
    
    def generate_report(self, stats: Dict) -> str:
        """توليد تقرير"""
        prompt = f"""أنشئ تقريراً يوميماً لمنصة تفسير الأحلام بناءً على البيانات:

إحصائيات اليوم:
- المقالات: {stats.get('articles', 0)}
- المستخدمين: {stats.get('users', 0)}
- الأحلام المفسرة: {stats.get('dreams', 0)}

التقرير debe avere:
- ملخصExecutive
- أهم الإنجازات
- التوصيات للمستقبل"""

        return self._call(prompt, max_tokens=1500)


# ============================================
# 📱 إدارة منصات التواصل
# ============================================
class SocialPoster:
    """الناشر على منصات التواصل"""
    
    def __init__(self):
        self.telegram_token = config.TELEGRAM_TOKEN
        self.telegram_channel = config.TELEGRAM_CHANNEL
        self.discord_webhook = config.DISCORD_WEBHOOK
    
    def post_to_telegram(self, message: str, photo_path: str = None) -> Dict:
        """نشر على تيليجرام"""
        if not self.telegram_token:
            return {"success": False, "error": "TELEGRAM_TOKEN غير موجود"}
        
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        
        try:
            if photo_path:
                # صورة + نص
                with open(photo_path, 'rb') as f:
                    files = {'photo': f}
                    data = {
                        'chat_id': self.telegram_channel,
                        'caption': message,
                        'parse_mode': 'HTML'
                    }
                    r = requests.post(url.replace('sendMessage', 'sendPhoto'), 
                                   data=data, files=files)
            else:
                # نص فقط
                r = requests.post(url, json={
                    'chat_id': self.telegram_channel,
                    'text': message,
                    'parse_mode': 'HTML'
                })
            
            result = r.json()
            return {"success": result.get("ok", False), "response": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def post_to_discord(self, message: str) -> Dict:
        """نشر على Discord"""
        if not self.discord_webhook:
            return {"success": False, "error": "DISCORD_WEBHOOK غير موجود"}
        
        try:
            r = requests.post(self.discord_webhook, json={"content": message})
            return {"success": r.status_code == 204, "status": r.status_code}
        except Exception as e:
            return {"success": False, "error": str(e)}


# ============================================
# 📊 مدير المحتوى
# ============================================
class ContentManager:
    """مدير المحتوى"""
    
    def __init__(self, blog_dir: str = config.BLOG_DIR):
        self.blog_dir = blog_dir
        os.makedirs(blog_dir, exist_ok=True)
    
    def save_article(self, article: Dict) -> str:
        """حفظ المقال"""
        title = article.get("title", "مقال جديد")
        # إنشاء slug
        slug = re.sub(r'[^\w\u0600-\u06FF]', '-', title.lower())
        slug = re.sub(r'-+', '-', slug).strip('-')
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{date_str}-{slug}.html"
        filepath = os.path.join(self.blog_dir, filename)
        
        # إنشاء HTML
        html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | تفسير الأحلام</title>
    <meta name="description" content="{title}">
    <meta property="og:title" content="{title}">
    <meta property="og:type" content="article">
    <link rel="canonical" href="{config.SITE_URL}/{filename}">
    <style>
        body {{ font-family: 'Tajawal', 'Segoe UI', sans-serif; 
              background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 100%);
              color: #e2d9f3; line-height: 1.8; padding: 2rem; margin: 0; }}
        .container {{ max-width: 800px; margin: auto; }}
        h1 {{ color: #f0c060; border-bottom: 2px solid #7c3aed; padding-bottom: 1rem; }}
        .meta {{ color: #888; font-size: 0.9rem; margin: 1rem 0; }}
        .content {{ background: rgba(255,255,255,0.05); padding: 2rem; border-radius: 1rem; }}
        .back {{ display: inline-block; margin-top: 2rem; color: #f0c060; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="meta">📅 {article.get('date', date_str)} | ⏱️ 10 دقائق قراءة</div>
        <div class="content">
            {article.get('content', '').replace(chr(10), '<br>')}
        </div>
        <a href="/blog.html" class="back">← العودة للمدونة</a>
    </div>
</body>
</html>"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return filepath
    
    def get_articles_list(self) -> List[str]:
        """قائمة المقالات"""
        if not os.path.exists(self.blog_dir):
            return []
        return [f for f in os.listdir(self.blog_dir) if f.endswith('.html')]


# ============================================
# 🎧 دعم العملاء
# ============================================
class SupportAgent:
    """وكيل دعم العملاء"""
    
    def __init__(self):
        self.ai = NIMClient()
        self.sessions: Dict[int, Dict] = {}
    
    def handle(self, user_id: int, message: str) -> str:
        """معالجة رسالة"""
        # إنشاء جلسة إذا لم تكن موجودة
        if user_id not in self.sessions:
            self.sessions[user_id] = {"history": [], "last_dream": None}
        
        session = self.sessions[user_id]
        
        # التحقق إذا كان حلم
        dream_keywords = ["حلم", "رأيت", "منام", "dream", "saw"]
        is_dream = any(kw in message.lower() for kw in dream_keywords)
        
        if is_dream:
            session["last_dream"] = message
            return self.ai.interpret_dream(message)
        
        # رد ذكي
        history = "\n".join(session["history"][-3:])
        context = f"مح.previous conversation:\n{history}\nLast dream: {session.get('last_dream', 'None')}"
        
        return self.ai.chat(message)


# ============================================
# 🤖 الوكيل الشامل
# ============================================
class WeaverAgent:
    """الوكيل الشامل للأتمتة"""
    
    def __init__(self):
        self.ai = NIMClient()
        self.content = ContentManager()
        self.social = SocialPoster()
        self.support = SupportAgent()
    
    def generate_and_publish(self, topic: str) -> Dict:
        """توليد ومثال"""
        print(f"🔄 جاري توليد مقال: {topic}")
        
        # 1. توليد المقال
        article = self.ai.generate_article(topic)
        
        # 2. حفظه
        filepath = self.content.save_article(article)
        print(f"✅ تم حفظ: {filepath}")
        
        # 3. نشر على تيليجرام
        message = f"""🔮 مقال جديد: {article['title']}

✨ اقرأ المقال: {config.SITE_URL}/{os.path.basename(filepath)}

🌙 جرب تفسير حلمك: {config.SITE_URL}/app/analyze"""

        result = self.social.post_to_telegram(message)
        
        return {
            "success": True,
            "article": article,
            "filepath": filepath,
            "social": result
        }
    
    def daily_automation(self, topic: str = None) -> Dict:
        """الأتمتة اليومية"""
        if not topic:
            topics = [
                "رموز الأحلام في الحضارات القديمة",
                "تفسير الثعبان في المنام",
                "أحلام الطيران ومعناها",
                "الماء في الأحلام",
                "الأسنان في الأحلام"
            ]
            import random
            topic = random.choice(topics)
        
        return self.generate_and_publish(topic)
    
    def interpret(self, dream: str) -> str:
        """تفسير حلم"""
        return self.ai.interpret_dream(dream)
    
    def fix_problem(self, code: str, error: str) -> str:
        """إصلاح مشكلة"""
        return self.ai.fix_code(code, error)


# ============================================
# 🚀 نقطة الدخول
# ============================================
def main():
    """النقطة الرئيسية"""
    import argparse
    
    parser = argparse.ArgumentParser(description="🤖 Weaver AI Agent")
    parser.add_argument("--topic", type=str, help="موضوع المقال")
    parser.add_argument("--dream", type=str, help="تفسير حلم")
    parser.add_argument("--fix", nargs=2, type=str, help="إصلاح: --fix 'code' 'error'")
    parser.add_argument("--chat", type=str, help="دردشة")
    parser.add_argument("--daily", action="store_true", help="أتمتة يومية")
    parser.add_argument("--port", type=int, default=8082, help="منفذ Proxy")
    
    args = parser.parse_args()
    
    # تغيير المنفذ إذا需要的
    if args.port != 8082:
        config.PROXY_URL = f"http://localhost:{args.port}"
    
    agent = WeaverAgent()
    
    if args.topic:
        result = agent.generate_and_publish(args.topic)
        print(f"✅ {result}")
    
    elif args.dream:
        result = agent.interpret(args.dream)
        print(result)
    
    elif args.fix:
        code, error = args.fix
        result = agent.fix_problem(code, error)
        print(result)
    
    elif args.chat:
        result = agent.ai.chat(args.chat)
        print(result)
    
    elif args.daily:
        result = agent.daily_automation()
        print(f"✅ أكملت: {result}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()