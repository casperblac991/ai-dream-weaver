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
        "en": "You are an Islamic dream interpreter specializing in Ibn Sirin's methodology. Keep the interpretation clear, balanced, and note that it is for reflection rather than a religious ruling.",
    },
    "psychological": {
        "ar": "أنت معالج نفسي متخصص في تفسير الأحلام وفق نظريات فرويد ويونغ. اربط الرموز بالمشاعر والسياق الشخصي بصورة متوازنة.",
        "en": "You are a psychologist specializing in dream analysis using Freud and Jung. Connect symbols to emotions and personal context in a balanced way.",
    },
    "spiritual": {
        "ar": "أنت مرشد روحي يفسر الأحلام كرسائل رمزية من النفس والروح. قدّم قراءة هادئة ومُلهمة دون ادعاءات قطعية.",
        "en": "You are a spiritual guide interpreting dreams as symbolic messages from the self and the soul. Offer a calm, inspiring reading without absolute claims.",
    },
    "general": {
        "ar": "أنت مفسر أحلام متوازن يقدم قراءة واضحة ومفيدة مع مراعاة الرموز والمشاعر والسياق. اذكر أن التفسير للاستئناس.",
        "en": "You are a balanced dream interpreter who gives a clear, useful reading while considering symbols, emotions, and context. Mention that the interpretation is for reflection.",
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
    user_prompt = f"فسّر هذا الحلم بالتفصيل:\n\nالحلم: {dream_text}\n\nقدّم التفسير بشكل منظم وواضح."
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
    prompt = f"Create a cinematic video script for this dream: {dream_text}. Language: {language}"
    return {
        "status": "processing",
        "script": prompt,
        "video_url": "https://aidreamweaver.store/static/videos/sample_dream.mp4",
        "voiceover": f"Generated voiceover in {language}",
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
