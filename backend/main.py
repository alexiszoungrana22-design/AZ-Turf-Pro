from pathlib import Path
import sys
import asyncio

# Ensure the backend directory is always on sys.path, including Render
# executions where the working directory can differ from the module directory.
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

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

# Scheduler PMU : synchronisation des arrivées et préparation anticipée
# du programme de demain deux heures après la course principale du jour.
_scheduler_task = None


@app.on_event("startup")
async def demarrer_scheduler_pmu():
    global _scheduler_task
    from scheduler_resultats import lancer_scheduler
    if _scheduler_task is None or _scheduler_task.done():
        _scheduler_task = lancer_scheduler()


@app.on_event("shutdown")
async def arreter_scheduler_pmu():
    global _scheduler_task
    if _scheduler_task is not None and not _scheduler_task.done():
        _scheduler_task.cancel()
        try:
            await _scheduler_task
        except asyncio.CancelledError:
            pass
    _scheduler_task = None

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
# CSS / JS (si prÃ©sents)
# ==============================

for dossier in ["css", "js"]:
    chemin = ROOT_DIR / dossier
    if chemin.exists():
        app.mount(f"/{dossier}", StaticFiles(directory=chemin), name=dossier)

# ==============================
# Fichiers frontend Ã  la racine
# ==============================
# Le frontend actuel rÃ©fÃ©rence ses CSS/JS/HTML directement Ã  la racine
# (/style.css, /analyse.js, /historique.js, etc.). Les dossiers /css et /js
# ne sont donc pas suffisants. Ces routes servent uniquement des fichiers
# prÃ©sents directement dans ROOT_DIR et bloquent les chemins traversants.

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
# Frontend statique Ã  la racine
# ==============================
# Sert les fichiers frontend rÃ©fÃ©rencÃ©s directement depuis /.
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
