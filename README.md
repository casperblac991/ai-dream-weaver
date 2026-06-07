# Weaver | نَسَّاج - منصة تفسير الأحلام بالذكاء الاصطناعي

الموقع: https://aidreamweaver.store

## الميزات
- تفسير AI بأسلوب ابن سيرين (Groq + Llama 4)
- **Ollama محلي** - تشغيل مجاني بدون API (8GB RAM)
- توليد صور 4K للأحلام
- مدونة يومية تلقائية بالذكاء الاصطناعي
- نظام إدارة المشتركين والنشرة البريدية
- بوت تيليجرام @aidreamweaver_bot
- تسويق آلي على منصات التواصل
- لوحة إدارة كاملة

## التشغيل السريع

### الوضع العادي (API)
```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### الوضع المحلي مع Ollama (مجاني)
```bash
# 1. تثبيت Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. تحميل النموذج
ollama pull llama3.2

# 3. تشغيل
ollama serve &
python ollama_gemma4.py --dream "حلمك هنا"
```

## GitHub Actions
- مقال يومي: 8:00 صباحاً
- تسويق: 3 مرات يومياً
- نشر تلقائي عند كل push

## التوثيق
- [دليل Ollama](OLLAMA_GUIDE.md) - التشغيل المحلي المجاني
- [إعداد Ollama](setup_gemma4.sh) - سكريبت التثبيت التلقائي

تحديث: 2026-06-07
