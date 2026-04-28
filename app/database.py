#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weaver Database - قاعدة البيانات
SQLite مع جداول محدّثة
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "weaver.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """تهيئة قاعدة البيانات وإنشاء الجداول"""
    with get_db() as db:
        # جدول المستخدمين
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                plan TEXT DEFAULT 'free',
                role TEXT DEFAULT 'user',
                dreams_used INTEGER DEFAULT 0,
                total_dreams INTEGER DEFAULT 0,
                avatar TEXT DEFAULT '',
                bio TEXT DEFAULT '',
                telegram_id TEXT DEFAULT '',
                is_active INTEGER DEFAULT 1,
                last_login TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # جدول الأحلام
        db.execute("""
            CREATE TABLE IF NOT EXISTS dreams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                dream_text TEXT NOT NULL,
                interpretation TEXT,
                image_prompt TEXT DEFAULT '',
                style TEXT DEFAULT 'islamic',
                language TEXT DEFAULT 'ar',
                is_public INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                views INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

        # جدول المشتركين في النشرة البريدية
        db.execute("""
            CREATE TABLE IF NOT EXISTS email_subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT DEFAULT '',
                is_active INTEGER DEFAULT 1,
                source TEXT DEFAULT 'website',
                subscribed_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # جدول مقالات المدونة
        db.execute("""
            CREATE TABLE IF NOT EXISTS blog_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                excerpt TEXT DEFAULT '',
                category TEXT DEFAULT 'تفسير الأحلام',
                author TEXT DEFAULT 'نَسَّاج AI',
                cover_image TEXT DEFAULT '',
                views INTEGER DEFAULT 0,
                is_published INTEGER DEFAULT 1,
                language TEXT DEFAULT 'ar',
                tags TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # جدول إحصائيات المنصة
        db.execute("""
            CREATE TABLE IF NOT EXISTS platform_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE NOT NULL,
                visitors INTEGER DEFAULT 0,
                new_users INTEGER DEFAULT 0,
                dreams_interpreted INTEGER DEFAULT 0,
                blog_views INTEGER DEFAULT 0
            )
        """)

        # جدول سجل التسويق
        db.execute("""
            CREATE TABLE IF NOT EXISTS marketing_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                content TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                posted_at TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        db.commit()
    print("✅ قاعدة البيانات جاهزة")
