FROM python:3.11-slim

# تثبيت مكتبات النظام المطلوبة لـ Pillow وباقي الحزم
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# ضبط مجلد العمل
WORKDIR /app

# نسخ ملف المتطلبات وتثبيت الحزم
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع
COPY . .

# تعريف منفذ التشغيل (Render سيحدده تلقائيًا)
EXPOSE 10000

# تشغيل البوت
CMD ["python", "all_bots.py"]
