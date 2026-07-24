from fastapi import APIRouter, HTTPException
from engine import lancer_analyse
import json
import os


router = APIRouter(
    prefix="/api",
    tags=["AZ Turf"]
)


@router.get("/analyse")
def analyse():

    try:

        chemin = os.path.join(
            "data",
            "courses.json"
        )


        with open(
            chemin,
            "r",
            encoding="utf-8"
        ) as fichier:

            course = json.load(fichier)



        chevaux = course.get(
            "chevaux",
            []
        )



        resultat = lancer_analyse(
            chevaux
        )



        return {

            "message": "Analyse AZ Turf terminée",

            "course": course.get(
                "course",
                "Course AZ"
            ),

            "date": course.get(
                "date",
                ""
            ),

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
