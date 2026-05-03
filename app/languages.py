"""
نظام اللغات الثنائي - Bilingual Language System
العربية والإنجليزية معاً بدون تعقيدات
"""

LANGUAGES = {
    "ar": {
        "name": "العربية",
        "direction": "rtl",
        "code": "ar"
    },
    "en": {
        "name": "English",
        "direction": "ltr",
        "code": "en"
    }
}

# الترجمات الأساسية
TRANSLATIONS = {
    "ar": {
        "welcome": "أهلاً وسهلاً",
        "login": "تسجيل الدخول",
        "register": "إنشاء حساب",
        "logout": "تسجيل الخروج",
        "dashboard": "لوحة التحكم",
        "blog": "المدونة",
        "dream": "الحلم",
        "interpretation": "التفسير",
        "email": "البريد الإلكتروني",
        "password": "كلمة المرور",
        "username": "اسم المستخدم",
        "submit": "إرسال",
        "cancel": "إلغاء",
        "save": "حفظ",
        "delete": "حذف",
        "edit": "تعديل",
        "back": "رجوع",
        "next": "التالي",
        "previous": "السابق",
        "home": "الرئيسية",
        "about": "عن المنصة",
        "contact": "اتصل بنا",
        "settings": "الإعدادات",
        "profile": "الملف الشخصي",
        "my_dreams": "أحلامي",
        "my_interpretations": "تفسيراتي",
        "subscribe": "اشترك",
        "unsubscribe": "إلغاء الاشتراك",
        "search": "بحث",
        "filter": "تصفية",
        "sort": "ترتيب",
        "loading": "جاري التحميل...",
        "error": "حدث خطأ",
        "success": "تم بنجاح",
        "warning": "تحذير",
        "info": "معلومة",
        "confirm": "تأكيد",
        "are_you_sure": "هل أنت متأكد؟",
        "yes": "نعم",
        "no": "لا",
        "ok": "حسناً",
    },
    "en": {
        "welcome": "Welcome",
        "login": "Login",
        "register": "Sign Up",
        "logout": "Logout",
        "dashboard": "Dashboard",
        "blog": "Blog",
        "dream": "Dream",
        "interpretation": "Interpretation",
        "email": "Email",
        "password": "Password",
        "username": "Username",
        "submit": "Submit",
        "cancel": "Cancel",
        "save": "Save",
        "delete": "Delete",
        "edit": "Edit",
        "back": "Back",
        "next": "Next",
        "previous": "Previous",
        "home": "Home",
        "about": "About",
        "contact": "Contact Us",
        "settings": "Settings",
        "profile": "Profile",
        "my_dreams": "My Dreams",
        "my_interpretations": "My Interpretations",
        "subscribe": "Subscribe",
        "unsubscribe": "Unsubscribe",
        "search": "Search",
        "filter": "Filter",
        "sort": "Sort",
        "loading": "Loading...",
        "error": "Error",
        "success": "Success",
        "warning": "Warning",
        "info": "Info",
        "confirm": "Confirm",
        "are_you_sure": "Are you sure?",
        "yes": "Yes",
        "no": "No",
        "ok": "OK",
    }
}

def get_text(key, language="ar"):
    """الحصول على نص مترجم"""
    if language not in TRANSLATIONS:
        language = "ar"
    return TRANSLATIONS[language].get(key, key)

def get_language_info(language_code):
    """الحصول على معلومات اللغة"""
    return LANGUAGES.get(language_code, LANGUAGES["ar"])
