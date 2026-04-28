#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weaver AI Engine - محرك الذكاء الاصطناعي
يدعم: Groq (Llama 4) + OpenAI fallback
"""

import os
import requests
import json
from datetime import datetime

# المفاتيح من المتغيرات البيئية
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# أنماط التفسير
INTERPRETATION_STYLES = {
    "islamic": {
        "ar": "أنت مفسر أحلام إسلامي متخصص، تعتمد على منهج الإمام ابن سيرين والتراث الإسلامي. فسّر الحلم بأسلوب علمي ديني، مع ذكر الرموز والدلالات من القرآن والسنة.",
        "en": "You are an Islamic dream interpreter specializing in Ibn Sirin's methodology. Interpret dreams using Islamic tradition, Quran and Sunnah references."
    },
    "psychological": {
        "ar": "أنت معالج نفسي متخصص في تفسير الأحلام وفق نظريات فرويد ويونغ. حلّل الحلم نفسياً مع ذكر الرموز اللاواعية والدلالات النفسية.",
        "en": "You are a psychologist specializing in dream analysis using Freud and Jung theories. Analyze the dream psychologically."
    },
    "ancient": {
        "ar": "أنت خبير في الحضارات القديمة (مصر، بابل، اليونان). فسّر الحلم وفق رموز ودلالات الحضارات القديمة.",
        "en": "You are an expert in ancient civilizations (Egypt, Babylon, Greece). Interpret dreams using ancient symbolism."
    },
    "general": {
        "ar": "أنت مفسر أحلام شامل يجمع بين التراث الإسلامي والعلم النفسي والحضارات القديمة. قدّم تفسيراً متكاملاً.",
        "en": "You are a comprehensive dream interpreter combining Islamic tradition, psychology, and ancient civilizations."
    }
}

def call_groq(messages: list, model: str = "llama3-70b-8192", max_tokens: int = 1500) -> str:
    """استدعاء Groq API"""
    if not GROQ_API_KEY:
        return None
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": max_tokens
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"⚠️ Groq error: {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        print(f"⚠️ Groq exception: {e}")
        return None

def call_openai(messages: list, max_tokens: int = 1500) -> str:
    """استدعاء OpenAI API كبديل"""
    if not OPENAI_API_KEY:
        return None
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": max_tokens
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return None
    except Exception as e:
        print(f"⚠️ OpenAI exception: {e}")
        return None

def interpret_dream(dream_text: str, style: str = "islamic", language: str = "ar") -> str:
    """
    تفسير الحلم بالذكاء الاصطناعي
    يدعم: عربي/إنجليزي، أنماط متعددة
    """
    style_config = INTERPRETATION_STYLES.get(style, INTERPRETATION_STYLES["general"])
    system_prompt = style_config.get(language, style_config["ar"])

    if language == "ar":
        user_prompt = f"""فسّر هذا الحلم بالتفصيل:

الحلم: {dream_text}

قدّم التفسير بالتنسيق التالي:
🌙 **التفسير العام:**
[التفسير الشامل]

🔮 **الرموز الرئيسية:**
[رمز 1]: [معناه]
[رمز 2]: [معناه]

💡 **الدلالة والرسالة:**
[ما يريد الحلم إيصاله]

✨ **النصيحة:**
[توجيه عملي للرائي]"""
    else:
        user_prompt = f"""Interpret this dream in detail:

Dream: {dream_text}

Format:
🌙 **General Interpretation:**
[comprehensive interpretation]

🔮 **Key Symbols:**
[symbol 1]: [meaning]
[symbol 2]: [meaning]

💡 **Message & Significance:**
[what the dream conveys]

