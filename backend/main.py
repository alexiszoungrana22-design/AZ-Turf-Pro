from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api import router


app = FastAPI(
    title="AZ Turf Pro",
    version="1.0"
)


# Routes API
app.include_router(router)


# Racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent


# Servir directement les fichiers frontend
app.mount(
    "/",
    StaticFiles(directory=str(BASE_DIR), html=True),
    name="frontend"
)


# Route API conservée par le router
