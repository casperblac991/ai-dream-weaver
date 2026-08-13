from pathlib import Path
import re
from html import escape

ROOT = Path(__file__).parent
blog_dir = ROOT / "blog"
reports_dir = ROOT / "reports"

posts = []

def extract_meta(html_content, default_title):
    title = default_title
    m_title = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
    if m_title:
        title = m_title.group(1).strip()
    return title

for p in sorted(blog_dir.glob("*.html"), key=lambda x: x.stat().st_mtime, reverse=True):
    content = p.read_text(encoding="utf-8", errors="ignore")
    title = extract_meta(content, p.stem.replace("-", " "))
    date = "2026"
    m_date = re.search(r'2026-\d{2}-\d{2}', p.name + content)
    if m_date:
        date = m_date.group(0)
    posts.append({
        "title": title,
        "url": f"/blog/{p.name}",
        "date": date,
        "category": "موسوعة الحضارات والتراث"
    })

for p in sorted(reports_dir.glob("*.html"), key=lambda x: x.stat().st_mtime, reverse=True):
    content = p.read_text(encoding="utf-8", errors="ignore")
    title = extract_meta(content, p.stem.replace("-", " "))
    date = "2026"
    m_date = re.search(r'2026-\d{2}-\d{2}', p.name + content)
    if m_date:
        date = m_date.group(0)
    posts.append({
        "title": title,
        "url": f"/reports/{p.name}",
        "date": date,
        "category": "التقارير التحليلية"
    })

print(f"Total collected items for blog: {len(posts)}")

html_cards = []
for item in posts:
    t_esc = escape(item["title"])
    u_esc = escape(item["url"])
    d_esc = escape(item["date"])
    c_esc = escape(item["category"])
    card = f'''
    <a href="{u_esc}" class="card" data-title="{t_esc}">
        <div class="card-img">📜</div>
        <div class="card-body">
            <span class="card-tag">{c_esc}</span>
            <h3>{t_esc}</h3>
            <p>تقرير بحثي شامل وموسّع من أرشيف منصة نَسَّاج لتفسير الأحلام والرموز.</p>
            <div class="card-meta">
                <span>📅 {d_esc}</span>
                <span class="read-more">اقرأ التقرير ←</span>
            </div>
        </div>
    </a>
    '''
    html_cards.append(card)

cards_html_str = "".join(html_cards)

