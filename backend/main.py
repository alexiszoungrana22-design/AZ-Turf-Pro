from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from fastapi.middleware.cors import CORSMiddleware

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



# Servir le frontend si présent

try:

    app.mount(
        "/static",
        StaticFiles(directory="../frontend"),
        name="static"
    )

except Exception:
    pass



# Page accueil

@app.get("/")
def accueil():

    return FileResponse(
        "../frontend/index.html"
    )
