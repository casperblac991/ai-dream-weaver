#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weaver AI Engine - كامل (يدعم Groq و OpenAI)
"""

import os
import requests
import json
from datetime import datetime

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

INTERPRETATION_STYLES = {
    "islamic": {
        "ar": "أنت مفسر أحلام إسلامي متخصص، تعتمد على منهج الإمام ابن سيرين والتراث الإسلامي. فسّر الحلم بأسلوب علمي ديني، مع ذكر الرموز والدلالات من القرآن والسنة.",
        "en": "You are an Islamic dream interpreter specializing in Ibn Sirin's methodology."
    },
    "psychological": {
        "ar": "أنت معالج نفسي متخصص في تفسير الأحلام وفق نظريات فرويد ويونغ.",
        "en": "You are a psychologist specializing in dream analysis using Freud and Jung."
    },
    "ancient": {
        "ar": "أنت خبير في الحضارات القديمة (مصر، بابل، اليونان). فسّر الحلم وفق رموزها.",
        "en": "You are an expert in ancient civilizations."
    },
    "general": {
        "ar": "أنت مفسر أحلام شامل يجمع بين التراث الإسلامي والعلم النفسي والحضارات القديمة.",
        "en": "You are a comprehensive dream interpreter."
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

def interpret_dream(dream_text, style="islamic", language="ar"):
    style_config = INTERPRETATION_STYLES.get(style, INTERPRETATION_STYLES["general"])
    system_prompt = style_config.get(language, style_config["ar"])
    user_prompt = f"فسّر هذا الحلم بالتفصيل:\n\nالحلم: {dream_text}\n\nقدم التفسير بشكل منظم."
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
    result = call_groq(messages)
    if result:
        return result
    result = call_openai(messages)
    if result:
        return result
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
