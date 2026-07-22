from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.database import Base, engine
from config import settings

from models import horse
from models import race
from models import prediction

# Création des tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Backend officiel AZ Turf-Pro"
)
@app.get("/pronostic")
def pronostic():
    return {
        "selection": [
            {"numero": 11, "indice": 92},
            {"numero": 10, "indice": 88},
            {"numero": 7, "indice": 85},
            {"numero": 4, "indice": 82},
            {"numero": 13, "indice": 79},
            {"numero": 6, "indice": 76},
            {"numero": 2, "indice": 72}
        ],
        "base": "11 - Cheval Confiance",
        "outsider": "6 - Cheval Surprise",
        "ticket": "11 - 10 - 7 - 4 - 13"
    }

# Autorisation frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def accueil():

    return {
        "message": "AZ Turf-Pro Backend opérationnel",
        "version": settings.VERSION
    }


@app.get("/status")
def status():

    return {
        "api": "active",
        "systeme": "AZ Turf-Pro",
        "intelligence": "en préparation"
    }
