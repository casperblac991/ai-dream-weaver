from pathlib import Path
from html import escape

ROOT = Path(__file__).parent


def write_alias(path: Path, target: str, title: str = "Weaver"):
    path.mkdir(parents=True, exist_ok=True)
    html = f'''<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="robots" content="noindex"><title>{escape(title)}</title><meta http-equiv="refresh" content="0;url={escape(target)}"><script>location.replace({target!r});</script></head><body><a href="{escape(target)}">فتح الصفحة</a></body></html>\n'''
    (path / "index.html").write_text(html, encoding="utf-8")

# All extension-less links used by the static home page and navigation.
aliases = {
    "login": "/app/login.html", "register": "/app/register.html", "signup": "/app/register.html",
    "dashboard": "/app/dashboard.html", "contact": "/app/contact.html", "creators": "/app/explore.html",
    "prompt-lab": "/app/dream-interpreter.html", "trending": "/app/trending.html",
    "dream-feed": "/app/dream-feed.html", "cart": "/shop.html",
}
for name, target in aliases.items():
    write_alias(ROOT / name, target, name)

app_aliases = {
    "login": "login.html", "register": "register.html", "dashboard": "dashboard.html", "analyze": "analyze.html",
    "community": "../templates/community.html", "lucid-lab": "../templates/lucid-lab.html", "cosmic-dictionary": "../templates/cosmic-dictionary.html",
    "global-map": "../templates/global-map.html", "personality-test": "../templates/personality-test.html", "offers": "../templates/offers.html",
    "explore": "explore.html", "trending": "trending.html", "dream-feed": "../templates/dream-feed.html",
    "dream-interpreter": "../templates/dream-interpreter.html", "contact": "contact.html",
}
for name, filename in app_aliases.items():
    if (ROOT / "app" / filename).is_file():
        target = filename if filename.startswith("/") else f"/app/{filename}"
        if filename.startswith("../templates/"):
            target = "/templates/" + filename.split("/", 2)[-1]
        write_alias(ROOT / "app" / name, target, name)

# Blog cards use /blog/<slug>; preserve every archived file through a directory alias.
blog_dir = ROOT / "blog"
for html_file in blog_dir.glob("*.html"):
    write_alias(blog_dir / html_file.stem, f"/blog/{html_file.name}", html_file.stem)

print("STATIC_ALIASES_GENERATED")
