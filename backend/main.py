from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api import router
import os

app = FastAPI(
    title="AZ Turf Pro API",
    version="1.0"
)

app.include_router(router)


# API uniquement sur Render
# Le frontend est hébergé par GitHub Pages


@app.get("/")
def accueil():
    return {
        "message": "AZ Turf Pro API en ligne"
    }