page_template = f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>موسوعة التقارير والمدونة | Weaver نَسَّاج</title>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800;900&display=swap" rel="stylesheet">
<style>
    *, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: 'Tajawal', sans-serif;
        background: #050210;
        color: #e2d9f3;
        line-height: 1.6;
    }}
    .bg {{ position: fixed; inset: 0; z-index: -2; background: radial-gradient(ellipse at 20% 50%,#1e0a3c 0%,transparent 60%), radial-gradient(ellipse at 80% 20%,#0c0a3e 0%,transparent 50%),#050210; }}
    nav {{
        position: sticky; top: 0; z-index: 100;
        display: flex; justify-content: space-between; align-items: center;
        padding: .75rem 2rem;
        background: rgba(5,2,16,.9);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(124,58,237,.4);
    }}
    .logo {{ font-size: 1.4rem; font-weight: 900; display: flex; align-items: center; gap: 5px; text-decoration: none; }}
    .logo-en {{ background: linear-gradient(135deg,#f0c060,#7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
    .logo-ar {{ color: #a855f7; }}
    .nav-links {{ display: flex; align-items: center; gap: 1rem; }}
    .nav-links a {{ color: #e2d9f3; text-decoration: none; font-size: .85rem; }}
    .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
    .page-hero {{ text-align: center; padding: 3rem 0; }}
    .page-hero h1 {{ font-size: 3rem; font-weight: 900; color: #f0c060; margin-bottom: 1rem; }}
    .page-hero p {{ color: rgba(226,217,243,0.7); max-width: 700px; margin: 0 auto; }}
    
    .search-box {{
        margin: 2rem auto;
        max-width: 600px;
        display: flex;
        gap: 10px;
    }}
    .search-box input {{
        flex: 1;
        padding: 14px 20px;
        background: rgba(30,10,60,0.8);
        border: 1px solid rgba(124,58,237,0.5);
        border-radius: 30px;
        color: white;
        font-family: inherit;
        font-size: 1rem;
        outline: none;
    }}
    .search-box input:focus {{ border-color: #f0c060; box-shadow: 0 0 15px rgba(240,192,96,0.3); }}
    
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 2rem; }}
    .card {{ background: rgba(30,10,60,0.6); border: 1px solid rgba(124,58,237,0.3); border-radius: 20px; overflow: hidden; transition: 0.3s; text-decoration: none; color: inherit; display: flex; flex-direction: column; }}
    .card:hover {{ transform: translateY(-5px); border-color: #a855f7; box-shadow: 0 10px 30px rgba(124,58,237,0.2); }}
    .card-img {{ height: 140px; background: linear-gradient(135deg, #1e0a3c, #0c0a3e); display: flex; align-items: center; justify-content: center; font-size: 3rem; }}
    .card-body {{ padding: 1.5rem; flex: 1; display: flex; flex-direction: column; }}
    .card-tag {{ display: inline-block; padding: 0.2rem 0.8rem; border-radius: 50px; font-size: 0.75rem; font-weight: bold; margin-bottom: 0.8rem; background: rgba(168,85,247,0.2); color: #a855f7; border: 1px solid rgba(168,85,247,0.4); }}
    .card h3 {{ font-size: 1.1rem; color: #f0c060; margin-bottom: 0.8rem; }}
    .card p {{ font-size: 0.85rem; color: rgba(226,217,243,0.7); margin-bottom: 1.5rem; flex: 1; }}
    .card-meta {{ font-size: 0.8rem; color: rgba(226,217,243,0.5); display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 1rem; }}
    .read-more {{ color: #f0c060; font-weight: bold; }}
    .footer {{ text-align: center; padding: 40px; color: rgba(226,217,243,0.5); border-top: 1px solid rgba(124,58,237,0.3); margin-top: 60px; }}
</style>
</head>
<body>
<div class="bg"></div>
<nav>
    <a href="/" class="logo"><span class="logo-en">Weaver</span><span class="logo-ar">نَسَّاج</span></a>
    <div class="nav-links">
        <a href="/">الرئيسية</a>
        <a href="/app/community">المجتمع</a>
        <a href="/reports">التقارير</a>
        <a href="/blog.html">المدونة</a>
    </div>
</nav>

<div class="container">
    <div class="page-hero">
        <h1>📚 موسوعة التقارير والمدونة</h1>
        <p>أرشيف متكامل يضم أكثر من 800 تقرير ومقال عن الحضارات القديمة، رموز الأحلام، وتراث التفسير الإسلامي والعالمي.</p>
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="ابحث في عناوين التقارير والرموز..." onkeyup="filterCards()">
        </div>
    </div>

    <div class="grid" id="postsGrid">
        {cards_html_str}
    </div>
</div>

<div class="footer">
    <p>© 2026 Weaver | نَسَّاج — موسوعة الأحلام والرموز بالذكاء الاصطناعي</p>
</div>

<script>
function filterCards() {{
    const input = document.getElementById('searchInput').value.toLowerCase();
    const cards = document.getElementsByClassName('card');
    for (let i = 0; i < cards.length; i++) {{
        const title = cards[i].getAttribute('data-title').toLowerCase();
        if (title.includes(input)) {{
            cards[i].style.display = "";
        }} else {{
            cards[i].style.display = "none";
        }}
    }}
}}
</script>
</body>
</html>
'''

(ROOT / "blog.html").write_text(page_template, encoding="utf-8")
print("BLOG_PAGE_GENERATED_SUCCESSFULLY")
