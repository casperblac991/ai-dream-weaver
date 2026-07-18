#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام المشاركة الاجتماعية الفيروسية - Viral Sharing
"""

import json
from datetime import datetime
from urllib.parse import quote

class ViralShareGenerator:
    """مولد محتوى المشاركة الفيروسية"""
    
    @staticmethod
    def generate_share_card(dream_interpretation: str, symbol: str):
        """توليد بطاقة مشاركة جذابة"""
        return {
            "title": f"🌙 تفسير حلمي: {symbol}",
            "description": dream_interpretation[:100] + "...",
            "image": f"https://aidreamweaver.store/api/generate-card?symbol={symbol}",
            "url": f"https://aidreamweaver.store/share/{symbol}",
            "cta": "اكتشف تفسير حلمك الآن! 🔮"
        }
    
    @staticmethod
    def generate_twitter_share(dream_interpretation: str, symbol: str):
        """توليد نص تويتر للمشاركة"""
        text = f"🌙 لقد فسرت حلمي عن {symbol}!\n\n{dream_interpretation[:140]}\n\n#تفسير_الأحلام #Weaver"
        return {
            "platform": "twitter",
            "text": text,
            "url": f"https://twitter.com/intent/tweet?text={quote(text)}&url=https://aidreamweaver.store"
        }
    
    @staticmethod
    def generate_facebook_share(dream_interpretation: str, symbol: str):
        """توليد رابط فيسبوك للمشاركة"""
        return {
            "platform": "facebook",
            "url": f"https://www.facebook.com/sharer/sharer.php?u=https://aidreamweaver.store/share/{symbol}",
            "quote": f"لقد فسرت حلمي عن {symbol} باستخدام Weaver! 🌙"
        }
    
    @staticmethod
    def generate_whatsapp_share(dream_interpretation: str, symbol: str):
        """توليد رابط واتس آب للمشاركة"""
        message = f"🌙 تفسير حلمي عن {symbol}:\n\n{dream_interpretation}\n\nجرب Weaver: https://aidreamweaver.store"
        return {
            "platform": "whatsapp",
            "url": f"https://wa.me/?text={quote(message)}",
            "message": message
        }
    
    @staticmethod
    def generate_instagram_caption(symbol: str):
        """توليد نص إنستجرام"""
        return {
            "platform": "instagram",
            "caption": f"🌙 تفسير حلم {symbol}\n\n✨ هل حلمت بـ {symbol}؟\n\n🔮 اكتشف معنى حلمك الآن\n\nرابط في البايو 👆\n\n#تفسير_الأحلام #الأحلام #Weaver #تفسير_الرؤى",
            "hashtags": ["تفسير_الأحلام", "الأحلام", "Weaver", "تفسير_الرؤى", "ابن_سيرين"]
        }
    
    @staticmethod
    def generate_tiktok_description(symbol: str):
        """توليد وصف TikTok"""
        return {
            "platform": "tiktok",
            "description": f"🌙 تفسير حلم {symbol} #تفسير_الأحلام #الأحلام #Weaver #FYP #ForYou",
            "hashtags": ["تفسير_الأحلام", "الأحلام", "Weaver", "FYP", "ForYou"]
        }

class ReferralSystem:
    """نظام الإحالة (Referral Program)"""
    
    @staticmethod
    def generate_referral_link(user_id: int):
        """توليد رابط إحالة فريد"""
        return {
            "referral_code": f"WEAVER{user_id}",
            "referral_link": f"https://aidreamweaver.store?ref=WEAVER{user_id}",
            "reward": "احصل على 30 يوم مجاني عند إحالة صديق"
        }
    
    @staticmethod
    def track_referral(referrer_id: int, referred_user_id: int):
        """تتبع الإحالة"""
        return {
            "referrer_id": referrer_id,
            "referred_user_id": referred_user_id,
            "reward_status": "pending",
            "reward_amount": 30,  # أيام مجانية
            "created_at": datetime.now().isoformat()
        }

class ViralMetrics:
    """قياس انتشار المحتوى الفيروسي"""
    
    METRICS = {
        "total_shares": 0,
        "twitter_shares": 0,
        "facebook_shares": 0,
        "whatsapp_shares": 0,
        "instagram_shares": 0,
        "tiktok_shares": 0,
        "referrals": 0,
        "viral_score": 0
    }
    
    @staticmethod
    def track_share(platform: str):
        """تتبع مشاركة"""
        ViralMetrics.METRICS["total_shares"] += 1
        ViralMetrics.METRICS[f"{platform}_shares"] += 1
        ViralMetrics.METRICS["viral_score"] += 10
        return ViralMetrics.METRICS
    
    @staticmethod
    def get_viral_metrics():
        """الحصول على مقاييس الانتشار"""
        return {
            "total_shares": ViralMetrics.METRICS["total_shares"],
            "by_platform": {
                "twitter": ViralMetrics.METRICS["twitter_shares"],
                "facebook": ViralMetrics.METRICS["facebook_shares"],
                "whatsapp": ViralMetrics.METRICS["whatsapp_shares"],
                "instagram": ViralMetrics.METRICS["instagram_shares"],
                "tiktok": ViralMetrics.METRICS["tiktok_shares"]
            },
            "referrals": ViralMetrics.METRICS["referrals"],
            "viral_score": ViralMetrics.METRICS["viral_score"]
        }

class ShareOptimization:
    """تحسين المشاركة للانتشار الأقصى"""
    
    @staticmethod
    def optimize_for_platform(content: str, platform: str):
        """تحسين المحتوى لكل منصة"""
        optimizations = {
            "twitter": {
                "max_length": 280,
                "add_hashtags": True,
                "add_emojis": True
            },
            "facebook": {
                "max_length": 63206,
                "add_image": True,
                "add_description": True
            },
            "instagram": {
                "max_length": 2200,
                "add_hashtags": True,
                "add_emojis": True,
                "add_image": True
            },
            "tiktok": {
                "max_length": 2200,
                "add_hashtags": True,
                "add_emojis": True,
                "add_video": True
            }
        }
        
        return optimizations.get(platform, {})
    
    @staticmethod
    def get_best_posting_time(platform: str):
        """الحصول على أفضل وقت للنشر"""
        best_times = {
            "twitter": "9:00 AM - 3:00 PM",
            "facebook": "1:00 PM - 4:00 PM",
            "instagram": "11:00 AM - 1:00 PM, 7:00 PM - 9:00 PM",
            "tiktok": "6:00 AM - 10:00 AM, 7:00 PM - 11:00 PM"
        }
        return best_times.get(platform, "")

if __name__ == "__main__":
    # اختبار النظام
    generator = ViralShareGenerator()
    share_card = generator.generate_share_card("حلم الطيران يشير إلى الحرية والطموح", "الطيران")
    print("Share Card:", json.dumps(share_card, indent=2, ensure_ascii=False))
