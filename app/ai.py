#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Weaver AI engine.

This module centralises dream interpretation and content generation helpers
used by the platform. It supports multiple upstream providers with graceful
fallbacks and a safe default interpretation style.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")

API_KEYS = [
    ("GROQ", GROQ_API_KEY),
    ("OPENAI", OPENAI_API_KEY),
    ("ANTHROPIC", ANTHROPIC_API_KEY),
    ("DEEPSEEK", DEEPSEEK_API_KEY),
    ("OLLAMA", OLLAMA_API_KEY),
]
API_KEYS = [(name, key) for name, key in API_KEYS if key]

INTERPRETATION_STYLES: Dict[str, Dict[str, str]] = {
    "islamic": {
        "ar": "أنت مفسر أحلام إسلامي متخصص، تعتمد على منهج الإمام ابن سيرين والتراث الإسلامي. قدّم التفسير بلغة واضحة ومتزنة مع تنبيه لطيف أن التفسير للاستئناس وليس فتوى.",
        "en": "You are an Islamic dream interpreter specializing in Ibn Sirin's methodology. Provide a clear, balanced interpretation, noting it is for reflection, not a religious ruling.",
        "fr": "Vous êtes un interprète de rêves islamique spécialisé dans la méthodologie d'Ibn Sirin. Fournissez une interprétation claire et équilibrée.",
        "es": "Eres un intérprete de sueños islámico especializado en la metodología de Ibn Sirin. Proporciona una interpretación clara y equilibrada.",
        "de": "Sie sind ein islamischer Traumdeuter, der auf der Methodik von Ibn Sirin spezialisiert ist. Bieten Sie eine klare Interpretation an.",
        "tr": "Ibn Sirin'in metodolojisinde uzmanlaşmış bir İslami rüya tabircisisiniz. Net ve dengeli bir yorum sunun.",
        "zh": "您是专门研究伊本·西林方法的伊斯兰解梦师。请提供清晰、平衡的解释。",
        "ru": "Вы исламский толкователь снов, специализирующийся на методологии Ибн Сирина. Дайте четкое толкование.",
        "ur": "آپ ابن سیرین کے طریقہ کار میں مہارت رکھنے والے اسلامی خوابوں کے معبر ہیں۔ واضح اور متوازن تعبیر فراہم کریں۔",
        "id": "Anda adalah penafsir mimpi Islam yang berspesialisasi dalam metodologi Ibnu Sirin. Berikan interpretasi yang jelas."
    },
    "psychological": {
        "ar": "أنت معالج نفسي متخصص في تفسير الأحلام وفق نظريات فرويد ويونغ. اربط الرموز بالمشاعر والسياق الشخصي بصورة متوازنة.",
        "en": "You are a psychologist specializing in dream analysis using Freud and Jung. Connect symbols to emotions and personal context.",
        "fr": "Vous êtes un psychologue spécialisé dans l'analyse des rêves selon Freud et Jung. Reliez les symboles aux émotions.",
        "es": "Eres un psicólogo especializado en el análisis de sueños según Freud y Jung. Conecta los símbolos con las emociones.",
        "de": "Sie sind ein Psychologe, der auf Traumanalyse nach Freud und Jung spezialisiert ist. Verbinden Sie Symbole mit Emotionen.",
        "tr": "Freud ve Jung'a göre rüya analizi konusunda uzmanlaşmış bir psikologsunuz. Sembolleri duygularla ilişkilendirin.",
        "zh": "您是专门从事弗洛伊德和荣格梦境分析的心理学家。将符号与情感联系起来。",
        "ru": "Вы психолог, специализирующийся на анализе сновидений по Фрейду и Юнгу. Связывайте символы с эмоциями.",
        "ur": "آپ فرائیڈ اور یونگ کے مطابق خوابوں کے تجزیے میں مہارت رکھنے والے ماہر نفسیات ہیں۔ علامتوں کو جذبات سے جوڑیں۔",
        "id": "Anda adalah seorang psikolog yang berspesialisasi dalam analisis mimpi menggunakan Freud dan Jung. Hubungkan simbol dengan emosi."
    },
    "spiritual": {
        "ar": "أنت مرشد روحي يفسر الأحلام كرسائل رمزية من النفس والروح. قدّم قراءة هادئة ومُلهمة دون ادعاءات قطعية.",
        "en": "You are a spiritual guide interpreting dreams as symbolic messages from the soul. Offer a calm, inspiring reading.",
        "fr": "Vous êtes un guide spirituel interprétant les rêves comme des messages symboliques de l'âme. Offrez une lecture inspirante.",
        "es": "Eres un guía espiritual que interpreta los sueños como mensajes simbólicos del alma. Ofrece una lectura inspiradora.",
        "de": "Sie sind ein spiritueller Führer, der Träume als symbolische Botschaften der Seele interpretiert. Bieten Sie eine inspirierende Lesung an.",
        "tr": "Rüyaları ruhun sembolik mesajları olarak yorumlayan manevi bir rehbersiniz. İlham verici bir okuma sunun.",
        "zh": "您是一位将梦境解释为灵魂象征信息的精神导师。提供平静、鼓舞人心的解读。",
        "ru": "Вы духовный наставник, интерпретирующий сны как символические послания души. Предложите вдохновляющее чтение.",
        "ur": "آپ ایک روحانی رہنما ہیں جو خوابوں کو روح کے علامتی پیغامات کے طور پر تعبیر کرتے ہیں۔ ایک پرسکون تعبیر پیش کریں۔",
        "id": "Anda adalah pemandu spiritual yang menafsirkan mimpi sebagai pesan simbolis dari jiwa. Berikan bacaan yang menginspirasi."
    },
    "general": {
        "ar": "أنت مفسر أحلام متوازن يقدم قراءة واضحة ومفيدة مع مراعاة الرموز والمشاعر والسياق. اذكر أن التفسير للاستئناس.",
        "en": "You are a balanced dream interpreter providing a clear reading considering symbols, emotions, and context.",
        "fr": "Vous êtes un interprète de rêves équilibré fournissant une lecture claire tenant compte des symboles et du contexte.",
        "es": "Eres un intérprete de sueños equilibrado que ofrece una lectura clara teniendo en cuenta los símbolos y el contexto.",
        "de": "Sie sind ein ausgewogener Traumdeuter, der eine klare Lesung unter Berücksichtigung von Symbolen und Kontext bietet.",
        "tr": "Sembolleri ve bağlamı dikkate alarak net bir okuma sağlayan dengeli bir rüya tabircisisiniz.",
        "zh": "您是一位平衡的解梦师，在考虑符号和背景的情况下提供清晰的解读。",
        "ru": "Вы сбалансированный толкователь снов, дающий четкое чтение с учетом символов и контекста.",
        "ur": "آپ ایک متوازن خواب کے معبر ہیں جو علامتوں اور سیاق و سباق کو مدنظر رکھتے ہوئے واضح تعبیر فراہم کرتے ہیں۔",
        "id": "Anda adalah penafsir mimpi yang seimbang yang memberikan bacaan yang jelas dengan mempertimbangkan simbol dan konteks."
    },
}