✨ **Advice:**
[practical guidance]"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    # محاولة Groq أولاً
    result = call_groq(messages, model="llama3-70b-8192")
    if result:
        return result

    # بديل: OpenAI
    result = call_openai(messages)
    if result:
        return result

    # نص افتراضي
    if language == "ar":
        return f"""🌙 **تفسير حلمك:**

حلمك يحمل رموزاً مهمة. {dream_text[:100]}...

🔮 **الرموز:**
تشير الرموز في حلمك إلى تحولات في حياتك الداخلية.

💡 **الرسالة:**
الحلم يعكس مشاعرك وأفكارك الداخلية.

✨ **النصيحة:**
تأمل في ما يشغل بالك، فالأحلام مرآة الروح.

⚠️ *ملاحظة: خدمة الذكاء الاصطناعي مؤقتاً غير متاحة. يرجى المحاولة لاحقاً.*"""
    else:
        return f"Dream interpretation temporarily unavailable. Please try again later."

def generate_image_prompt(dream_text: str) -> str:
    """توليد prompt لصورة الحلم"""
    messages = [
        {"role": "system", "content": "You are an expert at creating image generation prompts. Create a vivid, artistic prompt for the dream described. Make it suitable for AI image generation. Keep it under 100 words."},
        {"role": "user", "content": f"Create an image generation prompt for this dream: {dream_text}"}
    ]
    result = call_groq(messages, model="llama3-70b-8192", max_tokens=200)
    if result:
        return result
    return f"Surreal dreamscape, {dream_text[:50]}, ethereal lighting, mystical atmosphere, 4K, artistic"

def generate_blog_article(topic: str, language: str = "ar") -> str:
    """توليد مقال مدونة كامل"""
    if language == "ar":
        system = "أنت كاتب متخصص في تفسير الأحلام والحضارات القديمة. اكتب مقالات شيقة وعميقة بالعربية الفصحى."
        user_prompt = f"""اكتب مقالاً شاملاً عن: {topic}

المقال يجب أن يتضمن:
1. مقدمة جذابة
2. عناوين فرعية واضحة
3. معلومات تاريخية وثقافية
4. أمثلة عملية
5. خاتمة مفيدة

الطول: 600-800 كلمة
الأسلوب: علمي شيق، مناسب للقراء العرب"""
    else:
        system = "You are a writer specializing in dream interpretation and ancient civilizations."
        user_prompt = f"Write a comprehensive article about: {topic}. Include introduction, subheadings, historical info, practical examples, and conclusion. 600-800 words."

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_prompt}
    ]

    result = call_groq(messages, model="llama3-70b-8192", max_tokens=2000)
    if result:
        return result
    result = call_openai(messages, max_tokens=2000)
    if result:
        return result
    return f"<p>مقال عن: {topic}</p><p>المحتوى قيد التوليد...</p>"

def generate_marketing_post(topic: str, platform: str = "general") -> str:
    """توليد منشور تسويقي"""
    platform_instructions = {
        "twitter": "منشور قصير لا يتجاوز 280 حرفاً، مع هاشتاقات مناسبة",
        "instagram": "منشور جذاب مع إيموجي ووصف بصري، 150-200 كلمة",
        "facebook": "منشور متوسط الطول مع سؤال تفاعلي، 100-150 كلمة",
        "telegram": "منشور مفصل مع روابط، 200-300 كلمة",
        "general": "منشور متوازن مناسب لجميع المنصات"
    }

    instruction = platform_instructions.get(platform, platform_instructions["general"])

    messages = [
        {"role": "system", "content": f"أنت خبير تسويق رقمي. اكتب منشوراً تسويقياً لمنصة Weaver (نَسَّاج) لتفسير الأحلام. {instruction}"},
        {"role": "user", "content": f"اكتب منشوراً عن: {topic}\nالرابط: https://aidreamweaver.store"}
    ]

    result = call_groq(messages, model="llama3-70b-8192", max_tokens=500)
    if result:
        return result
    return f"🌙 {topic}\n\nاكتشف تفسير أحلامك بالذكاء الاصطناعي!\n🔗 https://aidreamweaver.store"

# للاختبار
if __name__ == "__main__":
    print("🧪 اختبار محرك الذكاء الاصطناعي...")
    result = interpret_dream("رأيت في المنام أنني أطير فوق البحر")
    print(result[:200])
