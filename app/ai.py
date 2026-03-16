import os
import requests
import logging

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

def interpret_dream(dream_text):
    """
    تفسير الحلم باستخدام Gemini API
    """
    log.info(f"🔑 GEMINI_API_KEY موجود: {'نعم' if GEMINI_API_KEY else 'لا'}")
    
    if not GEMINI_API_KEY:
        return "❌ خطأ: مفتاح Gemini غير موجود في المتغيرات البيئية"
    
    # نموذج 1.5 فلاش (أسرع وأكثر استقراراً)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # النص اللي نرسله لـ Gemini
    prompt = f"""فسر هذا الحلم بالعربية:
    
الحلم: {dream_text}

اكتب تفسيراً بسيطاً ومنظمًا يتضمن:
1. المعنى العام
2. الرموز المهمة
3. نصيحة للحالم
"""
    
    try:
        # إرسال الطلب لـ Gemini
        response = requests.post(
            url,
            json={
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        log.info(f"📡 رمز الاستجابة من Gemini: {response.status_code}")
        
        # إذا نجح الطلب
        if response.status_code == 200:
            data = response.json()
            try:
                interpretation = data["candidates"][0]["content"]["parts"][0]["text"]
                return interpretation.strip()
            except (KeyError, IndexError) as e:
                log.error(f"خطأ في تحليل استجابة Gemini: {e}")
                return "❌ خطأ في قراءة استجابة Gemini"
        
        # إذا فشل الطلب بسبب الحد اليومي
        elif response.status_code == 429:
            log.warning("⚠️ تم تجاوز الحد اليومي لـ Gemini")
            return "⚠️ تم تجاوز الحد اليومي لـ Gemini. انتظر قليلاً أو جرب مفتاح آخر."
        
        # أي خطأ آخر
        else:
            log.error(f"❌ خطأ من Gemini: {response.status_code} - {response.text[:200]}")
            return f"❌ خطأ في الاتصال بـ Gemini (الرمز: {response.status_code})"
    
    except requests.exceptions.Timeout:
        log.error("⏱️ انتهت مهلة الاتصال بـ Gemini")
        return "❌ انتهت مهلة الاتصال. حاول مرة أخرى."
    
    except requests.exceptions.ConnectionError:
        log.error("🔌 فشل الاتصال بـ Gemini")
        return "❌ فشل الاتصال بالإنترنت. تحقق من اتصال السيرفر."
    
    except Exception as e:
        log.error(f"💥 خطأ غير متوقع: {e}")
        return f"❌ حدث خطأ غير متوقع: {str(e)[:100]}"

# دالة للاختبار السريع (لو شغلت الملف مباشرة)
if __name__ == "__main__":
    test_dream = "حلمت أنني أطير فوق البحر"
    print(interpret_dream(test_dream))
