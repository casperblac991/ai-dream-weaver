#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════╗
║       🎨 نظام توليد الصور المتعدد - Weaver | نَسَّاج          ║
║       Multi-Provider Image Generation System v1.0           ║
╠══════════════════════════════════════════════════════════════╣
║  المزودين (كلهم مجانيين):                                    ║
║  1. felo.ai - الأفضل (4K, غير محدود, بدون تسجيل)            ║
║  2. Pollinations.ai - احتياطي أول (مجاني مستقر)             ║
║  3. Gemini Flash Image - عبر مفتاح Gemini (إذا كان موجوداً) ║
║  4. SiliconFlow - إذا كان المفتاح موجوداً                    ║
║  5. Replicate - تجريبي (بدون مفتاح)                         ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import requests
import base64
import logging
import time
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# إعداد التسجيل
log = logging.getLogger(__name__)

# ============================================================
# المزود 1: felo.ai (الأفضل - مجاني، 4K، غير محدود)
# ============================================================

def generate_felo(prompt: str, timeout: int = 60) -> Optional[bytes]:
    """
    التوليد عبر felo.ai (Nano Banana Pro / Gemini 3 Pro Image)
    - مجاني تماماً، لا يحتاج مفتاح
    - جودة 4K، دقة نص عالية
    - غير محدود يومياً
    """
    try:
        log.info(f"🎨 felo.ai: جاري توليد صورة...")
        
        # المحاولة عبر API felo (الرسمي)
        url = "https://api.felo.ai/v1/gemini-image-gen"
        payload = {
            "prompt": prompt[:500],  # حد 500 حرف كافي
            "resolution": "2048x2048",
            "model": "gemini-3-pro-image-preview",
            "style": "cinematic"
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Weaver-Bot/3.0"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=timeout)
        
        if response.status_code == 200:
            data = response.json()
            # محاولة استخراج الصورة بعدة طرق
            if "image" in data:
                return base64.b64decode(data["image"])
            elif "images" in data and len(data["images"]) > 0:
                if "url" in data["images"][0]:
                    img_response = requests.get(data["images"][0]["url"], timeout=30)
                    return img_response.content
                elif "base64" in data["images"][0]:
                    return base64.b64decode(data["images"][0]["base64"])
            elif "output" in data and "image" in data["output"]:
                return base64.b64decode(data["output"]["image"])
        
        # المحاولة البديلة عبر nano-banana.ai
        log.info("🎨 felo.ai: جاري المحاولة عبر nano-banana...")
        url2 = "https://nano-banana.ai/api/generate"
        payload2 = {
            "prompt": prompt,
            "model": "gemini-3-pro-image",
            "resolution": "1024x1024"
        }
        response2 = requests.post(url2, json=payload2, timeout=timeout)
        
        if response2.status_code == 200:
            data2 = response2.json()
            if "image" in data2:
                return base64.b64decode(data2["image"])
        
        log.warning(f"felo.ai فشل: {response.status_code}")
        return None
        
    except Exception as e:
        log.error(f"felo.ai خطأ: {e}")
        return None


# ============================================================
# المزود 2: Pollinations.ai (احتياطي أول - مجاني مستقر)
# ============================================================

def generate_pollinations(prompt: str, timeout: int = 45) -> Optional[bytes]:
    """
    التوليد عبر Pollinations.ai
    - مجاني تماماً، لا يحتاج مفتاح
    - مستقر جداً
    """
    try:
        log.info(f"🎨 Pollinations: جاري توليد صورة...")
        
        # ترميز النص للرابط
        safe_prompt = urllib.parse.quote(prompt[:300], safe="")
        
        # عدة محاولات بأحجام مختلفة
        urls = [
            f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true&model=flux",
            f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true",
            f"https://image.pollinations.ai/prompt/{safe_prompt}?width=768&height=768&nologo=true",
        ]
        
        for i, url in enumerate(urls):
            for attempt in range(2):  # محاولتين لكل رابط
                try:
                    response = requests.get(url, timeout=timeout)
                    if response.status_code == 200 and "image" in response.headers.get("content-type", ""):
                        log.info(f"✅ Pollinations نجح (محاولة {i+1}.{attempt+1})")
                        return response.content
                    elif response.status_code in (502, 503, 504):
                        log.warning(f"Pollinations مشكلة مؤقتة {response.status_code}, انتظار...")
                        time.sleep(3)
                    else:
                        break
                except Exception as e:
                    log.warning(f"Pollinations محاولة {attempt+1} فشلت: {e}")
                    time.sleep(2)
        
        log.warning("Pollinations: جميع المحاولات فشلت")
        return None
        
    except Exception as e:
        log.error(f"Pollinations خطأ: {e}")
        return None


# ============================================================
# المزود 3: Gemini Flash Image (عبر مفتاح Gemini)
# ============================================================

def generate_gemini_flash(prompt: str, api_key: str, timeout: int = 60) -> Optional[bytes]:
    """
    التوليد عبر Gemini 2.0 Flash Image Generation
    - يحتاج مفتاح Gemini API
    - مجاني ضمن حدود Google
    """
    if not api_key:
        return None
        
    try:
        log.info(f"🎨 Gemini Flash: جاري توليد صورة...")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp-image-generation:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": f"Generate a high quality image of: {prompt}. Make it cinematic, detailed, 4K quality."}]
            }],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"],
                "temperature": 0.4,
                "candidateCount": 1
            }
        }
        
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=timeout)
        
        if response.status_code == 200:
            data = response.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                for part in data["candidates"][0]["content"]["parts"]:
                    if "inlineData" in part and part["inlineData"]["mimeType"].startswith("image/"):
                        log.info("✅ Gemini Flash نجح")
                        return base64.b64decode(part["inlineData"]["data"])
        
        log.warning(f"Gemini Flash فشل: {response.status_code}")
        return None
        
    except Exception as e:
        log.error(f"Gemini Flash خطأ: {e}")
        return None


