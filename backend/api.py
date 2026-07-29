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


        if not chevaux:
            raise Exception(
                "Aucun cheval trouvé dans courses.json"
            )


        resultat = lancer_analyse(
            chevaux
        )


        print("RESULTAT ENGINE :", resultat)


        return {

            "message": "Analyse AZ Turf terminée",

            "course": course.get(
                "course",
                "Course"
            ),

            "date": course.get(
                "date",
                ""
            ),

            "reunion": course.get(
                "reunion",
                ""
            ),

            "course_numero": course.get(
                "course_numero",
                ""
            ),

            "hippodrome": course.get(
                "hippodrome",
                ""
            ),

            "discipline": course.get(
                "discipline",
                ""
            ),

            "distance_course": course.get(
                "distance_course",
                0
            ),

            "allocation": course.get(
                "allocation",
                0
            ),

            "partants": len(chevaux),


            "chevaux": resultat.get(
                "chevaux",
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
            ),


            "plus_joues": course.get(
                "plus_joues",
                []
            ),

            "source_plus_joues": course.get(
                "source_plus_joues",
                "Turf.fr"
            )

        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Erreur AZ : {str(e)}"
        )
