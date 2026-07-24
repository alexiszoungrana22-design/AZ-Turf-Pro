from fastapi import APIRouter, HTTPException
from engine import lancer_analyse


router = APIRouter(
    prefix="/api",
    tags=["AZ Turf"]
)


@router.get("/analyse")
def analyse():

    try:

        chevaux = [

            {
                "numero": 1,
                "nom": "Cheval AZ 1",
                "forme": 8,
                "regularite": 7,
                "gains": 7,
                "jockey": 8,
                "cote": 7,
                "distance": 8,
                "terrain": 7,
                "experience": 8
            },

            {
                "numero": 2,
                "nom": "Cheval AZ 2",
                "forme": 9,
                "regularite": 8,
                "gains": 8,
                "jockey": 7,
                "cote": 8,
                "distance": 9,
                "terrain": 8,
                "experience": 8
            },

            {
                "numero": 3,
                "nom": "Cheval AZ 3",
                "forme": 10,
                "regularite": 9,
                "gains": 9,
                "jockey": 9,
                "cote": 9,
                "distance": 9,
                "terrain": 9,
                "experience": 10
            },

            {
                "numero": 4,
                "nom": "Cheval AZ 4",
                "forme": 6,
                "regularite": 6,
                "gains": 6,
                "jockey": 7,
                "cote": 6,
                "distance": 7,
                "terrain": 6,
                "experience": 7
            },

            {
                "numero": 5,
                "nom": "Cheval AZ 5",
                "forme": 9,
                "regularite": 8,
                "gains": 8,
                "jockey": 8,
                "cote": 9,
                "distance": 8,
                "terrain": 8,
                "experience": 9
            },

            {
                "numero": 6,
                "nom": "Cheval AZ 6",
                "forme": 7,
                "regularite": 7,
                "gains": 7,
                "jockey": 8,
                "cote": 7,
                "distance": 7,
                "terrain": 8,
                "experience": 7
            },

            {
                "numero": 7,
                "nom": "Cheval AZ 7",
                "forme": 8,
                "regularite": 8,
                "gains": 7,
                "jockey": 7,
                "cote": 8,
                "distance": 8,
                "terrain": 7,
                "experience": 8
            }

        ]


        resultat = lancer_analyse(chevaux)


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
            detail=str(e)
        )
