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

    response = requests.post(API_URL, headers=headers, json=payload)

    result = response.json()

    try:
        interpretation = result[0]["generated_text"]
    except:
        interpretation = "Dream analysis is currently unavailable."

    return interpretation
