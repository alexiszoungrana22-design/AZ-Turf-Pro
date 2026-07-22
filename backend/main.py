from fastapi import FastAPI
from api import router

app = FastAPI(
    title="AZ Turf Pro API",
    version="1.0"
)

app.include_router(router)


@app.get("/")
def accueil():
    return {
        "message": "Bienvenue sur AZ Turf Pro"
    }
