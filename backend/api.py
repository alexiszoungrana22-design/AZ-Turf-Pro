from fastapi import APIRouter
from engine import lancer_analyse

router = APIRouter()


@router.get("/analyse")
def analyse():

    resultat = lancer_analyse()

    return {
        "message": "Analyse AZ Turf terminée",
        "chevaux": resultat
    }
