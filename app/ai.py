import os
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

def interpret_dream(dream_text):
    if not GEMINI_API_KEY:
        return "❌ مفتاح Gemini غير موجود"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""فسر هذا الحلم بالعربية بشكل عميق ومنظم:
    
الحلم: {dream_text}

اكتب تفسيراً يشمل:
1. المعنى العام
2. الرموز الرئيسية
3. رسالة للحالم
4. نصيحة عملية"""
    
    try:
        r = requests.post(url, json={
            "contents": [{"parts": [{"text": prompt}]}]
        }, timeout=30)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return "❌ خطأ في الاتصال"
    except:
        return "❌ فشل الاتصال"
