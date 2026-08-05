# =====================================
# AZ TURF PRO
# API
# Analyse + Premium
# =====================================

from fastapi import APIRouter, HTTPException
from engine import lancer_analyse

from database import (
    creer_abonnement,
    activer_abonnement,
    verifier_premium,
    lister_abonnements,
    statistiques_abonnements
)

from models import (
    AbonnementRequest,
    ActivationRequest
)

import json
import os
from datetime import datetime, timedelta



router = APIRouter(
    prefix="/api",
    tags=["AZ Turf"]
)



# =====================================
# ANALYSE AZ TURF
# =====================================

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

        classement = resultat.get(
            "chevaux",
            []
        )

        return {
            "message": "Analyse AZ Turf terminée",
            "course": course.get("course", "Course"),
            "date": course.get("date", ""),
            "hippodrome": course.get("hippodrome", ""),
            "discipline": course.get("discipline", ""),
            "distance": course.get("distance_course", ""),
            "plus_joues": course.get("plus_joues", []),
            "source_plus_joues": course.get("source_plus_joues", ""),
            "partants": len(chevaux),
            "chevaux": classement,
            "classement": classement,
            "favori": classement[0] if classement else {},
            "tickets": resultat.get("tickets", {})
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Erreur AZ : {str(e)}"
        )





# =====================================
# CREATION ABONNEMENT PREMIUM
# =====================================

@router.post("/abonnement")
def abonnement(data: AbonnementRequest):

    try:

        resultat = creer_abonnement(
            data.model_dump()
        )

        return {

            "message": "Abonnement enregistré",

            "abonnement": resultat

        }


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )





# =====================================
# ACTIVATION PREMIUM ADMIN
# =====================================

@router.post("/activation")
def activation_premium(
    activation: ActivationRequest
):

    abonnement = activer_abonnement(
        activation.telephone,
        activation.reference
    )


    if abonnement is None:

        raise HTTPException(
            status_code=404,
            detail="Aucun abonnement trouvé"
        )



    abonnement["date_fin"] = (
        datetime.now()
        +
        timedelta(
            days=int(
                abonnement.get(
                    "duree",
                    30
                )
            )
        )
    ).isoformat()



    return {

        "message":
        "Premium activé",

        "statut":
        "ACTIF",

        "date_fin":
        abonnement["date_fin"]

    }





# =====================================
# VERIFICATION PREMIUM
# =====================================

@router.get("/premium/{telephone}")
def premium(
    telephone: str
):

    return verifier_premium(
        telephone
    )
# =====================================
# ADMIN - ABONNEMENTS
# =====================================

@router.get("/admin/abonnements")
def admin_abonnements():

    return {
        "abonnements": lister_abonnements()
    }
# =====================================
# ADMIN - STATISTIQUES
# =====================================

@router.get("/admin/statistiques")
def admin_statistiques():

    return statistiques_abonnements()
