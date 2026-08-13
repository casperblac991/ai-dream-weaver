from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
paths = [
    "/", "/about", "/faq", "/blog", "/community", "/offers", "/reports",
    "/reports/index.json", "/ancient-egypt-dreams.html", "/blog/ancient-egypt-dreams",
    "/app/login", "/app/register", "/app/dashboard", "/app/analyze", "/health",
]
for path in paths:
    response = client.get(path, follow_redirects=False)
    print(path, response.status_code, response.headers.get("location", ""))
    if path in {"/", "/about", "/faq", "/blog", "/community", "/offers", "/reports", "/ancient-egypt-dreams.html", "/health"}:
        assert response.status_code == 200, (path, response.status_code, response.text[:200])
    if path in {"/app/dashboard", "/app/analyze"}:
        assert response.status_code in {302, 307} and response.headers.get("location") == "/app/login"
print("PAGE_SMOKE_OK")
