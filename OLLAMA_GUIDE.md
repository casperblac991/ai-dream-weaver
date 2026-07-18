# Ollama Local AI Integration Guide
# دليل دمج Ollama للذكاء الاصطناعي المحلي

## نظرة عامة | Overview

يتيح لك هذا الدليل تشغيل نماذج **Ollama** محلياً على جهازك لتشغيل ميزات الذكاء الاصطناعي بدون الحاجة لخدمات سحابية مدفوعة.

### المميزات | Features

- تفسير أحلام محلي - بدون اتصال بالإنترنت
- مجاني تماماً - لا توجد تكاليف API
- سريع الاستجابة - معالجة محلية فورية
- خصوصية كاملة - بياناتك لا تغادر جهازك
- يعمل على 8GB RAM - مع نموذج Llama 3.2

---

## التثبيت | Installation

### 1. تثبيت Ollama

```bash
# Linux / Mac
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# تحميل من https://ollama.com/download
```

### 2. تحميل نموذج

```bash
# Llama 3.2 - موصى به (8GB RAM)
ollama pull llama3.2

# Mistral - سريع وخفيف (6GB RAM)
ollama pull mistral

# Llama 3.1 - إصدار أقدم
ollama pull llama3.1
```

### 3. تشغيل Ollama

```bash
ollama serve
```

### 4. تشغيل سكريبت الإعداد

```bash
chmod +x setup_gemma4.sh
./setup_gemma4.sh
```

---

## الاستخدام | Usage

### سطر الأوامر | CLI

```bash
# فحص الاتصال
python ollama_gemma4.py --check

# قائمة النماذج
python ollama_gemma4.py --list-models

# تحميل النموذج
python ollama_gemma4.py --pull --model llama3.2

# تفسير حلم
python ollama_gemma4.py --dream "I saw myself flying in a dream" --style general

# وضع تفاعلي
python ollama_gemma4.py --model llama3.2
```

### في التطبيق | In App

```python
from app.ai import interpret_dream_local, check_ollama_status

# فحص حالة Ollama
status = check_ollama_status()
print(status)

# تفسير حلم
result = interpret_dream_local(
    dream_text="رأيت البحر في المنام",
    style="islamic",  # islamic, psychological, ancient, general
    language="ar"     # ar, en
)
print(result)
```

### متغيرات البيئة | Environment Variables

```bash
# URL Ollama (الافتراضي: http://localhost:11434)
export OLLAMA_BASE_URL=http://localhost:11434

# نموذج Ollama (الافتراضي: llama3.2)
export OLLAMA_MODEL=llama3.2
```

---

## نماذج Ollama المتاحة | Available Models

| النموذج | RAM | الوصف |
|---------|-----|-------|
| llama3.2 | 8GB | **موصى به** - أفضل توازن بين الجودة والسرعة |
| llama3.1 | 8GB | إصدار مستقر |
| mistral | 6GB | سريع وخفيف |
| gemma4:12b-it-qat | 8GB | Gemma 4 (قريباً) |

---

## Docker | Docker

### تشغيل مع Docker

```bash
# بناء الصورة
docker build -t weaver-ollama .

# تشغيل
docker run -p 8000:8000 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  weaver-ollama
```

### استخدام Ollama في Docker

```bash
# تشغيل Ollama في Container
docker run -d --name ollama -p 11434:11434 ollama/ollama

# تحميل النموذج
docker exec ollama ollama pull llama3.2

# تشغيل التطبيق
docker run -p 8000:8000 \
  --env-file .env \
  --link ollama \
  weaver-ollama
```

---

## مقارنة | Comparison

| الميزة | Ollama المحلي | API سحابي |
|--------|---------------|-----------|
| التكلفة | مجاني | مدفوع |
| الخصوصية | 100% محلية | بيانات على السحابة |
| السرعة | فوري (مع GPU) | يعتمد على الاتصال |
| الصيانة | تحتاج إعداد | جاهز فوراً |
| الجودة | عالية | عالية جداً |

---

## نصائح | Tips

### تحسين الأداء | Performance

1. استخدم GPU - Llama 3.2 يعمل أفضل مع GPU
2. النماذج المحسنة - استخدم النماذج المحسنة لتوفير الذاكرة
3. Quantization - فعّل fp16 أو int8 للإخراج

### استكشاف الأخطاء | Troubleshooting

```bash
# Ollama لا يعمل
ollama serve

# فحص النماذج
ollama list

# حذف نموذج
ollama rm llama3.2

# معلومات النموذج
ollama show llama3.2
```

---

## المراجع | References

- Ollama: https://ollama.com
- Llama Models: https://ollama.com/library/llama3.2
- Mistral: https://ollama.com/library/mistral

---

## دعم | Support

للمساعدة أو الأسئلة:
- Discord: Ollama Community https://discord.gg/ollama
- Email: hello@ollama.com
