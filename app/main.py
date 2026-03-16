from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import os

from app.database import init_db
from app.auth import register_user, login_user
from app.models import get_user_by_id, save_dream, get_user_dreams, get_dreams_used, increment_dreams_used
from app.ai import interpret_dream

init_db()
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

sessions = {}

@app.get("/app", response_class=HTMLResponse)
async def app_home(request: Request):
    user_id = sessions.get("user_id")
    user = get_user_by_id(user_id) if user_id else None
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.get("/app/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/app/register")
async def register(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    if register_user(username, email, password):
        return RedirectResponse("/app/login", status_code=302)
    return templates.TemplateResponse("register.html", {"request": request, "error": "المستخدم موجود"})

@app.get("/app/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/app/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    user = login_user(email, password)
    if user:
        sessions["user_id"] = user["id"]
        return RedirectResponse("/app/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "خطأ في البريد أو كلمة المرور"})

@app.get("/app/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user_id = sessions.get("user_id")
    if not user_id:
        return RedirectResponse("/app/login")
    user = get_user_by_id(user_id)
    dreams = get_user_dreams(user_id)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "dreams": dreams})

@app.get("/app/analyze", response_class=HTMLResponse)
async def analyze_page(request: Request):
    user_id = sessions.get("user_id")
    if not user_id:
        return RedirectResponse("/app/login")
    return templates.TemplateResponse("analyze.html", {"request": request})

@app.post("/app/analyze")
async def analyze(request: Request, dream: str = Form(...)):
    user_id = sessions.get("user_id")
    if not user_id:
        return RedirectResponse("/app/login")
    
    user = get_user_by_id(user_id)
    used = get_dreams_used(user_id)
    
    if user["plan"] == "free" and used >= 5:
        return templates.TemplateResponse("analyze.html", {"request": request, "error": "لقد استنفدت حدك المجاني. اشترك للاستمرار."})
    
    interpretation = interpret_dream(dream)
    save_dream(user_id, dream, interpretation)
    increment_dreams_used(user_id)
    
    return templates.TemplateResponse("analyze.html", {"request": request, "dream": dream, "interpretation": interpretation})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