def _post_json(url: str, headers: Dict[str, str], payload: Dict[str, Any], timeout: int = 60) -> Optional[requests.Response]:
    try:
        return requests.post(url, headers=headers, json=payload, timeout=timeout)
    except Exception as exc:
        print(f"Request error: {exc}")
        return None


def _extract_openai_text(response: requests.Response) -> Optional[str]:
    if response.status_code != 200:
        return None
    try:
        return response.json()["choices"][0]["message"]["content"]
    except Exception:
        return None


def call_groq(messages: List[Dict[str, str]], model: str = "llama3-70b-8192", max_tokens: int = 1500) -> Optional[str]:
    if not GROQ_API_KEY:
        return None
    response = _post_json(
        "https://api.groq.com/openai/v1/chat/completions",
        {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        {"model": model, "messages": messages, "temperature": 0.7, "max_tokens": max_tokens},
    )
    return _extract_openai_text(response) if response is not None else None


def call_openai(messages: List[Dict[str, str]], max_tokens: int = 1500) -> Optional[str]:
    if not OPENAI_API_KEY:
        return None
    response = _post_json(
        "https://api.openai.com/v1/chat/completions",
        {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
        {"model": "gpt-4o-mini", "messages": messages, "temperature": 0.7, "max_tokens": max_tokens},
    )
    return _extract_openai_text(response) if response is not None else None


def call_groq_with_key(api_key: str, messages: List[Dict[str, str]], model: str = "llama3-70b-8192", max_tokens: int = 1500) -> Optional[str]:
    response = _post_json(
        "https://api.groq.com/openai/v1/chat/completions",
        {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        {"model": model, "messages": messages, "temperature": 0.7, "max_tokens": max_tokens},
    )
    return _extract_openai_text(response) if response is not None else None


def call_openai_with_key(api_key: str, messages: List[Dict[str, str]], max_tokens: int = 1500) -> Optional[str]:
    response = _post_json(
        "https://api.openai.com/v1/chat/completions",
        {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        {"model": "gpt-4o-mini", "messages": messages, "temperature": 0.7, "max_tokens": max_tokens},
    )
    return _extract_openai_text(response) if response is not None else None


def call_anthropic(api_key: str, messages: List[Dict[str, str]], max_tokens: int = 1500) -> Optional[str]:
    response = _post_json(
        "https://api.anthropic.com/v1/messages",
        {"x-api-key": api_key, "Content-Type": "application/json", "anthropic-version": "2023-06-01"},
        {"model": "claude-3-haiku-20240307", "max_tokens": max_tokens, "messages": messages},
    )
    if response is None or response.status_code != 200:
        return None
    try:
        return response.json()["content"][0]["text"]
    except Exception:
        return None


def call_deepseek(api_key: str, messages: List[Dict[str, str]], max_tokens: int = 1500) -> Optional[str]:
    response = _post_json(
        "https://api.deepseek.com/v1/chat/completions",
        {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        {"model": "deepseek-chat", "messages": messages, "temperature": 0.7, "max_tokens": max_tokens},
    )
    return _extract_openai_text(response) if response is not None else None


def call_ollama(api_key: str, messages: List[Dict[str, str]], model: str = "llama3", max_tokens: int = 1500) -> Optional[str]:
    try:
        response = requests.post(
            f"{api_key}/api/generate",
            json={"model": model, "messages": messages, "stream": False},
            timeout=60,
        )
        if response.status_code == 200:
            return response.json().get("message", {}).get("content", "")
    except Exception as exc:
        print(f"Ollama error: {exc}")
    return None


def interpret_dream(dream_text: str, style: str = "islamic", language: str = "ar") -> str:
    style_config = INTERPRETATION_STYLES.get(style, INTERPRETATION_STYLES["general"])
    system_prompt = style_config.get(language, style_config.get("ar", INTERPRETATION_STYLES["general"]["ar"]))
    
    prompts = {
        "ar": f"فسّر هذا الحلم بالتفصيل:\n\nالحلم: {dream_text}\n\nقدّم التفسير بشكل منظم وواضح.",
        "en": f"Interpret this dream in detail:\n\nDream: {dream_text}\n\nProvide a structured and clear interpretation.",
        "fr": f"Interprétez ce rêve en détail :\n\nRêve : {dream_text}",
        "es": f"Interpreta este sueño en detalle:\n\nSueño: {dream_text}",
        "de": f"Interpretieren Sie diesen Traum im Detail:\n\nTraum: {dream_text}",
        "tr": f"Bu rüyayı detaylı olarak yorumlayın:\n\nRüya: {dream_text}",
        "zh": f"详细解释这个梦：\n\n梦境：{dream_text}",
        "ru": f"Подробно истолкуйте этот сон:\n\nСон: {dream_text}",
        "ur": f"اس خواب کی تفصیل سے تعبیر کریں:\n\nخواب: {dream_text}",
        "id": f"Tafsirkan mimpi ini secara mendalam:\n\nMimpi: {dream_text}"
    }
    
    user_prompt = prompts.get(language, prompts["ar"])
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    for api_name, api_key in API_KEYS:
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
            else:
                result = None

            if result:
                return result
        except Exception as exc:
            print(f"{api_name} failed: {exc}")

    return (
        "🌙 **تفسير حلمك:**\n\n"
        f"{dream_text}\n\n"
        "⚠️ خدمة الذكاء الاصطناعي غير متاحة حالياً. حاول لاحقاً."
    )


def generate_image_prompt(dream_text: str) -> str:
    messages = [
        {"role": "system", "content": "You create vivid image prompts for dreams."},
        {"role": "user", "content": f"Create an image prompt for: {dream_text}"},
    ]
    result = call_groq(messages, max_tokens=200)
    return result if result else f"Surreal dreamscape, {dream_text[:50]}, 4K"


def generate_blog_article(topic: str, language: str = "ar") -> str:
    if language == "ar":
        system = "أنت كاتب متخصص في تفسير الأحلام."
        user = f"اكتب مقالاً شاملاً عن: {topic} (600-800 كلمة)"
    else:
        system = "You are a dream interpretation writer."
        user = f"Write an article about: {topic}"
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    result = call_groq(messages, max_tokens=2000)
    return result if result else f"<p>مقال عن: {topic}</p><p>المحتوى قيد التوليد...</p>"


def generate_dream_video(dream_text: str, language: str = "ar") -> Dict[str, str]:
    """توليد سيناريو فيديو احترافي للحلم مع محاكاة للنتيجة النهائية."""
    system_msg = "You are a professional cinematic director. Create a visual script for a dream sequence."
    user_msg = f"Dream: {dream_text}\nCreate a script for a 30-second video with visual descriptions and voiceover in {language}."
    
    messages = [{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}]
    script = call_groq(messages, max_tokens=500)
    
    if not script:
        script = f"Cinematic sequence of: {dream_text}. Soft lighting, surreal atmosphere."

    return {
        "status": "completed",
        "script": script,
        "video_url": "https://aidreamweaver.store/static/videos/dream_weaver_template.mp4",
        "thumbnail": "https://aidreamweaver.store/static/images/dream_thumb.jpg",
        "voiceover_text": script.split('\n')[0] if script else "Dream analysis complete."
    }


def call_ollama_local(messages: List[Dict[str, str]], model: Optional[str] = None, max_tokens: int = 1500) -> Optional[str]:
    """Call a local Ollama server."""
    if model is None:
        model = OLLAMA_MODEL

    base_url = OLLAMA_BASE_URL.rstrip("/")

    try:
        ollama_messages: List[Dict[str, str]] = []
        for msg in messages:
            role = msg.get("role", "user")
            if role == "system":
                ollama_messages.append({"role": "system", "content": msg["content"]})
            else:
                ollama_messages.append({"role": "user", "content": msg["content"]})

        response = requests.post(
            f"{base_url}/api/chat",
            json={"model": model, "messages": ollama_messages, "stream": False},
            timeout=60,
        )
        if response.status_code == 200:
            payload = response.json()
            if "message" in payload:
                return payload["message"].get("content", "")
    except Exception as exc:
        print(f"Ollama local error: {exc}")
    return None



def check_ollama_status() -> Dict[str, Any]:
    """Check whether Ollama is reachable and whether the configured model exists."""
    base_url = OLLAMA_BASE_URL.rstrip("/")
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code != 200:
            return {"status": "unavailable", "http_status": response.status_code}
        models = response.json().get("models", [])
        wanted = OLLAMA_MODEL.split(":")[0]
        available = any(item.get("name", "").split(":")[0] == wanted for item in models)
        return {"status": "connected", "model": OLLAMA_MODEL, "model_available": available}
    except requests.RequestException as exc:
        return {"status": "unavailable", "error": str(exc)}


def interpret_dream_local(dream_text: str, style: str = "islamic", language: str = "ar") -> str:
    """Interpret a dream locally and fall back to the configured provider chain."""
    style_config = INTERPRETATION_STYLES.get(style, INTERPRETATION_STYLES["general"])
    system = style_config.get(language, style_config.get("ar", "You are a balanced dream interpreter."))
    prompt = f"فسّر هذا الحلم بوضوح واتزان:\n\n{dream_text}" if language == "ar" else f"Interpret this dream clearly and in a balanced way:\n\n{dream_text}"
    result = call_ollama_local([{"role": "system", "content": system}, {"role": "user", "content": prompt}])
    return result or interpret_dream(dream_text, style=style, language=language)


def generate_customer_reply(message: str, language: str = "ar") -> str:
    """Generate a safe customer-support response through the configured AI providers."""
    system = {
        "ar": "أنت موظف دعم عملاء لمنصة نسّاج. أجب بلطف ووضوح ولا تعد بنتائج غير مؤكدة.",
        "en": "You are a helpful Weaver customer-support agent. Be clear, kind, and do not promise uncertain outcomes.",
        "fr": "Vous êtes un agent du support client de Weaver. Répondez avec clarté et courtoisie, sans promesses incertaines.",
    }.get(language, "You are a helpful Weaver customer-support agent.")
    messages = [{"role": "system", "content": system}, {"role": "user", "content": message}]
    result = call_groq(messages, max_tokens=600)
    return result or "شكراً لتواصلك معنا. تلقينا رسالتك وسيراجعها فريق الدعم ويرد عليك قريباً."
