import os
from groq import Groq

# مفتاح Groq (من Environment)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# إذا ما كان في Environment، استخدم المفتاح مباشرة للاختبار
if not GROQ_API_KEY:
    GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

def interpret_dream(dream_text):
    """
    تفسير الحلم باستخدام Groq (Llama 4)
    """
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",  # أو أي نموذج متوفر
            messages=[
                {"role": "system", "content": "أنت مفسر أحلام خبير. قدم تفسيرًا عميقًا ومنظمًا بالعربية."},
                {"role": "user", "content": f"الحلم: {dream_text}"}
            ],
            temperature=0.7,
            max_tokens=1024
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

# للاختبار السريع
if __name__ == "__main__":
    print(interpret_dream("حلمت أنني أطير فوق البحر"))
