import requests

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"

headers = {
    "Content-Type": "application/json"
}

def analyze_dream_with_ai(dream_text):

    prompt = f"""
You are an expert dream interpreter.

Analyze the following dream and explain its psychological meaning
and possible symbolic interpretation.

Dream:
{dream_text}

Interpretation:
"""

    payload = {
        "inputs": prompt
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    result = response.json()

    try:
        interpretation = result[0]["generated_text"]
    except:
        interpretation = "AI could not analyze the dream right now."

    return interpretation
