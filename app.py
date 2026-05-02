import os
import sys

# إضافة المجلد الحالي لمسار النظام
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# استيراد التطبيق من app.main
from app.main import app as fastapi_app

# تصدير التطبيق للاستخدام من قبل Uvicorn
app = fastapi_app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
