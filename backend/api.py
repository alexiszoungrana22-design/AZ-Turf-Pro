from fastapi import APIRouter
from engine import lancer_analyse

router = APIRouter()


@router.get("/analyse")
def analyse():
    chevaux = [
        {"numero": 1, "nom": "Cheval 1"},
        {"numero": 2, "nom": "Cheval 2"},
        {"numero": 3, "nom": "Cheval 3"},
        {"numero": 4, "nom": "Cheval 4"},
        {"numero": 5, "nom": "Cheval 5"}
    ]

    resultat = lancer_analyse(chevaux)

    return resultat
