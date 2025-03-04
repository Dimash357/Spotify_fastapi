from fastapi import FastAPI, File, UploadFile, Request, Query, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
import shutil
import os

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

templates = Jinja2Templates(directory="static")

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"}  # Разрешённые аудиоформаты


@app.get("/")
async def index(request: Request, message: str = Query(None)):
    """Главная страница"""
    files = os.listdir(UPLOAD_DIR)  # Получаем список загруженных файлов
    return templates.TemplateResponse("main.html", {"request": request, "files": files, "message": message})


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Загрузка аудиофайла (с проверкой расширения)"""
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Можно загружать только аудиофайлы!")

    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return RedirectResponse(url=f"/?message=Файл-успешно-загружен!", status_code=303)



@app.get("/uploads/{filename}")
async def serve_file(filename: str):
    """Раздача загруженных аудиофайлов"""
    return StaticFiles(directory=UPLOAD_DIR).get_response(filename)


# Скачивание и воспроизведение файлов

@app.get("/play/{filename}")
async def play_audio(filename: str):
    """Раздаёт аудиофайл"""
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg")
    raise HTTPException(status_code=404, detail="Файл не найден")

