from pathlib import Path
import json
from urllib.parse import unquote

root = Path(__file__).parent
items = json.loads((root / "blog_index.json").read_text(encoding="utf-8"))
missing = []
for item in items:
    path = root / unquote(item["url"].lstrip("/"))
    if not path.is_file():
        missing.append((item.get("url"), str(path)))
print(f"BLOG_INDEX_ITEMS={len(items)}")
print(f"BLOG_INDEX_MISSING={len(missing)}")
if missing:
    for row in missing[:20]:
        print(row)
    raise SystemExit(1)
html = (root / "blog.html").read_text(encoding="utf-8")
assert "fetch('/blog_index.json" in html
assert "PER_PAGE=24" in html
print("BLOG_INDEX_OK")