# ============================================================
# المزود 4: SiliconFlow (إذا كان المفتاح موجوداً)
# ============================================================

def generate_siliconflow(prompt: str, api_key: str, timeout: int = 90) -> Optional[bytes]:
    """
    التوليد عبر SiliconFlow
    - يحتاج مفتاح API
    - جودة عالية، نماذج متعددة
    """
    if not api_key:
        return None
        
    try:
        log.info(f"🎨 SiliconFlow: جاري توليد صورة...")
        
        url = "https://api.siliconflow.cn/v1/images/generations"
        
        # قائمة النماذج المتاحة (مرتبة حسب الجودة)
        models = [
            "stabilityai/stable-diffusion-3-5-large",
            "black-forest-labs/FLUX.1-schnell",
            "deepseek-ai/Janus-Pro-7B",
            "stabilityai/stable-diffusion-xl-base-1.0"
        ]
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        for model in models:
            for attempt in range(2):
                try:
                    payload = {
                        "model": model,
                        "prompt": f"{prompt}, cinematic, high quality, 4K, masterpiece, detailed",
                        "negative_prompt": "blurry, distorted, ugly, text, watermark, low quality",
                        "size": "1024x1024",
                        "num_inference_steps": 25,
                        "guidance_scale": 7.0,
                        "num_images": 1
                    }
                    
                    response = requests.post(url, headers=headers, json=payload, timeout=timeout)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if "images" in data and len(data["images"]) > 0:
                            if "url" in data["images"][0]:
                                img_response = requests.get(data["images"][0]["url"], timeout=30)
                                if img_response.status_code == 200:
                                    log.info(f"✅ SiliconFlow نجح مع {model}")
                                    return img_response.content
                            elif "base64" in data["images"][0]:
                                return base64.b64decode(data["images"][0]["base64"])
                    elif response.status_code in (502, 503, 504):
                        time.sleep(3)
                        continue
                    else:
                        log.warning(f"SiliconFlow {model} فشل: {response.status_code}")
                        break
                        
                except Exception as e:
                    log.warning(f"SiliconFlow {model} محاولة {attempt+1}: {e}")
                    time.sleep(2)
        
        return None
        
    except Exception as e:
        log.error(f"SiliconFlow خطأ: {e}")
        return None


# ============================================================
# المزود 5: Replicate (محاولة بدون مفتاح)
# ============================================================

