from fastapi import APIRouter, HTTPException
from engine import lancer_analyse


router = APIRouter(
    prefix="/api",
    tags=["AZ Turf"]
)


@router.get("/analyse")
def analyse():

    try:
        resultat = lancer_analyse()

        if not isinstance(resultat, dict):
            raise Exception("Résultat analyse invalide")

        return {
            "message": "Analyse AZ Turf terminée",

            "chevaux": resultat.get(
                "classement",
                []
            ),

            "classement": resultat.get(
                "classement",
                []
            ),

            "favori": resultat.get(
                "favori",
                {}
            ),

            "tickets": resultat.get(
                "tickets",
                {}
            )
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Erreur analyse AZ Turf : {str(e)}"
        )
