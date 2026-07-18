#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weaver Database - قاعدة البيانات المتكاملة (包含所有函数)
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

def init_db():
    with get_db() as db:
        # Users
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
        # Dreams
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
        # Email subscribers
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
        # Blog posts
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
        # Community Comments
        db.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                dream_id INTEGER NOT NULL,
                comment_text TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(dream_id) REFERENCES dreams(id) ON DELETE CASCADE
            )
        """)
        # User Follows
        db.execute("""
            CREATE TABLE IF NOT EXISTS follows (
                follower_id INTEGER NOT NULL,
                followed_id INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (follower_id, followed_id),
                FOREIGN KEY(follower_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(followed_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        db.commit()
    print("✅ قاعدة البيانات جاهزة")

# ========== دوال المستخدمين ==========
def create_user(username, email, hashed_password):
    try:
        with get_db() as db:
            cursor = db.execute("""
                INSERT INTO users (username, email, password)
                VALUES (?, ?, ?)
            """, (username, email, hashed_password))
            db.commit()
            return {"success": True, "user_id": cursor.lastrowid}
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return {"success": False, "message": "اسم المستخدم موجود بالفعل"}
        if "email" in str(e):
            return {"success": False, "message": "البريد الإلكتروني موجود بالفعل"}
        return {"success": False, "message": "خطأ في قاعدة البيانات"}

def get_user_by_id(user_id):
    with get_db() as db:
        row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None

def get_user_by_email(email):
    with get_db() as db:
        row = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return dict(row) if row else None

def update_last_login(user_id):
    with get_db() as db:
        db.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.now().isoformat(), user_id))
        db.commit()

def get_all_users(limit=100):
    with get_db() as db:
        rows = db.execute("SELECT * FROM users ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(row) for row in rows]

# ========== دوال الأحلام ==========
def save_dream(user_id, dream_text, interpretation, image_prompt=""):
    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO dreams (user_id, dream_text, interpretation, image_prompt)
            VALUES (?, ?, ?, ?)
        """, (user_id, dream_text, interpretation, image_prompt))
        db.commit()
        return cursor.lastrowid

def get_user_dreams(user_id, limit=50):
    with get_db() as db:
        rows = db.execute("""
            SELECT * FROM dreams WHERE user_id = ?
            ORDER BY created_at DESC LIMIT ?
        """, (user_id, limit)).fetchall()
        return [dict(row) for row in rows]

def get_dreams_used(user_id):
    today = datetime.now().strftime("%Y-%m-%d")
    with get_db() as db:
        row = db.execute("""
            SELECT COUNT(*) FROM dreams
            WHERE user_id = ? AND DATE(created_at) = ?
        """, (user_id, today)).fetchone()
        return row[0] if row else 0

def increment_dreams_used(user_id):
    with get_db() as db:
        db.execute("UPDATE users SET dreams_used = dreams_used + 1 WHERE id = ?", (user_id,))
        db.commit()

# ========== دوال النشرة البريدية ==========
def save_email_subscriber(email, name=""):
    with get_db() as db:
        db.execute("INSERT OR IGNORE INTO email_subscribers (email, name) VALUES (?, ?)", (email, name))
        db.commit()

def get_all_subscribers():
    with get_db() as db:
        rows = db.execute("SELECT * FROM email_subscribers WHERE is_active = 1").fetchall()
        return [dict(row) for row in rows]

# ========== دوال المدونة ==========
def save_blog_post(title, content, slug, category="تفسير الأحلام", author="نَسَّاج AI"):
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

# ========== دوال الإحصائيات ==========
def get_platform_stats():
    with get_db() as db:
        total_users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_dreams = db.execute("SELECT COUNT(*) FROM dreams").fetchone()[0]
        total_blog = db.execute("SELECT COUNT(*) FROM blog_posts").fetchone()[0]
        dreams_today = db.execute("SELECT COUNT(*) FROM dreams WHERE DATE(created_at) = DATE('now')").fetchone()[0]
        return {
            "total_users": total_users,
            "total_dreams": total_dreams,
            "total_blog_posts": total_blog,
            "dreams_today": dreams_today
        }
