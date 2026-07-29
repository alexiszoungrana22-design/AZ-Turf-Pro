from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api import router


app = FastAPI(
    title="AZ Turf Pro API",
    version="1.0"
)

# Autorisation frontend GitHub Pages + Render

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://alexiszoungrana22-design.github.io",
        "https://az-turf-pro.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes API

app.include_router(router)

# ==============================
# Chemins du projet
# ==============================

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

# ==============================
# Images
# ==============================

IMAGES_DIR = ROOT_DIR / "images"

if IMAGES_DIR.exists():
    app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

# ==============================
# CSS / JS (si présents)
# ==============================

for dossier in ["css", "js"]:
    chemin = ROOT_DIR / dossier
    if chemin.exists():
        app.mount(f"/{dossier}", StaticFiles(directory=chemin), name=dossier)

# ==============================
# Page d'accueil
# ==============================

@app.get("/")
def accueil():

    index = ROOT_DIR / "index.html"

    if index.exists():
        return FileResponse(index)

    return {
        "message": "AZ Turf Pro API",
        "status": "OK"
    }
