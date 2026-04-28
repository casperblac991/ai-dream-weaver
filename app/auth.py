#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weaver Auth - نظام المصادقة
"""

import hashlib
import re
from app.models import create_user, get_user_by_email, update_last_login

def hash_password(password: str) -> str:
    """تشفير كلمة المرور"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email: str) -> bool:
    """التحقق من صحة البريد الإلكتروني"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> dict:
    """التحقق من قوة كلمة المرور"""
    if len(password) < 6:
        return {"valid": False, "message": "كلمة المرور يجب أن تكون 6 أحرف على الأقل"}
    return {"valid": True}

def register_user(username: str, email: str, password: str) -> dict:
    """تسجيل مستخدم جديد"""
    # التحقق من البيانات
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
    """تسجيل دخول المستخدم"""
    if not email or not password:
        return None

    user = get_user_by_email(email)
    if user and user["password"] == hash_password(password):
        if user.get("is_active", 1):
            update_last_login(user["id"])
            return user
    return None
