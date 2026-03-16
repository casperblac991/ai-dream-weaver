import os
from groq import Groq

# مفتاح Groq من Environment
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# إنشاء client
client = Groq(api_key=GROQ_API_KEY)

def interpret_dream(dream_text):
    """
    تفسير الحلم باستخدام Groq (Llama 4)
    يرد بنفس لغة المستخدم
    """
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": "Interpret the dream in the same language the user wrote it."},
                {"role": "user", "content": dream_text}
            ],
            temperature=0.7,
            max_tokens=1024
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

# للاختبار السريع
if __name__ == "__main__":
    print(interpret_dream("I was flying over the ocean"))
