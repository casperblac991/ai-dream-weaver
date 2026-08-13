from pathlib import Path
import json
import re
from html import escape

ROOT = Path(__file__).parent
BLOG_DIR = ROOT / "blog"
REPORTS_DIR = ROOT / "reports"


def extract_title(content: str, fallback: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
    if not match:
        return fallback
    title = re.sub(r"\s+", " ", match.group(1)).strip()
    return title or fallback


def extract_date(filename: str, content: str) -> str:
    match = re.search(r"20\d{2}-\d{2}-\d{2}", filename + " " + content)
    return match.group(0) if match else ""


def collect(directory: Path, prefix: str, category: str):
    entries = []
    for path in directory.glob("*.html"):
        content = path.read_text(encoding="utf-8", errors="ignore")
        entries.append({
            "title": extract_title(content, path.stem.replace("-", " ")),
            "url": f"{prefix}/{path.name}",
            "date": extract_date(path.name, content),
            "category": category,
        })
    return entries


posts = collect(BLOG_DIR, "/blog", "موسوعة الحضارات والتراث") + collect(REPORTS_DIR, "/reports", "التقارير التحليلية")
posts.sort(key=lambda item: (item["date"], item["title"]), reverse=True)
(ROOT / "blog_index.json").write_text(json.dumps(posts, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

page = r'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>موسوعة التقارير والمدونة | Weaver نَسَّاج</title>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800;900&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box}body{margin:0;font-family:Tajawal,Arial,sans-serif;background:#050210;color:#e2d9f3;line-height:1.6}.bg{position:fixed;inset:0;z-index:-2;background:radial-gradient(ellipse at 20% 50%,#1e0a3c 0%,transparent 60%),radial-gradient(ellipse at 80% 20%,#0c0a3e 0%,transparent 50%),#050210}nav{position:sticky;top:0;z-index:10;display:flex;justify-content:space-between;align-items:center;padding:.75rem 2rem;background:rgba(5,2,16,.94);backdrop-filter:blur(12px);border-bottom:1px solid rgba(124,58,237,.4)}.logo{font-size:1.4rem;font-weight:900;display:flex;gap:5px;text-decoration:none}.logo-en{background:linear-gradient(135deg,#f0c060,#7c3aed);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.logo-ar{color:#a855f7}.nav-links{display:flex;gap:1rem}.nav-links a{color:#e2d9f3;text-decoration:none;font-size:.85rem}.container{max-width:1200px;margin:auto;padding:2rem}.hero{text-align:center;padding:2.5rem 0 1rem}.hero h1{font-size:clamp(2rem,5vw,3rem);color:#f0c060;margin:0 0 1rem}.hero p{color:rgba(226,217,243,.72);max-width:720px;margin:auto}.tools{display:flex;gap:10px;max-width:800px;margin:2rem auto;flex-wrap:wrap}.tools input,.tools select{flex:1;min-width:220px;padding:13px 18px;background:rgba(30,10,60,.85);border:1px solid rgba(124,58,237,.55);border-radius:28px;color:#fff;font:inherit;outline:none}.tools select{flex:0 1 260px}.status{text-align:center;color:#b8acd5;margin:1rem 0}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:1.2rem}.card{background:rgba(30,10,60,.68);border:1px solid rgba(124,58,237,.35);border-radius:18px;overflow:hidden;transition:.25s;text-decoration:none;color:inherit;display:flex;flex-direction:column}.card:hover{transform:translateY(-4px);border-color:#a855f7;box-shadow:0 10px 25px rgba(124,58,237,.2)}.card-img{height:110px;background:linear-gradient(135deg,#1e0a3c,#0c0a3e);display:flex;align-items:center;justify-content:center;font-size:2.6rem}.card-body{padding:1.1rem;display:flex;flex-direction:column;min-height:190px}.tag{display:inline-block;padding:.15rem .65rem;border-radius:50px;font-size:.72rem;font-weight:bold;margin-bottom:.55rem;background:rgba(168,85,247,.2);color:#c084fc;border:1px solid rgba(168,85,247,.4);align-self:flex-start}.card h2{font-size:1rem;color:#f0c060;margin:.2rem 0 .55rem}.card p{font-size:.82rem;color:rgba(226,217,243,.68);margin:0 0 1rem;flex:1}.meta{font-size:.75rem;color:rgba(226,217,243,.58);border-top:1px solid rgba(255,255,255,.1);padding-top:.7rem;display:flex;justify-content:space-between}.read{color:#f0c060;font-weight:bold}.pager{display:flex;justify-content:center;align-items:center;gap:1rem;margin:2rem 0}.pager button{border:1px solid #7445c5;background:#17123a;color:#fff;border-radius:20px;padding:9px 18px;cursor:pointer;font:inherit}.pager button:disabled{opacity:.4;cursor:not-allowed}.footer{text-align:center;padding:35px;color:rgba(226,217,243,.5);border-top:1px solid rgba(124,58,237,.3);margin-top:45px}@media(max-width:650px){nav{padding:.75rem 1rem}.nav-links{gap:.5rem}.nav-links a{font-size:.75rem}.container{padding:1rem}.grid{grid-template-columns:1fr}}
</style>
</head>
<body><div class="bg"></div>
<nav><a href="/" class="logo"><span class="logo-en">Weaver</span><span class="logo-ar">نَسَّاج</span></a><div class="nav-links"><a href="/">الرئيسية</a><a href="/app/community">المجتمع</a><a href="/reports/">التقارير</a><a href="/blog.html">المدونة</a></div></nav>
<main class="container"><section class="hero"><h1>📚 موسوعة التقارير والمدونة</h1><p>أرشيف سريع ومنظم لتقارير الحضارات، رموز الأحلام، كتب التراث، والتحليل العلمي والنفسي.</p></section>
<section class="tools"><input id="search" type="search" placeholder="ابحث في عناوين التقارير والرموز..." autocomplete="off"><select id="category"><option value="">كل الأقسام</option></select></section>
<p id="status" class="status">جاري تحميل الفهرس...</p><section id="grid" class="grid" aria-live="polite"></section>
<div class="pager"><button id="prev" type="button">السابق</button><span id="pageInfo"></span><button id="next" type="button">التالي</button></div></main>
<footer class="footer">© 2026 Weaver | نَسَّاج — موسوعة الأحلام والرموز بالذكاء الاصطناعي</footer>
<script>
const PER_PAGE=24;let all=[],filtered=[],page=1;const $=id=>document.getElementById(id);const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function render(){const total=Math.max(1,Math.ceil(filtered.length/PER_PAGE));page=Math.min(page,total);const start=(page-1)*PER_PAGE;const visible=filtered.slice(start,start+PER_PAGE);$('status').textContent=`عرض ${filtered.length} من أصل ${all.length} تقريراً ومقالاً`;$('pageInfo').textContent=`صفحة ${page} من ${total}`;$('prev').disabled=page<=1;$('next').disabled=page>=total;$('grid').innerHTML=visible.map(x=>`<a class="card" href="${encodeURI(x.url)}"><div class="card-img">📜</div><div class="card-body"><span class="tag">${esc(x.category)}</span><h2>${esc(x.title)}</h2><p>تقرير بحثي من أرشيف منصة نَسَّاج لتفسير الأحلام والرموز.</p><div class="meta"><span>📅 ${esc(x.date||'')}</span><span class="read">اقرأ التقرير ←</span></div></div></a>`).join('')||'<p class="status">لا توجد نتائج مطابقة لبحثك.</p>';}
function filter(){const q=$('search').value.trim().toLowerCase(),c=$('category').value;filtered=all.filter(x=>(!q||`${x.title} ${x.category}`.toLowerCase().includes(q))&&(!c||x.category===c));page=1;render();}
$('search').addEventListener('input',filter);$('category').addEventListener('change',filter);$('prev').addEventListener('click',()=>{page--;render();window.scrollTo({top:250,behavior:'smooth'});});$('next').addEventListener('click',()=>{page++;render();window.scrollTo({top:250,behavior:'smooth'});});
fetch('/blog_index.json?v=20260813').then(r=>{if(!r.ok)throw Error('index');return r.json()}).then(data=>{all=Array.isArray(data)?data:[];filtered=all;[...new Set(all.map(x=>x.category).filter(Boolean))].forEach(c=>{const o=document.createElement('option');o.value=c;o.textContent=c;$('category').appendChild(o)});render()}).catch(()=>{$('status').textContent='تعذر تحميل فهرس المدونة. أعد المحاولة لاحقاً.'});
</script></body></html>
'''
(ROOT / "blog.html").write_text(page, encoding="utf-8")
print(f"BLOG_INDEX_ITEMS={len(posts)}")
print(f"BLOG_HTML_BYTES={(ROOT / 'blog.html').stat().st_size}")
print(f"BLOG_INDEX_BYTES={(ROOT / 'blog_index.json').stat().st_size}")
