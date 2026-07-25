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



# Dossier racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent



# Servir les fichiers du site
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR)),
    name="static"
)



# Page d'accueil
@app.get("/")
def accueil():

    return FileResponse(
        str(BASE_DIR / "index.html")
    )
