#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام الاشتراكات والخطط المدفوعة - Weaver v3.0
"""

from datetime import datetime, timedelta
import sqlite3

# خطط الاشتراك المتاحة
SUBSCRIPTION_PLANS = {
    "free": {
        "name": "مجاني",
        "price": 0,
        "dreams_per_day": 3,
        "image_generation": False,
        "advanced_analysis": False,
        "email_support": False,
        "features": ["تفسير أساسي", "حفظ الأحلام", "إحصائيات بسيطة"]
    },
    "pro": {
        "name": "احترافي",
        "price": 9.99,  # دولار شهري
        "dreams_per_day": 50,
        "image_generation": True,
        "advanced_analysis": True,
        "email_support": True,
        "features": [
            "تفسير متقدم",
            "توليد صور الأحلام",
            "تحليل نفسي عميق",
            "تقارير شهرية",
            "دعم البريد الإلكتروني"
        ]
    },
    "business": {
        "name": "عملي",
        "price": 29.99,  # دولار شهري
        "dreams_per_day": 999,
        "image_generation": True,
        "advanced_analysis": True,
        "email_support": True,
        "api_access": True,
        "features": [
            "تفسير غير محدود",
            "توليد صور 4K",
            "تحليل نفسي متقدم",
            "تقارير أسبوعية",
            "دعم الأولوية 24/7",
            "وصول API",
            "تصدير البيانات"
        ]
    }
}

def create_subscription_tables():
    """إنشاء جداول الاشتراكات والفواتير"""
    conn = sqlite3.connect("app/weaver.db")
    cursor = conn.cursor()
    
    # جدول الاشتراكات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan TEXT NOT NULL DEFAULT 'free',
            status TEXT NOT NULL DEFAULT 'active',
            start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_date TIMESTAMP,
            auto_renew INTEGER DEFAULT 1,
            stripe_subscription_id TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # جدول الفواتير
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            status TEXT DEFAULT 'pending',
            stripe_invoice_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            paid_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # جدول الترقيات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS upgrades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            from_plan TEXT,
            to_plan TEXT,
            amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ جداول الاشتراكات جاهزة")

def get_user_subscription(user_id: int):
    """الحصول على معلومات الاشتراك الحالي للمستخدم"""
    conn = sqlite3.connect("app/weaver.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT plan, status, end_date FROM subscriptions 
        WHERE user_id = ? ORDER BY start_date DESC LIMIT 1
    """, (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        plan, status, end_date = result
        return {
            "plan": plan,
            "status": status,
            "end_date": end_date,
            "details": SUBSCRIPTION_PLANS.get(plan, SUBSCRIPTION_PLANS["free"])
        }
    return {
        "plan": "free",
        "status": "active",
        "details": SUBSCRIPTION_PLANS["free"]
    }

def upgrade_subscription(user_id: int, new_plan: str, amount: float = 0):
    """ترقية اشتراك المستخدم إلى خطة أعلى"""
    conn = sqlite3.connect("app/weaver.db")
    cursor = conn.cursor()
    
    # الحصول على الخطة الحالية
    cursor.execute("SELECT plan FROM subscriptions WHERE user_id = ? ORDER BY start_date DESC LIMIT 1", (user_id,))
    current = cursor.fetchone()
    old_plan = current[0] if current else "free"
    
    # إنشاء اشتراك جديد
    end_date = datetime.now() + timedelta(days=30)
    cursor.execute("""
        INSERT INTO subscriptions (user_id, plan, status, end_date)
        VALUES (?, ?, 'active', ?)
    """, (user_id, new_plan, end_date))
    
    # تسجيل الترقية
    cursor.execute("""
        INSERT INTO upgrades (user_id, from_plan, to_plan, amount)
        VALUES (?, ?, ?, ?)
    """, (user_id, old_plan, new_plan, amount))
    
    # إنشاء فاتورة
    cursor.execute("""
        INSERT INTO invoices (user_id, plan, amount, status)
        VALUES (?, ?, ?, 'pending')
    """, (user_id, new_plan, amount))
    
    conn.commit()
    conn.close()
    return {"success": True, "message": f"تم الترقية إلى {SUBSCRIPTION_PLANS[new_plan]['name']}"}

def create_invoice(user_id: int, plan: str):
    """إنشاء فاتورة للمستخدم"""
    plan_info = SUBSCRIPTION_PLANS.get(plan, SUBSCRIPTION_PLANS["free"])
    amount = plan_info["price"]
    
    conn = sqlite3.connect("app/weaver.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO invoices (user_id, plan, amount, currency, status)
        VALUES (?, ?, ?, 'USD', 'pending')
    """, (user_id, plan, amount))
    
    invoice_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "invoice_id": invoice_id,
        "user_id": user_id,
        "plan": plan,
        "amount": amount,
        "currency": "USD",
        "status": "pending"
    }

def mark_invoice_paid(invoice_id: int, stripe_invoice_id: str = None):
    """تحديث حالة الفاتورة إلى مدفوعة"""
    conn = sqlite3.connect("app/weaver.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE invoices 
        SET status = 'paid', paid_at = CURRENT_TIMESTAMP, stripe_invoice_id = ?
        WHERE id = ?
    """, (stripe_invoice_id, invoice_id))
    conn.commit()
    conn.close()
    return {"success": True, "message": "تم تحديث الفاتورة"}

def get_revenue_stats():
    """الحصول على إحصائيات الإيرادات"""
    conn = sqlite3.connect("app/weaver.db")
    cursor = conn.cursor()
    
    # إجمالي الإيرادات
    cursor.execute("SELECT SUM(amount) FROM invoices WHERE status = 'paid'")
    total_revenue = cursor.fetchone()[0] or 0
    
    # عدد المشتركين المدفوعين
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM subscriptions WHERE plan != 'free'")
    paid_users = cursor.fetchone()[0] or 0
    
    # الخطط الأكثر شيوعاً
    cursor.execute("""
        SELECT plan, COUNT(*) as count FROM subscriptions 
        WHERE status = 'active' GROUP BY plan
    """)
    plans_distribution = dict(cursor.fetchall())
    
    conn.close()
    
    return {
        "total_revenue": total_revenue,
        "paid_users": paid_users,
        "plans_distribution": plans_distribution,
        "average_revenue_per_user": total_revenue / paid_users if paid_users > 0 else 0
    }

if __name__ == "__main__":
    create_subscription_tables()
