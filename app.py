import os
import sys

# إضافة المجلد الحالي لمسار النظام لضمان العثور على المجلدات الفرعية
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
