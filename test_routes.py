from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
email = f"qa-{uuid4().hex[:10]}@example.com"
username = f"qa_{uuid4().hex[:10]}"
password = "TestPassword123!"

assert client.get("/api/me").status_code == 401
register = client.post("/api/register", json={"username": username, "email": email, "password": password})
assert register.status_code == 200, register.text
assert register.json().get("authenticated") is True
assert client.get("/api/me").json().get("authenticated") is True
assert client.get("/app/dashboard").status_code == 200
reply = client.post("/api/customer-reply", json={"message": "كيف أستخدم المنصة؟", "language": "ar"})
assert reply.status_code == 200, reply.text
assert reply.json().get("reply")
subscribe = client.post("/api/subscribe", json={"email": f"sub-{uuid4().hex[:10]}@example.com", "name": "QA"})
assert subscribe.status_code == 200
client.get("/app/logout")
assert client.get("/api/me").status_code == 401
print("HTTP_ROUTES_OK")
