#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weaver AI Engine - كامل مع دعم مفاتيح API متعددة (Fallback) + Gemma 4
"""

import os
import requests
import json
from datetime import datetime

# إعدادات Ollama / Local AI
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

# مفاتيح API متعددة مع ترتيب الأولوية
API_KEYS = [
    ("GROQ", os.environ.get("GROQ_API_KEY", "")),
    ("OPENAI", os.environ.get("OPENAI_API_KEY", "")),
    ("ANTHROPIC", os.environ.get("ANTHROPIC_API_KEY", "")),
    ("DEEPSEEK", os.environ.get("DEEPSEEK_API_KEY", "")),
    ("OLLAMA", os.environ.get("OLLAMA_API_KEY", "")),
]

# تصفية المفاتيح الفارغة
API_KEYS = [(name, key) for name, key in API_KEYS if key]
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

INTERPRETATION_STYLES = {
    "islamic": {
        "ar": "أنت مفسر أحلام إسلامي متخصص، تعتمد على منهج الإمام ابن سيرين والتراث الإسلامي.",
        "en": "You are an Islamic dream interpreter specializing in Ibn Sirin's methodology.",
        "fr": "Vous êtes un interprète de rêves islamique spécialisé dans la méthodologie d'Ibn Sirin.",
        "es": "Eres un intérprete de sueños islámico especializado en la metodología de Ibn Sirin.",
        "de": "Sie sind ein islamischer Traumdeuter, der auf die Methodik von Ibn Sirin spezialisiert ist.",
        "tr": "Ibn Sirin metodolojisinde uzmanlaşmış bir İslami rüya tabircisisiniz.",
        "ur": "آپ ابن سیرین کے طریقہ کار میں مہارت رکھنے والے اسلامی خوابوں کے معبر ہیں۔",
        "id": "Anda adalah penafsir mimpi Islam yang berspesialisasi dalam metodologi Ibn Sirin.",
        "ru": "Вы исламский толкователь снов, специализирующийся на методологии Ибн Сирина.",
        "zh": "您是专门研究伊本·西林方法的伊斯兰解梦师。"
    },
    "psychological": {
        "ar": "أنت معالج نفسي متخصص في تفسير الأحلام وفق نظريات فرويد ويونغ.",
        "en": "You are a psychologist specializing in dream analysis using Freud and Jung.",
        "fr": "Vous êtes un psychologue spécialisé dans l'analyse des rêves selon Freud et Jung.",
        "es": "Eres un psicólogo especializado en el análisis de los sueños según Freud y Jung.",
        "de": "Sie sind ein Psychologe, der auf Traumanalyse nach Freud und Jung spezialisiert ist.",
        "tr": "Freud ve Jung'a göre rüya analizi konusunda uzmanlaşmış bir psikologsunuz.",
        "ru": "Вы психолог, специализирующийся на анализе сновидений по Фрейду и Юнгу.",
        "zh": "您是专门根据弗洛伊德和荣格理论进行梦境分析的心理学家。"
    },
    "spiritual": {
        "ar": "أنت مرشد روحي يفسر الأحلام كرسائل من الكون والروح.",
        "en": "You are a spiritual guide interpreting dreams as messages from the universe and soul.",
        "fr": "Vous êtes un guide spirituel interprétant les rêves comme des messages de l'univers.",
        "es": "Eres un guía espiritual que interpreta los sueños como mensajes del universo."
    }
}

def call_groq(messages, model="llama3-70b-8192", max_tokens=1500):
    if not GROQ_API_KEY:
        return None
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": model, "messages": messages, "temperature": 0.7, "max_tokens": max_tokens},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq error: {e}")
    return None

def call_openai(messages, max_tokens=1500):
    if not OPENAI_API_KEY:
        return None
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            json={"model": "gpt-4o-mini", "messages": messages, "temperature": 0.7, "max_tokens": max_tokens},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"OpenAI error: {e}")
    return None

# ========== دوال API إضافية للمفاتيح المتعددة ==========

def call_groq_with_key(api_key, messages, model="llama3-70b-8192", max_tokens=1500):
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": messages, "temperature": 0.7, "max_tokens": max_tokens},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq error: {e}")
    return None

def call_openai_with_key(api_key, messages, max_tokens=1500):
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "gpt-4o-mini", "messages": messages, "temperature": 0.7, "max_tokens": max_tokens},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"OpenAI error: {e}")
    return None

def call_anthropic(api_key, messages, max_tokens=1500):
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": api_key, "Content-Type": "application/json", "anthropic-version": "2023-06-01"},
            json={"model": "claude-3-haiku-20240307", "max_tokens": max_tokens, "messages": messages},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["content"][0]["text"]
    except Exception as e:
        print(f"Anthropic error: {e}")
    return None

def call_deepseek(api_key, messages, max_tokens=1500):
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": messages, "temperature": 0.7, "max_tokens": max_tokens},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"DeepSeek error: {e}")
    return None

def call_ollama(api_key, messages, model="llama3", max_tokens=1500):
    """Ollama API (محلي)"""
    try:
        response = requests.post(
            f"{api_key}/api/generate",
            json={"model": model, "messages": messages, "stream": False},
            timeout=60
        )
        if response.status_code == 200:
            return response.json().get("message", {}).get("content", "")
    except Exception as e:
        print(f"Ollama error: {e}")
    return None

def interpret_dream(dream_text, style="islamic", language="ar"):
    style_config = INTERPRETATION_STYLES.get(style, INTERPRETATION_STYLES["general"])
    system_prompt = style_config.get(language, style_config["ar"])
    user_prompt = f"فسّر هذا الحلم بالتفصيل:\n\nالحلم: {dream_text}\n\nقدم التفسير بشكل منظم."
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
    
    # محاولة المفاتيح واحدة تلو الأخرى
    for api_name, api_key in API_KEYS:
        if not api_key:
            continue
        try:
            if api_name == "GROQ":
                result = call_groq_with_key(api_key, messages)
            elif api_name == "OPENAI":
                result = call_openai_with_key(api_key, messages)
            elif api_name == "ANTHROPIC":
                result = call_anthropic(api_key, messages)
            elif api_name == "DEEPSEEK":
                result = call_deepseek(api_key, messages)
            elif api_name == "OLLAMA":
                result = call_ollama(api_key, messages)
            
            if result:
                return result
        except Exception as e:
            print(f"{api_name} failed: {e}")
            continue
    
    return f"🌙 **تفسير حلمك:**\n\n{dream_text}\n\n⚠️ خدمة الذكاء الاصطناعي غير متاحة حالياً. حاول لاحقاً."

def generate_image_prompt(dream_text):
    messages = [{"role": "system", "content": "You create vivid image prompts for dreams."},
                {"role": "user", "content": f"Create an image prompt for: {dream_text}"}]
    result = call_groq(messages, max_tokens=200)
    if result:
        return result
    return f"Surreal dreamscape, {dream_text[:50]}, 4K"

def generate_blog_article(topic, language="ar"):
    if language == "ar":
        system = "أنت كاتب متخصص في تفسير الأحلام."
        user = f"اكتب مقالاً شاملاً عن: {topic} (600-800 كلمة)"
    else:
        system = "You are a dream interpretation writer."
        user = f"Write an article about: {topic}"
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    result = call_groq(messages, max_tokens=2000)
    if result:
        return result
    return f"<p>مقال عن: {topic}</p><p>المحتوى قيد التوليد...</p>"

def generate_dream_video(dream_text, language="ar"):
    """
    محاكاة توليد فيديو للأحلام باستخدام الذكاء الاصطناعي (Sora/Runway style)
    في هذه المرحلة، نقوم بتوليد السيناريو والروابط المطلوبة.
    """
    prompt = f"Create a cinematic video script for this dream: {dream_text}. Language: {language}"
    # سيتم ربط هذا لاحقاً بـ API لتوليد الفيديو مثل Replicate أو Runway
    return {
        "status": "processing",
        "script": prompt,
        "video_url": "https://aidreamweaver.store/static/videos/sample_dream.mp4",
        "voiceover": f"Generated voiceover in {language}"
    }


# ========== دوال Ollama / Gemma 4 ==========

def call_ollama_local(messages, model=None, max_tokens=1500):
    """استدعاء Ollama المحلي"""
    if model is None:
        model = OLLAMA_MODEL
    
    base_url = OLLAMA_BASE_URL.rstrip("/")
    
    try:
        # تحويل تنسيق الرسائل لـ Ollama
        ollama_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            if role == "system":
                ollama_messages.append({"role": "system", "content": msg["content"]})
            else:
                ollama_messages.append({"role": "user", "content": msg["content"]})
        
        response = requests.post(
            f"{base_url}/api/chat",
            json={
                "model": model,
                "messages": ollama_messages,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": max_tokens
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json().get("message", {}).get("content", "")
    except Exception as e:
        print(f"Ollama local error: {e}")
    return None


def check_ollama_status():
    """فحص حالة Ollama"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return {
                "status": "connected",
                "available_models": [m.get("name") for m in models],
                "current_model": OLLAMA_MODEL,
                "llama_available": any("llama" in m.get("name", "").lower() for m in models)
            }
    except:
        pass
    return {
        "status": "disconnected",
        "current_model": OLLAMA_MODEL,
        "llama_available": False
    }


def interpret_dream_local(dream_text, style="islamic", language="ar"):
    """تفسير الحلم باستخدام Ollama المحلي"""
    style_config = INTERPRETATION_STYLES.get(style, INTERPRETATION_STYLES["general"])
    system_prompt = style_config.get(language, style_config["ar"])
    
    if language == "ar":
        user_prompt = f"""الحلم: {dream_text}

قدم تفسيراً منظماً يتضمن:
1. التفسير الرمزي
2. الدلالات الروحانية والنفسية
3. النصائح العملية

أجب بالعربية الفصحى."""
    else:
        user_prompt = f"""Dream: {dream_text}

Provide an organized interpretation with:
1. Symbolic interpretation
2. Spiritual and psychological meanings
3. Practical advice."""
    
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
    result = call_ollama_local(messages, model=OLLAMA_MODEL, max_tokens=2000)
    
    if result:
        return result
    
    # Fallback إلى API التقليدية
    return interpret_dream(dream_text, style, language)
