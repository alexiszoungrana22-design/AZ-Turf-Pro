# =====================================
# AZ TURF PRO
# API
# Analyse + Premium
# =====================================
#
# CORRECTIONS APPORTEES A CETTE VERSION (rien d'autre n'a change) :
#
# 1. charger_course() ne fige plus reunion="R1"/course_numero="C1"
#    en dur : ces valeurs sont desormais laissees a
#    charger_course_pmu(), qui lit le vrai programme du jour et
#    choisit la premiere reunion/course reellement disponible
#    (cf. pmu_source.py corrige). Avant, meme si R1/C1 n'existait
#    pas ce jour-la, on ne le savait jamais - PMU echouait toujours
#    silencieusement et on retombait sur courses.json.
#
# 2. Quand la source reelle echoue et qu'on retombe sur
#    courses.json, la reponse de /api/analyse indique desormais
#    clairement qu'il s'agit de donnees de demonstration (source
#    "demo" + message explicite + date_demo separee de la date du
#    jour), pour ne jamais laisser croire que c'est la course
#    actuelle. Toutes les autres routes (abonnement, activation,
#    premium, admin) sont strictement inchangees.


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
# CHARGEMENT COURSE
# PMU PRIORITAIRE + FALLBACK LOCAL
# =====================================

def charger_course():

    aujourd_hui = datetime.now()

    # Format attendu par l'API PMU
    date_pmu = aujourd_hui.strftime(
        "%d%m%Y"
    )

    # =================================
    # 1. TENTATIVE PMU
    # reunion/course_numero ne sont plus
    # fixes en dur : charger_course_pmu()
    # determine elle-meme la premiere
    # reunion/course reellement
    # disponible dans le programme du
    # jour si on ne lui impose rien.
    # =================================

    try:

        course = charger_course_pmu(
            date_pmu
        )

        if (
            course
            and isinstance(course, dict)
            and course.get("chevaux")
        ):

            print(
                "Source utilisÃ©e : PMU rÃ©el"
            )

            return course, "pmu_live"

    except Exception as erreur:

        print(
            "PMU indisponible :",
            erreur
        )

    # =================================
    # 2. FALLBACK LOCAL
    # Marque explicitement comme donnee
    # de demonstration : ne doit jamais
    # etre presentee comme la course du
    # jour.
    # =================================

    try:

        course = charger_course_locale()

        if (
            course
            and isinstance(course, dict)
            and course.get("chevaux")
        ):

            print(
                "Source utilisÃ©e : donnÃ©es locales (dÃ©mo)"
            )

            course["donnees_demo"] = True

            return course, "demo"

    except Exception as erreur:

        print(
            "Erreur chargement local :",
            erreur
        )

    return None, "none"


# =====================================
# ANALYSE AZ TURF
# =====================================

@router.get("/analyse")
def analyse():

    try:

        # =================================
        # 1. CHARGEMENT DES DONNÃ‰ES
        # =================================

        course, source = charger_course()

        if not course:

            raise HTTPException(
                status_code=503,
                detail=(
                    "Aucune donnÃ©e de course "
                    "disponible actuellement."
                )
            )

        # =================================
        # 2. CHEVAUX
        # =================================

        chevaux = course.get(
            "chevaux",
            []
        )

        if not chevaux:

            raise HTTPException(
                status_code=503,
                detail=(
                    "Aucun cheval trouvÃ© "
                    "dans la course."
                )
            )

        # =================================
        # 3. MOTEUR AZ
        # =================================

        resultat = lancer_analyse(
            chevaux
        )

        if not isinstance(
            resultat,
            dict
        ):
            raise Exception(
                "RÃ©ponse invalide du moteur AZ"
            )

        classement = resultat.get(
            "chevaux",
            []
        )

        if not classement:

            raise Exception(
                "Le moteur AZ n'a retournÃ© "
                "aucun classement."
            )

        # =================================
        # 4. INFORMATIONS COURSE
        # =================================

        aujourd_hui = datetime.now()

        est_demo = (source == "demo")

        date_course = (
            course.get("date")
            or aujourd_hui.strftime(
                "%Y-%m-%d"
            )
        )

        reunion = (
            course.get("reunion")
            or "R1"
        )

        course_numero = (
            course.get("course_numero")
            or "C1"
        )

        # =================================
        # 5. RÃ‰PONSE API
        # =================================

        reponse = {

            "message": (
                "Analyse AZ Turf terminÃ©e"
                if not est_demo else
                "Analyse AZ Turf terminÃ©e "
                "(donnÃ©es de dÃ©monstration, "
                "aucune course rÃ©elle "
                "disponible actuellement)"
            ),

            "source":
                source,

            # Indique explicitement au frontend
            # qu'il ne s'agit pas d'une course
            # reelle du jour, pour eviter toute
            # confusion.
            "donnees_demo":
                est_demo,

            "course":
                course.get(
                    "course",
                    "Course"
                ),

            "date":
                date_course,

            "reunion":
                reunion,

            "course_numero":
                course_numero,

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
                    "Non disponible"
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

        if est_demo:

            reponse["avertissement"] = (
                "Ces donnÃ©es sont des donnÃ©es de "
                "dÃ©monstration figÃ©es et ne "
                "correspondent pas Ã  une course "
                "rÃ©elle du jour."
            )

        return reponse

    except HTTPException:
        raise

    except Exception as erreur:

        print(
            "Erreur analyse AZ :",
            erreur
        )

        raise HTTPException(

            status_code=500,

            detail=(
                "Erreur AZ : "
                f"{str(erreur)}"
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
                "Abonnement enregistrÃ©",

            "abonnement":
                resultat

        }

    except Exception as erreur:

        raise HTTPException(

            status_code=500,

            detail=str(erreur)

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
                "Aucun abonnement trouvÃ©"

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
            "Premium activÃ©",

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
