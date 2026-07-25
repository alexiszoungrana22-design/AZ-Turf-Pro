from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from api import router


app = FastAPI(
    title="AZ Turf Pro",
    version="1.0"
)


# API analyse
app.include_router(router)


# Chemin frontend
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


# Servir CSS / JS / images
app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static"
)


# Page principale
@app.get("/")
def accueil():
    return FileResponse(
        FRONTEND_DIR / "index.html"
    )
