from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# تشغيل مجلد الصور والملفات الثابتة
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    return FileResponse("templates/index.html")

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
