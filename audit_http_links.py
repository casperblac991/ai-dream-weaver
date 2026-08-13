import re
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

root = Path(__file__).parent
links = set()
for path in list((root / "templates").glob("*.html")) + list((root / "app").glob("*.html")):
    text = path.read_text(encoding="utf-8", errors="ignore")
    for value in re.findall(r'(?:href|src)=["\']([^"\']+)', text):
        value = value.split("#", 1)[0].split("?", 1)[0]
        if value.startswith("/") and not value.startswith(("//", "/api/", "/css/", "/js/", "/images/")):
            if "{{" not in value and "${" not in value:
                links.add(value)

client = TestClient(app)
failures = []
for link in sorted(links):
    response = client.get(link, follow_redirects=False)
    if response.status_code == 404:
        failures.append((link, response.status_code))
print(f"CHECKED={len(links)}")
print(f"NOT_FOUND={len(failures)}")
for link, status in failures:
    print(status, link)
if failures:
    raise SystemExit(1)
print("HTTP_LINK_AUDIT_OK")
