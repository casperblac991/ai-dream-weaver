from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# تشغيل مجلد الملفات الثابتة (الصور)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def index():
    return FileResponse("templates/index.html")

@app.get("/home")
def home():
    return FileResponse("templates/home.html")

@app.get("/dashboard")
def dashboard():
    return FileResponse("templates/dashboard.html")

@app.get("/dream")
def dream():
    return FileResponse("templates/dream.html")

@app.get("/dream-feed")
def dream_feed():
    return FileResponse("templates/dream_feed.html")

@app.get("/explore")
def explore():
    return FileResponse("templates/explore.html")

@app.get("/history")
def history():
    return FileResponse("templates/history.html")

@app.get("/profile")
def profile():
    return FileResponse("templates/profile.html")

@app.get("/search")
def search():
    return FileResponse("templates/search.html")

@app.get("/trending")
def trending():
    return FileResponse("templates/trending.html")

@app.get("/login")
def login():
    return FileResponse("templates/login.html")

@app.get("/register")
def register():
    return FileResponse("templates/register.html")

# المدونة
@app.get("/blog")
def blog():
    return FileResponse("templates/blog/index.html")

@app.get("/blog/ancient-egypt-dreams")
def egypt():
    return FileResponse("templates/blog/ancient-egypt-dreams.html")

@app.get("/blog/babylonian-dreams")
def babylon():
    return FileResponse("templates/blog/babylonian-dreams.html")

@app.get("/blog/greek-dream-interpretation")
def greek():
    return FileResponse("templates/blog/greek-dream-interpretation.html")

@app.get("/blog/islamic-dream-interpretation")
def islamic():
    return FileResponse("templates/blog/islamic-dream-interpretation.html")

@app.get("/blog/snake-dream-meaning")
def snake():
    return FileResponse("templates/blog/snake-dream-meaning.html")

@app.get("/blog/flying-dream-meaning")
def flying():
    return FileResponse("templates/blog/flying-dream-meaning.html")
