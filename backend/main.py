from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api import router
import os


app = FastAPI(
    title="AZ Turf Pro API",
    version="1.0"
)


# Routes API
app.include_router(router)


# Chemin absolu du frontend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")


# Fichiers CSS / JS
app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static"
)


# Page d'accueil
@app.get("/")
def accueil():

    return FileResponse(
        os.path.join(FRONTEND_DIR, "index.html")
    )