def generate_replicate_anonymous(prompt: str, timeout: int = 60) -> Optional[bytes]:
    """
    التوليد عبر Replicate (محاولة بدون مفتاح)
    - قد يعمل أحياناً، لكن غير مضمون
    - احتياطي أخير
    """
    try:
        log.info(f"🎨 Replicate: جاري محاولة توليد صورة...")
        
        # محاولة استخدام واجهة عامة
        url = "https://replicate.com/api/models/black-forest-labs/flux-schnell/predictions"
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        
        payload = {
            "input": {
                "prompt": prompt,
                "num_outputs": 1,
                "aspect_ratio": "1:1",
                "output_format": "png"
            }
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 201:
            data = response.json()
            if "urls" in data and "get" in data["urls"]:
                # انتظار اكتمال التوليد
                get_url = data["urls"]["get"]
                for _ in range(10):
                    time.sleep(3)
                    status_response = requests.get(get_url, timeout=30)
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        if status_data.get("status") == "succeeded":
                            if "output" in status_data and len(status_data["output"]) > 0:
                                img_response = requests.get(status_data["output"][0], timeout=30)
                                if img_response.status_code == 200:
                                    log.info("✅ Replicate نجح")
                                    return img_response.content
                        elif status_data.get("status") == "failed":
                            break
        
        return None
        
    except Exception as e:
        log.error(f"Replicate خطأ: {e}")
        return None


# ============================================================
# المولد الرئيسي (يجرب كل المزودين بالترتيب)
# ============================================================

class ImageGenerator:
    """
    الفئة الرئيسية لتوليد الصور
    - تجرب المزودين بالترتيب
    - تنتقل للتالي تلقائياً عند الفشل
    - تسجل النجاح والفشل
    """
    
    def __init__(self, gemini_api_key: str = "", siliconflow_api_key: str = ""):
        self.gemini_api_key = gemini_api_key
        self.siliconflow_api_key = siliconflow_api_key
        self.stats = {
            "felo": {"success": 0, "fail": 0},
            "pollinations": {"success": 0, "fail": 0},
            "gemini_flash": {"success": 0, "fail": 0},
            "siliconflow": {"success": 0, "fail": 0},
            "replicate": {"success": 0, "fail": 0}
        }
    
    def generate(self, prompt: str, max_attempts: int = 5) -> Optional[bytes]:
        """
        توليد صورة بتجربة كل المزودين بالترتيب
        """
        log.info(f"🎨 بدء توليد صورة: {prompt[:50]}...")
        
        # 1. felo.ai (الأفضل)
        log.info("1. محاولة felo.ai...")
        result = generate_felo(prompt)
        if result:
            self.stats["felo"]["success"] += 1
            log.info("✅ نجح مع felo.ai")
            return result
        self.stats["felo"]["fail"] += 1
        
        # 2. Pollinations.ai (احتياطي أول)
        log.info("2. محاولة Pollinations.ai...")
        result = generate_pollinations(prompt)
        if result:
            self.stats["pollinations"]["success"] += 1
            log.info("✅ نجح مع Pollinations.ai")
            return result
        self.stats["pollinations"]["fail"] += 1
        
        # 3. Gemini Flash Image (إذا كان المفتاح موجوداً)
        if self.gemini_api_key:
            log.info("3. محاولة Gemini Flash...")
            result = generate_gemini_flash(prompt, self.gemini_api_key)
            if result:
                self.stats["gemini_flash"]["success"] += 1
                log.info("✅ نجح مع Gemini Flash")
                return result
            self.stats["gemini_flash"]["fail"] += 1
        else:
            log.info("3. تخطي Gemini Flash (لا يوجد مفتاح)")
        
        # 4. SiliconFlow (إذا كان المفتاح موجوداً)
        if self.siliconflow_api_key:
            log.info("4. محاولة SiliconFlow...")
            result = generate_siliconflow(prompt, self.siliconflow_api_key)
            if result:
                self.stats["siliconflow"]["success"] += 1
                log.info("✅ نجح مع SiliconFlow")
                return result
            self.stats["siliconflow"]["fail"] += 1
        else:
            log.info("4. تخطي SiliconFlow (لا يوجد مفتاح)")
        
        # 5. Replicate (احتياطي أخير)
        log.info("5. محاولة Replicate...")
        result = generate_replicate_anonymous(prompt)
        if result:
            self.stats["replicate"]["success"] += 1
            log.info("✅ نجح مع Replicate")
            return result
        self.stats["replicate"]["fail"] += 1
        
        log.error("❌ جميع المزودين فشلوا!")
        return None
    
    def print_stats(self):
        """طباعة إحصائيات النجاح والفشل"""
        log.info("📊 إحصائيات المزودين:")
        for provider, stats in self.stats.items():
            total = stats["success"] + stats["fail"]
            if total > 0:
                rate = (stats["success"] / total) * 100
                log.info(f"  {provider}: نجاح {stats['success']}, فشل {stats['fail']} ({rate:.1f}%)")


# ============================================================
# دالة مساعدة للاستخدام السريع
# ============================================================

def generate_image(prompt: str, 
                   gemini_api_key: str = "", 
                   siliconflow_api_key: str = "") -> Optional[bytes]:
    """
    دالة سريعة لتوليد الصور (للاستخدام المباشر)
    """
    generator = ImageGenerator(gemini_api_key, siliconflow_api_key)
    return generator.generate(prompt)


# ============================================================
# اختبار سريع
# ============================================================

if __name__ == "__main__":
    # إعداد التسجيل للاختبار
    logging.basicConfig(level=logging.INFO)
    
    # اختبار مع صورة
    prompt = "a beautiful sunset over mountains, digital art"
    
    print(f"🎨 جاري توليد: {prompt}")
    
    # تجربة مع مفاتيح من البيئة (إذا كانت موجودة)
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    silicon_key = os.environ.get("SILICONFLOW_API_KEY", "")
    
    generator = ImageGenerator(gemini_key, silicon_key)
    result = generator.generate(prompt)
    
    if result:
        print(f"✅ تم توليد الصورة بنجاح! الحجم: {len(result)} بايت")
        # حفظ الصورة للاختبار
        with open("test_image.jpg", "wb") as f:
            f.write(result)
        print("💾 تم حفظ الصورة في test_image.jpg")
    else:
        print("❌ فشل توليد الصورة")
    
    generator.print_stats()
