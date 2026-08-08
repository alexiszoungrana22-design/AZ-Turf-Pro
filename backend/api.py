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

from pmu_source import charger_course_pmu

import json
import os
from datetime import datetime, timedelta


router = APIRouter(
    prefix="/api",
    tags=["AZ Turf"]
)


# =====================================
# CHARGEMENT COURSE LOCALE
# =====================================

def charger_course_locale():

    chemin = os.path.join(
        os.path.dirname(__file__),
        "data",
        "courses.json"
    )

    with open(
        chemin,
        "r",
        encoding="utf-8"
    ) as fichier:

        return json.load(fichier)


# =====================================
# ANALYSE AZ TURF
# =====================================

@router.get("/analyse")
def analyse():

    source = "local"

    try:

        # ---------------------------------
        # 1. Tentative PMU
        # ---------------------------------

        aujourd_hui = datetime.now()

        date_pmu = aujourd_hui.strftime("%d%m%Y")

        reunion = "R1"
        course_numero = "C1"

        course = None

        try:

            course = charger_course_pmu(
                date_pmu,
                reunion,
                course_numero
            )

        except Exception:

            course = None


        # ---------------------------------
        # 2. Vérification des données PMU
        # ---------------------------------

        if (
            course
            and isinstance(course, dict)
            and course.get("chevaux")
        ):

            source = "pmu_live"

        else:

            # ---------------------------------
            # 3. Fallback courses.json
            # ---------------------------------

            course = charger_course_locale()

            source = "local"


        chevaux = course.get(
            "chevaux",
            []
        )


        if not chevaux:

            raise Exception(
                "Aucun cheval trouvé dans la course"
            )


        # ---------------------------------
        # 4. Moteur AZ
        # ---------------------------------

        resultat = lancer_analyse(
            chevaux
        )


        classement = resultat.get(
            "chevaux",
            []
        )


        # ---------------------------------
        # 5. Réponse API
        # ---------------------------------

        return {

            "message":
                "Analyse AZ Turf terminée",

            "source":
                source,

            "course":
                course.get(
                    "course",
                    "Course"
                ),

            "date":
                course.get(
                    "date",
                    ""
                ),

            "reunion":
                course.get(
                    "reunion",
                    reunion
                ),

            "course_numero":
                course.get(
                    "course_numero",
                    course_numero
                ),

            "hippodrome":
                course.get(
                    "hippodrome",
                    ""
                ),

            "discipline":
                course.get(
                    "discipline",
                    ""
                ),

            "distance":
                course.get(
                    "distance_course",
                    ""
                ),

            "allocation":
                course.get(
                    "allocation",
                    ""
                ),

            "plus_joues":
                course.get(
                    "plus_joues",
                    []
                ),

            "source_plus_joues":
                course.get(
                    "source_plus_joues",
                    ""
                ),

            "partants":
                len(chevaux),

            "chevaux":
                classement,

            "classement":
                classement,

            "favori": (
                classement[0]
                if classement
                else {}
            ),

            "tickets":
                resultat.get(
                    "tickets",
                    {}
                )

        }


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=(
                "Erreur AZ : "
                f"{str(e)}"
            )

        )


# =====================================
# CREATION ABONNEMENT PREMIUM
# =====================================

@router.post("/abonnement")
def abonnement(
    data: AbonnementRequest
):

    try:

        resultat = creer_abonnement(
            data.model_dump()
        )

        return {

            "message":
                "Abonnement enregistré",

            "abonnement":
                resultat

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

            detail=
                "Aucun abonnement trouvé"

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

        "abonnements":
            lister_abonnements()

    }


# =====================================
# ADMIN - STATISTIQUES
# =====================================

@router.get("/admin/statistiques")
def admin_statistiques():

    return statistiques_abonnements()
