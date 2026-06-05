#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت نشر المقالات اليومي لمنصة نَسَّاج الأحلام
يقوم بتوليد مقالات تلقائية عن تفسير الأحلام بالذكاء الاصطناعي
"""

import os
import sys
from datetime import datetime
import json
import random
import logging

# إعداد الـ logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# محاولة استيراد المكتبات المطلوبة
try:
    from groq import Groq
    logger.info("✅ تم استيراد مكتبة Groq بنجاح")
except ImportError as e:
    logger.error(f"❌ فشل استيراد Groq: {e}")
    logger.info("محاولة التثبيت...")
    os.system("pip install groq")
    from groq import Groq

try:
    import requests
    logger.info("✅ تم استيراد مكتبة requests بنجاح")
except ImportError:
    logger.error("❌ فشل استيراد requests")
    os.system("pip install requests")
    import requests


class DailyBlogBot:
    """بوت توليد المقالات اليومية"""
    
    def __init__(self):
        """تهيئة البوت"""
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.groq_api_key:
            logger.warning("⚠️ GROQ_API_KEY غير موجود - سيتم استخدام محتوى احتياطي")
        
        self.client = None
        if self.groq_api_key:
            try:
                self.client = Groq(api_key=self.groq_api_key)
                logger.info("✅ تم تهيئة Groq client بنجاح")
            except Exception as e:
                logger.error(f"❌ فشل تهيئة Groq client: {e}")
        
        # مواضيع المقالات
        self.topics = [
            "تفسير حلم الماء في المنام",
            "رؤية الثعبان في الحلم - التفسير الشامل",
            "تفسير حلم الطيران في السماء",
            "رؤية الموت في المنام - المعاني والدلالات",
            "تفسير حلم النار والحريق",
            "رؤية الحيوانات في الأحلام",
            "تفسير حلم السقوط من مكان عالٍ",
            "رؤية الأشخاص الموتى في المنام",
            "تفسير حلم المال والثروة",
            "رؤية البحر في المنام",
            "تفسير حلم الزواج للعزباء",
            "رؤية الحمل في المنام",
            "تفسير حلم السفر والرحلات",
            "رؤية المطر في الحلم",
            "تفسير حلم البكاء والحزن"
        ]
        
        # قوالب HTML للمقالات
        self.html_template = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | نَسَّاج الأحلام</title>
    <meta name="description" content="{description}">
    <meta name="keywords" content="تفسير الأحلام, {keywords}">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://aidreamweaver.store/{slug}">
    
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" href="css/blog.css">
</head>
<body>
    <header>
        <nav>
            <div class="container">
                <a href="index.html" class="logo">🌙 نَسَّاج الأحلام</a>
                <ul class="nav-links">
                    <li><a href="index.html">الرئيسية</a></li>
                    <li><a href="blog.html">المدونة</a></li>
                    <li><a href="dream.html">تفسير حلمك</a></li>
                    <li><a href="about.html">من نحن</a></li>
                </ul>
            </div>
        </nav>
    </header>

    <main class="article-page">
        <article class="container">
            <header class="article-header">
                <h1>{title}</h1>
                <div class="article-meta">
                    <span class="date">📅 {date}</span>
                    <span class="author">✍️ فريق نَسَّاج الأحلام</span>
                    <span class="reading-time">⏱️ {reading_time} دقائق قراءة</span>
                </div>
            </header>

            <div class="article-content">
                {content}
            </div>

            <footer class="article-footer">
                <div class="tags">
                    {tags}
                </div>
                
                <div class="share-buttons">
                    <h3>شارك المقال:</h3>
                    <button onclick="shareOnTwitter()">🐦 تويتر</button>
                    <button onclick="shareOnFacebook()">📘 فيسبوك</button>
                    <button onclick="shareOnWhatsApp()">💬 واتساب</button>
                </div>
            </footer>
        </article>
    </main>

    <footer class="site-footer">
        <div class="container">
            <p>© 2026 نَسَّاج الأحلام - منصة تفسير الأحلام بالذكاء الاصطناعي</p>
        </div>
    </footer>

    <script src="js/main.js"></script>
</body>
</html>"""
    
    def generate_article_with_ai(self, topic):
        """توليد مقال باستخدام AI"""
        if not self.client:
            logger.warning("⚠️ Groq client غير متاح - استخدام محتوى احتياطي")
            return self.generate_fallback_article(topic)
        
        try:
            logger.info(f"🤖 توليد مقال عن: {topic}")
            
            prompt = f"""أنت كاتب محترف متخصص في تفسير الأحلام. اكتب مقالاً شاملاً عن "{topic}" بالعربية.

يجب أن يتضمن المقال:
1. مقدمة جذابة (100-150 كلمة)
2. المعنى الرئيسي للحلم (200-300 كلمة)
3. التفسيرات المختلفة حسب السياق (300-400 كلمة)
4. الرموز والدلالات (200-250 كلمة)
5. خاتمة ملهمة (100-150 كلمة)

استخدم تنسيق HTML مع عناوين <h2> و <h3> وفقرات <p>.
اجعل المحتوى غنياً بالمعلومات ومفيداً للقارئ."""

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "أنت خبير في تفسير الأحلام وكتابة المحتوى العربي."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            logger.info(f"✅ تم توليد المقال بنجاح ({len(content)} حرف)")
            return content
            
        except Exception as e:
            logger.error(f"❌ فشل توليد المقال: {e}")
            return self.generate_fallback_article(topic)
    
    def generate_fallback_article(self, topic):
        """توليد مقال احتياطي عند فشل AI"""
        logger.info("📝 إنشاء مقال احتياطي...")
        
        return f"""
<h2>مقدمة</h2>
<p>يعتبر {topic} من الأحلام الشائعة التي يراها الكثيرون، وله دلالات ومعانٍ عميقة في عالم تفسير الأحلام.</p>

<h2>التفسير العام</h2>
<p>يشير {topic} في المنام إلى العديد من المعاني والدلالات التي تختلف باختلاف سياق الحلم وحالة الرائي.</p>

<h3>للعزباء</h3>
<p>قد يرمز هذا الحلم للعزباء إلى تغييرات إيجابية قادمة في حياتها.</p>

<h3>للمتزوجة</h3>
<p>بالنسبة للمرأة المتزوجة، قد يدل الحلم على استقرار الحياة الأسرية.</p>

<h3>للرجل</h3>
<p>أما بالنسبة للرجل، فقد يشير الحلم إلى النجاح في العمل أو المشاريع.</p>

<h2>الدلالات الإيجابية</h2>
<p>من بين الدلالات الإيجابية لهذا الحلم:</p>
<ul>
    <li>تحقيق الأهداف والطموحات</li>
    <li>تحسن الأحوال المادية</li>
    <li>السعادة والراحة النفسية</li>
</ul>

<h2>الدلالات السلبية</h2>
<p>في بعض الحالات، قد يحمل الحلم دلالات تحذيرية مثل:</p>
<ul>
    <li>وجود عقبات في الطريق</li>
    <li>الحاجة إلى الحذر في اتخاذ القرارات</li>
    <li>التنبيه لأمور تحتاج إلى اهتمام</li>
</ul>

<h2>نصائح عملية</h2>
<p>إذا رأيت هذا الحلم، يُنصح بما يلي:</p>
<ul>
    <li>التفكر في حالتك النفسية الحالية</li>
    <li>تدوين تفاصيل الحلم فور الاستيقاظ</li>
    <li>الاستعانة بالله والدعاء</li>
</ul>

<h2>خاتمة</h2>
<p>تذكر أن تفسير الأحلام علم واسع، والتفسيرات تختلف باختلاف السياق والظروف. نسأل الله أن يرينا وإياكم في المنام ما يسرنا.</p>
"""
    
    def create_blog_post(self):
        """إنشاء مقال مدونة جديد"""
        try:
            # اختيار موضوع عشوائي
            topic = random.choice(self.topics)
            logger.info(f"📌 الموضوع المختار: {topic}")
            
            # توليد المحتوى
            content = self.generate_article_with_ai(topic)
            
            # إنشاء البيانات الوصفية
            date = datetime.now()
            slug = f"{date.strftime('%Y-%m-%d')}-{topic.replace(' ', '-')}"
            
            # حساب وقت القراءة (متوسط 200 كلمة/دقيقة)
            word_count = len(content.split())
            reading_time = max(1, word_count // 200)
            
            # التوصيف
            description = f"تفسير شامل ومفصل عن {topic} في المنام مع الدلالات والمعاني المختلفة."
            keywords = f"{topic}, تفسير الأحلام, رؤيا, منام"
            
            # الوسوم
            tags_list = topic.split()[:3]
            tags_html = " ".join([f'<span class="tag">#{tag}</span>' for tag in tags_list])
            
            # ملء القالب
            html_content = self.html_template.format(
                title=topic,
                description=description,
                keywords=keywords,
                slug=slug,
                date=date.strftime('%Y-%m-%d'),
                reading_time=reading_time,
                content=content,
                tags=tags_html
            )
            
            # حفظ الملف
            filename = f"{slug}.html"
            with open('/home/ubuntu/ai-dream-weaver/templates/' + filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"✅ تم إنشاء المقال: {filename}")
            
            # تحديث صفحة المدونة
            self.update_blog_index(topic, slug, description, date)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ فشل إنشاء المقال: {e}")
            return False
    
    def update_blog_index(self, title, slug, description, date):
        """تحديث صفحة فهرس المدونة"""
        try:
            blog_index_file = '/home/ubuntu/ai-dream-weaver/templates/blog.html'
            
            if not os.path.exists(blog_index_file):
                logger.warning("⚠️ ملف blog.html غير موجود")
                return
            
            # قراءة المحتوى الحالي
            with open(blog_index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # إنشاء بطاقة المقال الجديد
            new_card = f"""
        <article class="article-card reveal visible">
            <div class="article-category">✦ {title}</div>
            <h3><a href="{slug}.html">{title}</a></h3>
            <p>{description}</p>
            <div class="article-meta">📅 {date.strftime("%Y-%m-%d")} • 5 min read</div>
            <a href="{slug}.html" class="read-more">اقرأ المزيد →</a>
        </article>
        <article class="blog-card">
            <div class="blog-card-header">
                <h3><a href="{slug}.html">{title}</a></h3>
                <span class="date">📅 {date.strftime('%Y-%m-%d')}</span>
            </div>
            <p>{description}</p>
            <a href="{slug}.html" class="read-more">اقرأ المزيد ←</a>
        </article>
"""
            
            # إضافة المقال الجديد في بداية القائمة
            if '<div class="posts-grid" id="postsGrid">' in content:
                content = content.replace(
                    '<div class="posts-grid" id="postsGrid">',
                    f'<div class="posts-grid" id="postsGrid">{new_card}',
                    1
                )
                
                with open(blog_index_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info("✅ تم تحديث صفحة المدونة")
            else:
                logger.warning("⚠️ لم يتم العثور على posts-grid في blog.html")
                
        except Exception as e:
            logger.error(f"❌ فشل تحديث فهرس المدونة: {e}")


def main():
    """الوظيفة الرئيسية"""
    try:
        logger.info("🚀 بدء تشغيل البوت...")
        
        bot = DailyBlogBot()
        success = bot.create_blog_post()
        
        if success:
            logger.info("✅ تم تنفيذ البوت بنجاح!")
            return 0
        else:
            logger.error("❌ فشل تنفيذ البوت")
            return 1
            
    except Exception as e:
        logger.error(f"❌ خطأ فادح: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
