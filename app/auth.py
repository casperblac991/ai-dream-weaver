#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weaver Auth - نظام المصادقة (معدل للاستيراد من database.py)
"""

import re
import bcrypt
from app.database import create_user, get_user_by_email, update_last_login

def hash_password(password: str) -> str:
    """تشفير كلمة المرور باستخدام bcrypt مباشرةً لتوافق أفضل مع الإصدارات الحديثة."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """التحقق من كلمة المرور مع التعامل الآمن مع الهاش غير الصالح."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except (ValueError, TypeError):
        return False

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> dict:
    if len(password) < 6:
        return {"valid": False, "message": "كلمة المرور يجب أن تكون 6 أحرف على الأقل"}
    return {"valid": True}

def register_user(username: str, email: str, password: str) -> dict:
    if not username or len(username) < 3:
        return {"success": False, "message": "اسم المستخدم يجب أن يكون 3 أحرف على الأقل"}
    if not validate_email(email):
        return {"success": False, "message": "البريد الإلكتروني غير صالح"}
    pwd_check = validate_password(password)
    if not pwd_check["valid"]:
        return {"success": False, "message": pwd_check["message"]}
    hashed = hash_password(password)
    return create_user(username, email, hashed)

def login_user(email: str, password: str):
    if not email or not password:
        return None
    user = get_user_by_email(email)
    if user and verify_password(password, user["password"]):
        if user.get("is_active", 1):
            update_last_login(user["id"])
            return user
    return None
