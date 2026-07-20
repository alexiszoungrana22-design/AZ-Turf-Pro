from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
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
