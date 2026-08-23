# =====================================
# AZ TURF PRO - SERVEUR PRINCIPAL (main.py)
# FastAPI + Routes API + Fichiers Statiques
# =====================================

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from api import router


app = FastAPI(
    title="AZ Turf Pro API",
    description="Serveur web et API d'analyse hippique AZ Turf Pro",
    version="1.0.0"
)

# =====================================
# AUTORISATIONS CORS (GitHub Pages, Render, Local)
# =====================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://alexiszoungrana22-design.github.io",
        "https://az-turf-pro.onrender.com",
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:5500",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================
# ROUTES API
# =====================================

app.include_router(router)

# =====================================
# CHEMINS DU PROJET ET DÉTECTION RACINE
# =====================================

BASE_DIR = Path(__file__).resolve().parent

# Détection automatique de la racine du projet (si main.py est dans un sous-dossier ou à la racine)
if (BASE_DIR / "index.html").exists():
    ROOT_DIR = BASE_DIR
else:
    ROOT_DIR = BASE_DIR.parent

# =====================================
# MONTAGE DES DOSSIERS STATIQUES (IMAGES, CSS, JS)
# =====================================

# Dossier Images
IMAGES_DIR = ROOT_DIR / "images"
if not IMAGES_DIR.exists():
    IMAGES_DIR = BASE_DIR / "images"

if IMAGES_DIR.exists():
    app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

# Dossiers CSS et JS
for dossier in ["css", "js"]:
    chemin = ROOT_DIR / dossier
    if not chemin.exists():
        chemin = BASE_DIR / dossier

    if chemin.exists():
        app.mount(f"/{dossier}", StaticFiles(directory=chemin), name=dossier)

# =====================================
# ROUTE DE SANTÉ / HEALTHCHECK
# =====================================

@app.get("/health", tags=["Système"])
def health_check():
    return {
        "status": "OK",
        "app": "AZ Turf Pro",
        "message": "Le serveur est en ligne et fonctionnel."
    }

# =====================================
# SERVING DE LA PAGE D'ACCUEIL ET PAGES HTML
# =====================================

@app.get("/", tags=["Frontend"])
def accueil():
    index_file = ROOT_DIR / "index.html"
    if not index_file.exists():
        index_file = BASE_DIR / "index.html"

    if index_file.exists():
        return FileResponse(index_file)

    return {
        "message": "AZ Turf Pro API est opérationnelle.",
        "status": "OK",
        "documentation": "/docs"
    }


@app.get("/{page_name}.html", tags=["Frontend"])
def servir_page_html(page_name: str):
    fichier_html = ROOT_DIR / f"{page_name}.html"
    if not fichier_html.exists():
        fichier_html = BASE_DIR / f"{page_name}.html"

    if fichier_html.exists():
        return FileResponse(fichier_html)

    return JSONResponse(
        status_code=404,
        content={"message": f"Page '{page_name}.html' introuvable."}
        )
