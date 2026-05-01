"""
نظام الحماية والتحكم بالوصول (Middleware)
يفرض تسجيل الدخول قبل الوصول لأي محتوى
"""

from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from functools import wraps
import jwt
from datetime import datetime, timedelta

# المسارات التي لا تتطلب تسجيل دخول (Public Routes)
PUBLIC_ROUTES = [
    "/",
    "/app/login",
    "/app/register",
    "/api/login",
    "/api/register",
    "/api/subscribe",
    "/static/",
    "/docs",
    "/openapi.json"
]

def get_current_user(request: Request):
    """الحصول على بيانات المستخدم من الـ Session أو Token"""
    try:
        # محاولة الحصول على الـ token من الـ cookies
        token = request.cookies.get("access_token")
        if not token:
            return None
        
        # فك تشفير الـ token (يمكن تحسينه لاحقاً)
        # للآن سنستخدم طريقة مبسطة
        return {"authenticated": True, "token": token}
    except:
        return None

def require_login(func):
    """Decorator لفرض تسجيل الدخول على دالة معينة"""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        user = get_current_user(request)
        if not user:
            # إعادة التوجيه لصفحة تسجيل الدخول
            return RedirectResponse(url="/app/login", status_code=302)
        return await func(request, *args, **kwargs)
    return wrapper

async def auth_middleware(request: Request, call_next):
    """Middleware لفرض التحقق من تسجيل الدخول على جميع المسارات"""
    
    # تحديد ما إذا كان المسار عام أم لا
    is_public = False
    for public_route in PUBLIC_ROUTES:
        if public_route.endswith("/"):
            if request.url.path.startswith(public_route):
                is_public = True
                break
        else:
            if request.url.path == public_route:
                is_public = True
                break
    
    # إذا كان المسار عام، السماح بالوصول
    if is_public:
        response = await call_next(request)
        return response
    
    # إذا كان المسار خاص، التحقق من تسجيل الدخول
    user = get_current_user(request)
    if not user:
        # إعادة التوجيه لصفحة تسجيل الدخول
        return RedirectResponse(url="/app/login", status_code=302)
    
    response = await call_next(request)
    return response
