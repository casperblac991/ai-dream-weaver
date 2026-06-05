#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weaver Shop API - واجهة برمجية للمتجر
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import json
from datetime import datetime

router = APIRouter(prefix="/api/shop", tags=["shop"])

# قاعدة بيانات المنتجات (يمكن نقلها إلى قاعدة بيانات حقيقية لاحقاً)
PRODUCTS = [
    {
        "id": 1,
        "name": "تفسير حلم واحد",
        "category": "basic",
        "price": 9.99,
        "emoji": "🔮",
        "description": "تفسير شامل لحلم واحد مع شرح مفصل"
    },
    {
        "id": 2,
        "name": "باقة 10 أحلام",
        "category": "premium",
        "price": 49.99,
        "emoji": "✨",
        "description": "تفسير 10 أحلام مع تحليل نفسي عميق"
    },
    {
        "id": 3,
        "name": "تقرير الأحلام الأسبوعي",
        "category": "premium",
        "price": 29.99,
        "emoji": "📊",
        "description": "تقرير شامل لأحلام الأسبوع مع رسوم بيانية"
    },
    {
        "id": 4,
        "name": "دورة تفسير الأحلام الإسلامي",
        "category": "courses",
        "price": 79.99,
        "emoji": "📚",
        "description": "دورة متكاملة في تفسير الأحلام وفقاً للتراث الإسلامي"
    },
    {
        "id": 5,
        "name": "دورة علم النفس والأحلام",
        "category": "courses",
        "price": 69.99,
        "emoji": "🧠",
        "description": "فهم الأحلام من منظور علم النفس الحديث"
    },
    {
        "id": 6,
        "name": "أداة تحليل الأحلام المتقدمة",
        "category": "tools",
        "price": 99.99,
        "emoji": "🔧",
        "description": "أداة متقدمة لتحليل الأحلام مع ميزات AI"
    },
    {
        "id": 7,
        "name": "قاموس الرموز الحلمية",
        "category": "tools",
        "price": 39.99,
        "emoji": "📖",
        "description": "قاموس شامل لتفسير الرموز والدلالات"
    },
    {
        "id": 8,
        "name": "اشتراك سنوي بريميوم",
        "category": "premium",
        "price": 199.99,
        "emoji": "👑",
        "description": "وصول غير محدود لجميع الخدمات والمميزات"
    }
]

# سجل الطلبات (يمكن نقله إلى قاعدة بيانات)
ORDERS = []

@router.get("/products")
async def get_products(category: str = None):
    """الحصول على قائمة المنتجات"""
    if category and category != "all":
        filtered = [p for p in PRODUCTS if p["category"] == category]
        return {"status": "success", "products": filtered}
    return {"status": "success", "products": PRODUCTS}

@router.get("/products/{product_id}")
async def get_product(product_id: int):
    """الحصول على تفاصيل منتج معين"""
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="المنتج غير موجود")
    return {"status": "success", "product": product}

@router.post("/orders")
async def create_order(request: Request):
    """إنشاء طلب جديد"""
    try:
        data = await request.json()
        
        # التحقق من البيانات
        if not data.get("items") or not data.get("email"):
            raise HTTPException(status_code=400, detail="بيانات غير كاملة")
        
        # حساب الإجمالي
        total = 0
        for item in data["items"]:
            product = next((p for p in PRODUCTS if p["id"] == item["id"]), None)
            if not product:
                raise HTTPException(status_code=400, detail=f"المنتج {item['id']} غير موجود")
            total += product["price"] * item.get("quantity", 1)
        
        # إنشاء الطلب
        order = {
            "id": len(ORDERS) + 1,
            "email": data["email"],
            "items": data["items"],
            "total": total,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "payment_url": f"https://payment.example.com/checkout/{len(ORDERS) + 1}"
        }
        
        ORDERS.append(order)
        
        return {
            "status": "success",
            "order": order,
            "message": "تم إنشاء الطلب بنجاح"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/{order_id}")
async def get_order(order_id: int):
    """الحصول على تفاصيل طلب"""
    order = next((o for o in ORDERS if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="الطلب غير موجود")
    return {"status": "success", "order": order}

@router.post("/checkout")
async def checkout(request: Request):
    """معالجة الدفع (محاكاة)"""
    try:
        data = await request.json()
        
        order_id = data.get("order_id")
        payment_method = data.get("payment_method", "card")
        
        # البحث عن الطلب
        order = next((o for o in ORDERS if o["id"] == order_id), None)
        if not order:
            raise HTTPException(status_code=404, detail="الطلب غير موجود")
        
        # تحديث حالة الطلب
        order["status"] = "completed"
        order["payment_method"] = payment_method
        order["paid_at"] = datetime.now().isoformat()
        
        return {
            "status": "success",
            "message": "تم الدفع بنجاح",
            "order": order,
            "receipt_url": f"https://aidreamweaver.store/receipts/{order_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_shop_stats():
    """إحصائيات المتجر"""
    total_products = len(PRODUCTS)
    total_orders = len(ORDERS)
    total_revenue = sum(o["total"] for o in ORDERS if o["status"] == "completed")
    
    return {
        "status": "success",
        "stats": {
            "total_products": total_products,
            "total_orders": total_orders,
            "completed_orders": len([o for o in ORDERS if o["status"] == "completed"]),
            "total_revenue": total_revenue,
            "average_order_value": total_revenue / total_orders if total_orders > 0 else 0
        }
    }

@router.post("/subscribe")
async def subscribe_email(request: Request):
    """الاشتراك في النشرة البريدية"""
    try:
        data = await request.json()
        email = data.get("email")
        
        if not email or "@" not in email:
            raise HTTPException(status_code=400, detail="بريد إلكتروني غير صحيح")
        
        # يمكن حفظ البريد في قاعدة البيانات هنا
        return {
            "status": "success",
            "message": "تم الاشتراك بنجاح",
            "email": email
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
