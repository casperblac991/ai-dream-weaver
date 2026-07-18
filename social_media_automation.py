#!/usr/bin/env python3
"""
AI Dream Weaver - Social Media Marketing Automation
============================================
سكريبت أتمتة التسويق على منصات التواصل الاجتماعي بالذكاء الاصطناعي

المميزات:
- جدولة المنشورات كل 6 ساعات
- توليد محتوى ذكي باستخدام AI
- النشر على Twitter, Facebook, Telegram
- تحليل التفاعل والتقارير

التشغيل:
    python3 social_media_automation.py
    
للخدمة كdaemon:
    python3 social_media_automation.py --daemon
"""

import os
import json
import time
import random
import asyncio
import logging
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import threading

# Third-party imports
try:
    import requests as _requests
    requests = _requests
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'requests', '-q'])
    import requests

try:
    import groq as _groq
    groq = _groq
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'groq', '-q'])
    import groq

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/project/ai-dream-weaver/logs/social_media.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class SocialPost:
    """نموذج منشور على وسائل التواصل الاجتماعي"""
    content: str
    platform: str
    hashtags: List[str] = field(default_factory=list)
    scheduled_at: Optional[datetime] = None
    posted: bool = False
    likes: int = 0
    shares: int = 0
    comments: int = 0


@dataclass  
class CampaignStats:
    """إحصائيات الحملة"""
    total_posts: int = 0
    successful_posts: int = 0
    failed_posts: int = 0
    total_reach: int = 0
    total_engagement: int = 0
    top_content: List[str] = field(default_factory=list)


