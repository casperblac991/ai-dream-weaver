import requests

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"

headers = {
    "Content-Type": "application/json"
}


def analyze_dream_with_ai(dream_text):

    prompt = f"""
You are a professional dream psychologist.

Analyze the dream below and provide:

1. Dream Meaning
2. Dream Symbols
3. Psychological Insight
4. Advice

Dream:
{dream_text}

Response:
"""

    payload = {
        "inputs": prompt
    }

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            return "AI service is temporarily unavailable."

        result = response.json()

        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]

        return "Dream analysis is currently unavailable."

    except Exception as e:
        print("AI Error:", e)
        return "AI service error. Please try again later."
