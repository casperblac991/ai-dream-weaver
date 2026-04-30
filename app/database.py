#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weaver Database - قاعدة البيانات المتكاملة
تحتوي على جميع الدوال التي يحتاجها main.py
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "weaver.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# ================================================================
# INITIALIZATION
# ================================================================
def init_db():
    with get_db() as db:
        # users
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
        db.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")

        # dreams
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
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        db.execute("CREATE INDEX IF NOT EXISTS idx_dreams_user ON dreams(user_id)")

        # email_subscribers
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

        # blog_posts
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
        db.execute("CREATE INDEX IF NOT EXISTS idx_blog_slug ON blog_posts(slug)")

        # platform_stats
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

        # marketing_log
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

# ================================================================
# USER FUNCTIONS (يستخدمها auth.py و main.py)
# ================================================================
def get_user_by_id(user_id: int):
    with get_db() as db:
        row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None

def get_user_by_email(email: str):
    with get_db() as db:
        row = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return dict(row) if row else None

def get_user_by_username(username: str):
    with get_db() as db:
        row = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return dict(row) if row else None

def create_user(username: str, email: str, hashed_password: str):
    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?)
        """, (username, email, hashed_password))
        db.commit()
        return cursor.lastrowid

def update_last_login(user_id: int):
    with get_db() as db:
        db.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.now().isoformat(), user_id))
        db.commit()

def get_all_users(limit=100):
    with get_db() as db:
        rows = db.execute("SELECT * FROM users ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(row) for row in rows]

# ================================================================
# DREAM FUNCTIONS (يستخدمها main.py)
# ================================================================
def save_dream(user_id: int, dream_text: str, interpretation: str, image_prompt: str = ""):
    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO dreams (user_id, dream_text, interpretation, image_prompt)
            VALUES (?, ?, ?, ?)
        """, (user_id, dream_text, interpretation, image_prompt))
        db.commit()
        return cursor.lastrowid

def get_user_dreams(user_id: int, limit=50):
    with get_db() as db:
        rows = db.execute("""
            SELECT * FROM dreams WHERE user_id = ?
            ORDER BY created_at DESC LIMIT ?
        """, (user_id, limit)).fetchall()
        return [dict(row) for row in rows]

def get_dreams_used(user_id: int) -> int:
    """عدد التفسيرات التي استخدمها المستخدم اليوم (حسب التاريخ)"""
    today = datetime.now().strftime("%Y-%m-%d")
    with get_db() as db:
        row = db.execute("""
            SELECT COUNT(*) FROM dreams
            WHERE user_id = ? AND DATE(created_at) = ?
        """, (user_id, today)).fetchone()
        return row[0] if row else 0

def increment_dreams_used(user_id: int):
    """زيادة عداد التفسيرات اليومية للمستخدم"""
    # هذه دالة اختيارية - يمكن استخدامها مع حقل dreams_used في users
    with get_db() as db:
        db.execute("UPDATE users SET dreams_used = dreams_used + 1 WHERE id = ?", (user_id,))
        db.commit()

def get_all_dreams(limit=100):
    with get_db() as db:
        rows = db.execute("""
            SELECT d.*, u.username FROM dreams d
            JOIN users u ON d.user_id = u.id
            ORDER BY d.created_at DESC LIMIT ?
        """, (limit,)).fetchall()
        return [dict(row) for row in rows]

# ================================================================
# SUBSCRIPTION FUNCTIONS (للاشتراكات البريدية)
# ================================================================
def save_email_subscriber(email: str, name: str = ""):
    with get_db() as db:
        db.execute("""
            INSERT OR IGNORE INTO email_subscribers (email, name)
            VALUES (?, ?)
        """, (email, name))
        db.commit()

def get_all_subscribers():
    with get_db() as db:
        rows = db.execute("SELECT * FROM email_subscribers WHERE is_active = 1").fetchall()
        return [dict(row) for row in rows]

def remove_subscriber(email: str):
    with get_db() as db:
        db.execute("UPDATE email_subscribers SET is_active = 0 WHERE email = ?", (email,))
        db.commit()

# ================================================================
# BLOG FUNCTIONS (يستخدمها main.py للمدونة)
# ================================================================
def save_blog_post(title: str, content: str, slug: str, category: str = "تفسير الأحلام", author: str = "نَسَّاج AI"):
    with get_db() as db:
        excerpt = content[:150] + "..." if len(content) > 150 else content
        db.execute("""
            INSERT OR REPLACE INTO blog_posts (title, slug, content, excerpt, category, author)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, slug, content, excerpt, category, author))
        db.commit()

def get_blog_posts(limit=50):
    with get_db() as db:
        rows = db.execute("""
            SELECT * FROM blog_posts WHERE is_published = 1
            ORDER BY created_at DESC LIMIT ?
        """, (limit,)).fetchall()
        return [dict(row) for row in rows]

def get_blog_post_by_slug(slug: str):
    with get_db() as db:
        row = db.execute("SELECT * FROM blog_posts WHERE slug = ?", (slug,)).fetchone()
        return dict(row) if row else None

def increment_blog_views(slug: str):
    with get_db() as db:
        db.execute("UPDATE blog_posts SET views = views + 1 WHERE slug = ?", (slug,))
        db.commit()

# ================================================================
# STATS FUNCTIONS (إحصائيات المنصة)
# ================================================================
def get_platform_stats():
    with get_db() as db:
        total_users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_dreams = db.execute("SELECT COUNT(*) FROM dreams").fetchone()[0]
        total_blog = db.execute("SELECT COUNT(*) FROM blog_posts").fetchone()[0]
        active_today = db.execute("""
            SELECT COUNT(*) FROM dreams
            WHERE DATE(created_at) = DATE('now')
        """).fetchone()[0]
        return {
            "total_users": total_users,
            "total_dreams": total_dreams,
            "total_blog_posts": total_blog,
            "dreams_today": active_today
        }

def record_daily_stats():
    """تسجيل إحصائيات اليوم (يُستدعى مرة يومياً)"""
    today = datetime.now().strftime("%Y-%m-%d")
    with get_db() as db:
        # هل يوجد سجل لليوم؟
        existing = db.execute("SELECT id FROM platform_stats WHERE date = ?", (today,)).fetchone()
        if not existing:
            db.execute("INSERT INTO platform_stats (date) VALUES (?)", (today,))
            db.commit()
