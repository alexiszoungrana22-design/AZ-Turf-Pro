from pathlib import Path

from fastapi import FastAPI, HTTPException
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
# Fichiers frontend à la racine
# ==============================
# Le frontend actuel référence ses CSS/JS/HTML directement à la racine
# (/style.css, /analyse.js, /historique.js, etc.). Les dossiers /css et /js
# ne sont donc pas suffisants. Ces routes servent uniquement des fichiers
# présents directement dans ROOT_DIR et bloquent les chemins traversants.

@app.get("/{asset_name}.css")
def servir_css(asset_name: str):
    fichier = ROOT_DIR / f"{asset_name}.css"
    if fichier.is_file() and fichier.parent == ROOT_DIR:
        return FileResponse(fichier, media_type="text/css")
    raise HTTPException(status_code=404, detail="CSS introuvable")


@app.get("/{asset_name}.js")
def servir_js(asset_name: str):
    fichier = ROOT_DIR / f"{asset_name}.js"
    if fichier.is_file() and fichier.parent == ROOT_DIR:
        return FileResponse(fichier, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="JavaScript introuvable")


@app.get("/{page_name}.html")
def servir_page_html(page_name: str):
    fichier = ROOT_DIR / f"{page_name}.html"
    if fichier.is_file() and fichier.parent == ROOT_DIR:
        return FileResponse(fichier, media_type="text/html; charset=utf-8")
    raise HTTPException(status_code=404, detail="Page introuvable")


# ==============================
# Frontend statique à la racine
# ==============================
# Sert les fichiers frontend référencés directement depuis /.
if ROOT_DIR.exists():
    app.mount("/_frontend_static", StaticFiles(directory=ROOT_DIR), name="frontend_static")

# ==============================
# Page d'accueil
# ==============================

@app.get("/")
def accueil():

    index = ROOT_DIR / "index.html"

    if index.exists():
        return FileResponse(index, media_type="text/html; charset=utf-8")

    return {
        "message": "AZ Turf Pro API",
        "status": "OK"
    }
