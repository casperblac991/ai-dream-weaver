#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام الدفع - Stripe و PayPal Integration
"""

import os
import json
from datetime import datetime

# محاكاة Stripe (في الإنتاج، استخدم مفتاح API الفعلي)
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "sk_test_demo_key")
PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID", "demo_client_id")
PAYPAL_CLIENT_SECRET = os.environ.get("PAYPAL_CLIENT_SECRET", "demo_secret")

class PaymentProcessor:
    """معالج الدفع الموحد"""
    
    @staticmethod
    def create_stripe_checkout(user_id: int, plan: str, amount: float):
        """إنشاء جلسة دفع Stripe"""
        return {
            "provider": "stripe",
            "session_id": f"cs_{user_id}_{plan}_{int(datetime.now().timestamp())}",
            "user_id": user_id,
            "plan": plan,
            "amount": amount,
            "currency": "USD",
            "checkout_url": f"https://checkout.stripe.com/pay/cs_{user_id}_{plan}",
            "status": "pending"
        }
    
    @staticmethod
    def create_paypal_order(user_id: int, plan: str, amount: float):
        """إنشاء طلب PayPal"""
        return {
            "provider": "paypal",
            "order_id": f"pp_{user_id}_{plan}_{int(datetime.now().timestamp())}",
            "user_id": user_id,
            "plan": plan,
            "amount": amount,
            "currency": "USD",
            "approval_url": f"https://www.paypal.com/checkoutnow?token=pp_{user_id}_{plan}",
            "status": "pending"
        }
    
    @staticmethod
    def verify_stripe_payment(session_id: str):
        """التحقق من دفع Stripe"""
        # في الإنتاج، استخدم Stripe API
        return {
            "status": "success",
            "session_id": session_id,
            "amount_paid": 9.99,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def verify_paypal_payment(order_id: str):
        """التحقق من دفع PayPal"""
        # في الإنتاج، استخدم PayPal API
        return {
            "status": "success",
            "order_id": order_id,
            "amount_paid": 9.99,
            "timestamp": datetime.now().isoformat()
        }

class RefundProcessor:
    """معالج استرجاع الأموال"""
    
    @staticmethod
    def process_refund(invoice_id: int, reason: str = ""):
        """معالجة استرجاع الأموال"""
        return {
            "refund_id": f"ref_{invoice_id}_{int(datetime.now().timestamp())}",
            "invoice_id": invoice_id,
            "reason": reason,
            "status": "processed",
            "timestamp": datetime.now().isoformat()
        }

class SubscriptionManager:
    """مدير الاشتراكات المتقدم"""
    
    @staticmethod
    def calculate_proration(old_plan: str, new_plan: str, days_remaining: int):
        """حساب الفرق عند الترقية (Proration)"""
        from app.subscriptions import SUBSCRIPTION_PLANS
        
        old_price = SUBSCRIPTION_PLANS[old_plan]["price"]
        new_price = SUBSCRIPTION_PLANS[new_plan]["price"]
        
        daily_old = old_price / 30
        daily_new = new_price / 30
        
        credit = daily_old * days_remaining
        charge = daily_new * days_remaining
        
        return {
            "credit": credit,
            "charge": charge,
            "net_amount": charge - credit
        }
    
    @staticmethod
    def send_payment_receipt(user_email: str, invoice_data: dict):
        """إرسال إيصال الدفع عبر البريد الإلكتروني"""
        receipt = f"""
        🧾 إيصال الدفع - Weaver
        
        البريد الإلكتروني: {user_email}
        الخطة: {invoice_data['plan']}
        المبلغ: ${invoice_data['amount']}
        التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        شكراً لاختيارك Weaver! 🌙
        """
        return {"sent": True, "receipt": receipt}

# إحصائيات الدفع
PAYMENT_STATS = {
    "total_transactions": 0,
    "total_revenue": 0,
    "successful_payments": 0,
    "failed_payments": 0,
    "refunds": 0
}

def log_transaction(transaction_type: str, amount: float, status: str):
    """تسجيل معاملة مالية"""
    PAYMENT_STATS["total_transactions"] += 1
    if status == "success":
        PAYMENT_STATS["total_revenue"] += amount
        PAYMENT_STATS["successful_payments"] += 1
    elif status == "failed":
        PAYMENT_STATS["failed_payments"] += 1
    elif status == "refund":
        PAYMENT_STATS["refunds"] += 1
    
    return {
        "transaction_logged": True,
        "stats": PAYMENT_STATS
    }

def get_payment_analytics():
    """الحصول على تحليلات الدفع"""
    success_rate = (PAYMENT_STATS["successful_payments"] / PAYMENT_STATS["total_transactions"] * 100) if PAYMENT_STATS["total_transactions"] > 0 else 0
    
    return {
        "total_transactions": PAYMENT_STATS["total_transactions"],
        "total_revenue": PAYMENT_STATS["total_revenue"],
        "successful_payments": PAYMENT_STATS["successful_payments"],
        "failed_payments": PAYMENT_STATS["failed_payments"],
        "refunds": PAYMENT_STATS["refunds"],
        "success_rate": f"{success_rate:.2f}%",
        "average_transaction": PAYMENT_STATS["total_revenue"] / PAYMENT_STATS["successful_payments"] if PAYMENT_STATS["successful_payments"] > 0 else 0
    }
