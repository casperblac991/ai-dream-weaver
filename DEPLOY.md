# 📦 دليل النشر

## الوضع الحالي
- الموقع: https://aidreamweaver.store (GitHub Pages - Static HTML)
- التطبيق: Python FastAPI (يتطلب خادم)

## 🔧 للنشر على الخادم

### الطريقة 1: تشغيل يدوي على الخادم
```bash
cd /path/to/ai-dream-weaver
git pull
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### الطريقة 2: استخدام systemd (للإنتاج)
```bash
sudo nano /etc/systemd/system/weaver.service
```

```ini
[Unit]
Description=Weaver AI Dream Interpreter
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/ai-dream-weaver
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable weaver
sudo systemctl start weaver
```

### الطريقة 3: Docker
```bash
docker build -t weaver-ai .
docker run -d -p 8000:8000 weaver-ai
```

## 📁 الملفات المطلوبة للنشر
- `app/main.py` - التطبيق الرئيسي
- `app/ai.py` - ذكاء اصطناعي (Ollama + API)
- `templates/*.html` - صفحات HTML
- `requirements.txt` - التبعيات

## ✅ التحقق
```bash
curl http://localhost:8000/dream-experience.html
curl http://localhost:8000/api/ollama-status
```