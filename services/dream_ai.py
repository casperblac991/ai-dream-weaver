import os
import requests


def analyze_dream_with_ai(dream_text):

    api_key = os.getenv("GEMINI_API_KEY")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"

    prompt = f"""
Interpret this dream psychologically and symbolically.

Dream:
{dream_text}

Explain the possible meaning and emotions behind it.
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(url, json=payload)

    try:
        result = response.json()
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        return text
    except:
        return "Dream interpretation unavailable."
