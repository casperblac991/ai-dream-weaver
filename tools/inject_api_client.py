from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
targets = [ROOT / "index.html", ROOT / "404.html", *sorted((ROOT / "app").glob("*.html"))]
marker = '<script src="/js/api-client.js"></script>'

for path in targets:
    text = path.read_text(encoding="utf-8")
    if marker in text or "<head" not in text.lower():
        continue
    updated, count = re.subn(
        r"(<head(?:\s[^>]*)?>)",
        lambda match: match.group(1) + "\n" + marker,
        text,
        count=1,
        flags=re.IGNORECASE,
    )
    if count:
        path.write_text(updated, encoding="utf-8")
        print(path.relative_to(ROOT))
