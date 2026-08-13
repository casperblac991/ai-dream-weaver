import re
from pathlib import Path

root = Path(__file__).parent
links = set()
for path in list((root / "templates").glob("*.html")) + list((root / "app").glob("*.html")) + list((root / "blog").glob("*.html")):
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        continue
    for value in re.findall(r'(?:href|src)=["\']([^"\']+)', text):
        if value.startswith("/") and not value.startswith(("//", "/api/", "/css/", "/js/", "/images/", "/reports/")):
            links.add(value.split("#", 1)[0].split("?", 1)[0])

existing_templates = {f"/{p.name}" for p in (root / "templates").glob("*.html")}
existing_app = {f"/app/{p.name}" for p in (root / "app").glob("*.html")}
missing = sorted(link for link in links if link.endswith(".html") and link not in existing_templates and link not in existing_app)
print("LINK_COUNT", len(links))
print("MISSING_STATIC_HTML", len(missing))
for link in missing:
    print(link)
