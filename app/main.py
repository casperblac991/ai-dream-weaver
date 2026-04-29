#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sqlite3
from datetime import datetime
from pathlib import Path

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# إعداد القوالب (تأكد من وجود مجلد templates)
templates = Jinja2Templates(directory="app/templates")

# قاعدة بيانات بسيطة للمستخدمين
DB_PATH = "weaver.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ قاعدة البيانات جاهزة")

init_db()

# صفحات تسجيل الدخول وإنشاء الحساب (GET)
@app.get("/app/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/app/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# معالجة تسجيل الدخول (POST)
@app.post("/app/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        response = RedirectResponse("/", status_code=302)
        response.set_cookie("user_id", str(user[0]), max_age=86400)
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "بيانات غير صحيحة"})

# معالجة إنشاء حساب (POST)
@app.post("/app/register")
async def register(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        response = RedirectResponse("/", status_code=302)
        response.set_cookie("user_id", str(user_id), max_age=86400)
        return response
    except sqlite3.IntegrityError:
        conn.close()
        return templates.TemplateResponse("register.html", {"request": request, "error": "البريد أو اسم المستخدم موجود مسبقاً"})

# الصفحة الرئيسية
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# نقاط إضافية (للمدونة، المتجر، إلخ) يمكنك إضافتها لاحقاً

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
