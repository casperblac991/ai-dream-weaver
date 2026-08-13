from app.main import app

paths = {getattr(route, "path", "") for route in app.routes}
required = {"/api/login", "/api/register", "/api/interpret", "/api/customer-reply", "/community", "/offers", "/app/dream/{dream_id}"}
missing = sorted(required - paths)
print(f"ROUTES={len(paths)}")
print("MISSING=" + ",".join(missing))
print("IMPORT_OK" if not missing else "IMPORT_INCOMPLETE")
if missing:
    raise SystemExit(1)