class DreamContentGenerator:
    """مولد محتوى ذكي للأحلام باستخدام AI"""
    
    DREAM_TOPICS = [
        {
            "title": "رؤية البحر في المنام",
            "summary": "دليل على الاستقرار العاطفي والتوازن النفسي",
            "arabic_content": "البحر في المنام يرمز للمشاعر العميقة stability. إذا كان هادئاً فذلك يدل على السكينة، وإذا كان عاصفاً فيدل على توتر داخلي.",
            "tags": ["#الأحلام", "#البحر", "#التفسير_الإسلامي", "#علم_النفس"]
        },
        {
            "title": "تفسير حلم السقوط من مكان عالٍ", 
            "summary": "دلالة على فقدان السيطرة أو القلق من الفشل",
            "arabic_content": "السقوط من مكان عالٍ في المنام يعكس مخاوفك من الفشل أو فقدان مكانتك. إنه رسالة من عقلك الباطني تطمئنك أن كل فشل يقود لنهوض.",
            "tags": ["#الأحلام", "#السقوط", "#القلق", "#التفسير"]
        },
        {
            "title": "رؤية الثعبان في الحلم",
            "summary": "رمز للتقوى والحيوية أو للعدو الخفي",
            "arabic_content": "الثعبان في المنام يرمز للعدو الخفي أو للقوة الحيوية. قتله يعني победу على الأعداء، ولمسه يعني الاستفادة من الحكمة القديمة.",
            "tags": ["#الأحلام", "#الثعبان", "#التفسير_الإسلامي", "#الرموز"]
        },
        {
            "title": "حلم النار والحريق",
            "summary": "دليل على الغضب المكبوت أو الطاقة الروحية",
            "arabic_content": "النار في المنام.symbolizes الغضب الداخلي أو الطاقة القوية. حريق بيتك يعنيProblems في العائلة، وحريق الغابة يعني التغييرات الكبيرة.",
            "tags": ["#الأحلام", "#النار", "#التفسير", "#الرموز"]
        },
        {
            "title": "تفسير حلم الزواج للعزباء",
            "summary": "رمز للارتباط الحقيقي أو التغير في الحياة",
            "arabic_content": "الزواج في المنام للعزباء يرمز لتجربة جديدة أو مشروع مهم. قد يعني الارتباط بشخص جديد أو اتخاذ قرار مصيري.",
            "tags": ["#الأحلام", "#الزواج", "#التفسير", "#التغيير"]
        },
        {
            "title": "رؤية المال والثرروة في الحلم",
            "summary": "دليل على الثقة بالنفس والقيمة الشخصية",
            "arabic_content": "المال في المنام يرمز لقيمتك وثقتك بنفسك. جمع المال يعني ganancias قريباً، وإنفاقه يعني كرمك وسخاءك.",
            "tags": ["#الأحلام", "#المال", "#الثرروة", "#التفسير"]
        },
        {
            "title": "حلم سقوط الأسنان",
            "summary": "دليل على القلق من فقدان السيطرة",
            "arabic_content": "سقوط الأسنان في المنام يرمز للقلق من كلمة أو فعل. اسندانك تدل على أقارب، والأسنان الطويلة تعني قوة وحرية.",
            "tags": ["#الأحلام", "#الأسنان", "#القلق", "#التفسير"]
        },
        {
            "title": "رؤية الماء في المنام",
            "summary": "رمز للمشاعر والطهارة",
            "arabic_content": "الماء الصافي يدل على فرح وسعادة قادمة. الماء العكر يعني هموم وغم. الغرق يعني submerged في المشاعر.",
            "tags": ["#الأحلام", "#الماء", "#التفسير", "#المشاعر"]
        }
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.client = None
        if self.api_key:
            try:
                self.client = groq.Groq(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")
    
    def generate_post(self, platform: str = "telegram") -> SocialPost:
        """توليد منشور ذكي للأحلام"""
        # Select random dream topic
        topic = random.choice(self.DREAM_TOPICS)
        
        templates = {
            "telegram": f"""🌙 {topic['title']}

{topic['arabic_content']}

{topic['summary']}

🔗 للمزيد: ai-dreamweaver.store

{', '.join(topic['tags'])}""",
            
            "twitter": f"""🌙 {topic['title']}

{topic['summary']}

اكتشف المزيد 👇

{', '.join(topic['tags'])} #AI #DreamInterpretation""",
            
            "facebook": f"""✨ كل حلم يحمل رسالة!

{topic['title']}

{topic['arabic_content']}

{topic['summary']}

👈 زر موقعنا للمزيد من التفسيرات

#تفسير_الأحلام #علم_النفس #الأحلام_والرؤيا""",
            
            "instagram": f"""🌙✨\n{topic['title']}\n.\n.\n{topic['summary']}\n.\n.\n🔮 اكتشف معنا تفسير أحلامك\n.\n.\n{', '.join(topic['tags'])}\n.\n.\n#الأحلام #رؤيا #تفسير_الأحلام #علم_النفس #AI_Dreams"""
        }
        
        content = templates.get(platform, templates["telegram"])
        
        return SocialPost(
            content=content,
            platform=platform,
            hashtags=topic['tags']
        )
    
    def generate_engaging_content(self) -> List[SocialPost]:
        """توليد محتوى متعدد للمنصات"""
        posts = []
        for platform in ["telegram", "twitter", "facebook", "instagram"]:
            posts.append(self.generate_post(platform))
        return posts


class SocialMediaPoster:
    """ناشر على وسائل التواصل الاجتماعي"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.telegram_token = config.get("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat_id = config.get("TELEGRAM_CHAT_ID", "")
        self.twitter_bearer = config.get("TWITTER_BEARER_TOKEN", "")
        self.facebook_token = config.get("FACEBOOK_ACCESS_TOKEN", "")
        self.facebook_page_id = config.get("FACEBOOK_PAGE_ID", "")
        
    def post_to_telegram(self, post: SocialPost) -> bool:
        """النشر على Telegram"""
        if not self.telegram_token or not self.telegram_chat_id:
            logger.warning("Telegram credentials not configured")
            return False
            
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        data = {
            "chat_id": self.telegram_chat_id,
            "text": post.content,
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                logger.info(f"Posted to Telegram successfully")
                return True
            else:
                logger.error(f"Telegram posting failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Telegram error: {e}")
            return False
    
    def post_to_twitter(self, post: SocialPost) -> bool:
        """النشر على Twitter/X"""
        if not self.twitter_bearer:
            logger.warning("Twitter credentials not configured")
            return False
            
        url = "https://api.twitter.com/2/tweets"
        headers = {
            "Authorization": f"Bearer {self.twitter_bearer}",
            "Content-Type": "application/json"
        }
        data = {"text": post.content[:280]}
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=10)
            if response.status_code in [200, 201]:
                logger.info(f"Posted to Twitter successfully")
                return True
            else:
                logger.error(f"Twitter posting failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Twitter error: {e}")
            return False
    
    def post_to_facebook(self, post: SocialPost) -> bool:
        """النشر على Facebook"""
        if not self.facebook_token or not self.facebook_page_id:
            logger.warning("Facebook credentials not configured")
            return False
            
        url = f"https://graph.facebook.com/v18.0/{self.facebook_page_id}/feed"
        params = {
            "access_token": self.facebook_token,
            "message": post.content
        }
        
        try:
            response = requests.post(url, params=params, timeout=10)
            if response.status_code in [200, 201]:
                logger.info(f"Posted to Facebook successfully")
                return True
            else:
                logger.error(f"Facebook posting failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Facebook error: {e}")
            return False
    
    def post_all(self, posts: List[SocialPost]) -> Dict[str, bool]:
        """النشر على جميع المنصات"""
        results = {}
        for post in posts:
            if post.platform == "telegram":
                results["telegram"] = self.post_to_telegram(post)
            elif post.platform == "twitter":
                results["twitter"] = self.post_to_twitter(post)
            elif post.platform == "facebook":
                results["facebook"] = self.post_to_facebook(post)
            elif post.platform == "instagram":
                # Instagram uses Facebook API
                results["instagram"] = self.post_to_facebook(post)
        return results


class SocialMediaScheduler:
    """جدولة ومناولة الحملات التسويقية"""
    
    DEFAULT_INTERVAL_HOURS = 6
    
    def __init__(self, config: Dict):
        self.config = config
        self.interval_hours = int(config.get("POST_INTERVAL_HOURS", self.DEFAULT_INTERVAL_HOURS))
        self.content_generator = DreamContentGenerator(config.get("GROQ_API_KEY"))
        self.poster = SocialMediaPoster(config)
        self.stats = CampaignStats()
        self.running = False
        self._lock = threading.Lock()
        
    def load_stats(self) -> CampaignStats:
        """تحميل الإحصائيات من الملف"""
        stats_file = Path("/workspace/project/ai-dream-weaver/logs/campaign_stats.json")
        if stats_file.exists():
            try:
                with open(stats_file) as f:
                    data = json.load(f)
                    self.stats = CampaignStats(**data)
            except Exception as e:
                logger.error(f"Failed to load stats: {e}")
        return self.stats
    
    def save_stats(self):
        """حفظ الإحصائيات"""
        stats_file = Path("/workspace/project/ai-dream-weaver/logs/campaign_stats.json")
        stats_file.parent.mkdir(parents=True, exist_ok=True)
        with open(stats_file, 'w') as f:
            json.dump({
                "total_posts": self.stats.total_posts,
                "successful_posts": self.stats.successful_posts,
                "failed_posts": self.stats.failed_posts,
                "total_reach": self.stats.total_reach,
                "total_engagement": self.stats.total_engagement,
                "top_content": self.stats.top_content,
                "last_updated": datetime.now().isoformat()
            }, f, indent=2)
    
    def run_campaign(self):
        """تشغيل حملة تسويقية واحدة"""
        logger.info("Starting social media campaign...")
        
        # Generate content
        posts = self.content_generator.generate_engaging_content()
        
        # Post to all platforms
        results = self.poster.post_all(posts)
        
        # Update stats
        with self._lock:
            self.stats.total_posts += len(posts)
            for platform, success in results.items():
                if success:
                    self.stats.successful_posts += 1
                else:
                    self.stats.failed_posts += 1
            
            # Save stats
            self.save_stats()
        
        logger.info(f"Campaign completed. Results: {results}")
        return results
    
    def start_daemon(self):
        """تشغيل كخدمة خلفية"""
        logger.info(f"Starting social media automation daemon (every {self.interval_hours}h)...")
        self.running = True
        
        while self.running:
            self.run_campaign()
            # Sleep until next interval
            for _ in range(self.interval_hours * 60):
                if not self.running:
                    break
                time.sleep(60)  # Check every minute
    
    def stop(self):
        """إيقاف الخدمة"""
        self.running = False
        logger.info("Stopping social media automation...")


def main():
    """الدالة الرئيسية"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Dream Weaver Social Media Automation")
    parser.add_argument("--daemon", "-d", action="store_true", help="Run as daemon")
    parser.add_argument("--once", "-o", action="store_true", help="Run once and exit")
    parser.add_argument("--interval", "-i", type=int, default=6, help="Post interval in hours")
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    env_file = Path("/workspace/project/ai-dream-weaver/.env")
    
    # Try to load from .env file
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        config[key.strip()] = value.strip()
    
    # Also load from environment
    for key in ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "TWITTER_BEARER_TOKEN", 
               "FACEBOOK_ACCESS_TOKEN", "FACEBOOK_PAGE_ID", "GROQ_API_KEY"]:
        config[key] = os.getenv(key, config.get(key, ""))
    
    config["POST_INTERVAL_HOURS"] = str(args.interval)
    
    # Create scheduler
    scheduler = SocialMediaScheduler(config)
    
    if args.daemon:
        # Run as daemon
        try:
            scheduler.start_daemon()
        except KeyboardInterrupt:
            scheduler.stop()
    elif args.once:
        # Run once
        scheduler.run_campaign()
    else:
        # Interactive mode
        print("""
╔══════════════════════════════════════════════════════════╗
║    AI Dream Weaver - Social Media Automation            ║
║    أتمتة التسويق على وسائل التواصل الاجتماعي         ║
╠══════════════════════════════════════════════════════════╣
║  [1] تشغيل حملة واحدة                              ║
║  [2] تشغيل كخدمة خلفية (كل 6 ساعات)          ║
║  [3] عرض الإحصائيات                             ║
║  [q] خروج                                       ║
╚══════════════════════════════════════════════════════════╝
""")
        while True:
            choice = input("اختر: ").strip().lower()
            
            if choice == "1":
                scheduler.run_campaign()
            elif choice == "2":
                print("تشغيل الخدمة الخلفية...")
                try:
                    scheduler.start_daemon()
                except KeyboardInterrupt:
                    scheduler.stop()
                    print("تم إيقاف الخدمة.")
                    break
            elif choice == "3":
                stats = scheduler.load_stats()
                print(f"""
إحصائيات الحملة:
- إجمالي المنشورات: {stats.total_posts}
- المنشورات الناجحة: {stats.successful_posts}
- المنشورات الفاشلة: {stats.failed_posts}
- إجمالي الوصول: {stats.total_reach}
- إجمالي التفاعل: {stats.total_engagement}
""")
            elif choice == "q":
                break
            else:
                print("خيار غير صحيح")


if __name__ == "__main__":
    main()