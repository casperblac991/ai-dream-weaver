from pathlib import Path
from html import escape

root = Path(__file__).parent / "app"
pages = {
    "lucid-lab": ("مختبر الأحلام", "أدوات عملية لفهم الأحلام وتسجيل التجارب بواجهة بسيطة.", "🔬"),
    "cosmic-dictionary": ("القاموس الكوني", "استكشف رموز الأحلام ومعانيها الثقافية عبر الحضارات.", "🌌"),
    "global-map": ("خارطة الأحلام العالمية", "اكتشف كيف تتقاطع رموز الأحلام بين المجتمعات والثقافات.", "🌍"),
    "personality-test": ("تحليل الشخصية", "اختبار تأملي يساعدك على تنظيم أفكارك وتجاربك، وليس تشخيصاً طبياً.", "🧠"),
    "offers": ("العروض الخاصة", "خطط Weaver وخيارات الاستخدام المتاحة للمجتمع العالمي.", "💎"),
    "dream-interpreter": ("مفسر الأحلام", "اكتب حلمك للحصول على تحليل ذكي متوازن مع تنبيه أن النتائج للتأمل وليست بديلاً عن المختصين.", "🔮"),
}
style = "body{margin:0;background:#07051a;color:#f4eaff;font-family:Arial,Tahoma,sans-serif}.nav,main{max-width:900px;margin:auto}.nav{padding:18px 20px;display:flex;justify-content:space-between}.nav a{color:#ffd166;text-decoration:none}main{padding:70px 20px;text-align:center}.hero{background:#17123a;border:1px solid #7445c5;border-radius:24px;padding:45px 25px}.icon{font-size:4rem}h1{color:#ffd166}p{color:#c9bddf;line-height:1.8}.cta{display:inline-block;margin:15px 8px;padding:12px 20px;border-radius:24px;background:#ffd166;color:#130b25;text-decoration:none;font-weight:bold}.secondary{background:#7445c5;color:#fff}"
for slug, (title, description, icon) in pages.items():
    html = f'''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} | نَسَّاج</title><style>{style}</style></head><body><nav class="nav"><a href="/">Weaver | نَسَّاج</a><a href="/app/community.html">المجتمع</a></nav><main><section class="hero"><div class="icon">{icon}</div><h1>{escape(title)}</h1><p>{escape(description)}</p><a class="cta" href="/app/analyze.html">ابدأ الآن</a><a class="cta secondary" href="/blog.html">استكشف المدونة</a></section></main></body></html>\n'''
    (root / f"{slug}.html").write_text(html, encoding="utf-8")
print(f"STATIC_FEATURES={len(pages)}")
