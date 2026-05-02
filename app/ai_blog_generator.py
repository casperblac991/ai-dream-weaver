"""
بوت توليد المقالات بالذكاء الاصطناعي (AI Blog Generator)
يقوم بكتابة مقالات جديدة ثنائية اللغة ونشرها تلقائياً
"""

import os
from datetime import datetime
from app.blog_manager import BlogPost, BlogManager
import asyncio

# استيراد مكتبات الذكاء الاصطناعي
try:
    from groq import Groq
except ImportError:
    print("⚠️ تحذير: مكتبة Groq غير مثبتة")

class AIBlogGenerator:
    """مولد المقالات الذكي"""
    
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
        self.blog_manager = BlogManager()
        self.dream_topics = [
            "الأسد والقوة",
            "الماء والعواطف",
            "الطيران والحرية",
            "الثعبان والحكمة",
            "السقوط والخوف",
            "الضياع والارتباك",
            "المنزل والأمان",
            "الموت والتحول",
            "الزواج والالتزام",
            "الامتحان والقلق"
        ]
    
    async def generate_article(self, topic: str) -> dict:
        """توليد مقالة جديدة بالعربية والإنجليزية"""
        try:
            # توليد المحتوى بالعربية
            ar_content = await self._generate_content_ar(topic)
            
            # توليد المحتوى بالإنجليزية
            en_content = await self._generate_content_en(topic)
            
            # استخراج العناوين
            ar_title = f"تفسير حلم {topic} - دليل شامل"
            en_title = f"Dream of {topic} Interpretation - Complete Guide"
            
            return {
                "title_ar": ar_title,
                "title_en": en_title,
                "content_ar": ar_content,
                "content_en": en_content,
                "topic": topic
            }
        except Exception as e:
            print(f"❌ خطأ في توليد المقالة: {e}")
            return None
    
    async def _generate_content_ar(self, topic: str) -> str:
        """توليد محتوى المقالة بالعربية"""
        prompt = f"""
أنت خبير في تفسير الأحلام. اكتب مقالة شاملة عن تفسير حلم "{topic}" بالعربية.

المقالة يجب أن تتضمن:
1. مقدمة جذابة عن الموضوع
2. المعاني الرئيسية للحلم (3-5 معاني)
3. تفسيرات مختلفة حسب السياق
4. نصائح عملية للمستخدم
5. خاتمة مفيدة

الصيغة: استخدم HTML مع الفقرات والقوائم.
الطول: 400-500 كلمة
اللغة: عربية فصحى
"""
        
        try:
            message = self.client.messages.create(
                model="mixtral-8x7b-32768",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            print(f"خطأ في توليد المحتوى العربي: {e}")
            return f"<p>مقالة عن تفسير حلم {topic}</p>"
    
    async def _generate_content_en(self, topic: str) -> str:
        """توليد محتوى المقالة بالإنجليزية"""
        prompt = f"""
You are an expert in dream interpretation. Write a comprehensive article about the interpretation of "{topic}" dreams in English.

The article should include:
1. An engaging introduction to the topic
2. Main meanings of the dream (3-5 meanings)
3. Different interpretations based on context
4. Practical tips for the user
5. A helpful conclusion

Format: Use HTML with paragraphs and lists.
Length: 400-500 words
Language: English

Write the content in HTML format.
"""
        
        try:
            message = self.client.messages.create(
                model="mixtral-8x7b-32768",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            print(f"Error generating English content: {e}")
            return f"<p>Article about {topic} dream interpretation</p>"
    
    async def publish_article(self, article_data: dict) -> bool:
        """نشر المقالة في المدونة"""
        try:
            # إنشاء slug من الموضوع
            slug = article_data["topic"].replace(" ", "-").lower()
            slug = f"dream-{slug}-{datetime.now().strftime('%Y%m%d')}"
            
            # إنشاء كائن المقالة
            post = BlogPost(
                slug=slug,
                title_ar=article_data["title_ar"],
                title_en=article_data["title_en"],
                content_ar=article_data["content_ar"],
                content_en=article_data["content_en"],
                category="تفسير أحلام"
            )
            
            # حفظ المقالة
            if self.blog_manager.save_post(post):
                print(f"✅ تم نشر المقالة: {article_data['title_ar']}")
                return True
            else:
                print(f"❌ فشل نشر المقالة: {article_data['title_ar']}")
                return False
        except Exception as e:
            print(f"❌ خطأ في نشر المقالة: {e}")
            return False
    
    async def generate_daily_article(self) -> bool:
        """توليد ونشر مقالة يومية"""
        import random
        
        # اختيار موضوع عشوائي
        topic = random.choice(self.dream_topics)
        
        print(f"🤖 جاري توليد مقالة عن: {topic}")
        
        # توليد المقالة
        article_data = await self.generate_article(topic)
        
        if article_data:
            # نشر المقالة
            return await self.publish_article(article_data)
        
        return False
    
    async def generate_multiple_articles(self, count: int = 5) -> int:
        """توليد عدة مقالات"""
        published_count = 0
        
        for i, topic in enumerate(self.dream_topics[:count]):
            print(f"\n📝 المقالة {i+1}/{count}: {topic}")
            
            article_data = await self.generate_article(topic)
            if article_data:
                if await self.publish_article(article_data):
                    published_count += 1
            
            # تأخير بين المقالات لتجنب الحد من الطلبات
            await asyncio.sleep(2)
        
        return published_count

# دالة للاستخدام من خارج الملف
async def run_daily_blog_generation():
    """تشغيل توليد المقالات اليومي"""
    generator = AIBlogGenerator()
    success = await generator.generate_daily_article()
    return success

if __name__ == "__main__":
    # اختبار البوت
    import asyncio
    
    generator = AIBlogGenerator()
    
    # توليد 3 مقالات للاختبار
    print("🚀 بدء توليد المقالات...")
    count = asyncio.run(generator.generate_multiple_articles(3))
    print(f"\n✅ تم نشر {count} مقالات بنجاح!")
