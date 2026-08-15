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

from lonab_source import recuperer_journal_lonab, diagnostiquer_journal_lonab

from learning import lire_historique, mettre_a_jour_arrivee

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
                "Source utilisée : PMU réel"
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
                "Source utilisée : données locales (démo)"
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
        # 1. CHARGEMENT DES DONNÉES
        # =================================

        course, source = charger_course()

        if not course:

            raise HTTPException(
                status_code=503,
                detail=(
                    "Aucune donnée de course "
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
                    "Aucun cheval trouvé "
                    "dans la course."
                )
            )

        # =================================
        # 3. MOTEUR AZ
        # =================================

        resultat = lancer_analyse(
            chevaux,
            info_course={
                "date": course.get("date"),
                "reunion": course.get("reunion"),
                "course_numero": course.get("course_numero"),
                "course": course.get("course", ""),
                "hippodrome": course.get("hippodrome"),
                "discipline": course.get("discipline", ""),
                "distance": course.get("distance_course", ""),
                "allocation": course.get("allocation", ""),
                "heure_depart": course.get("heure_depart", ""),
                "horaires": course.get("horaires", {}),
            }
        )

        if not isinstance(
            resultat,
            dict
        ):
            raise Exception(
                "Réponse invalide du moteur AZ"
            )

        classement = resultat.get(
            "chevaux",
            []
        )

        if not classement:

            raise Exception(
                "Le moteur AZ n'a retourné "
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
        # 5. RÉPONSE API
        # =================================

        reponse = {

            "message": (
                "Analyse AZ Turf terminée"
                if not est_demo else
                "Analyse AZ Turf terminée "
                "(données de démonstration, "
                "aucune course réelle "
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

            "heure_depart":
                course.get("heure_depart", ""),

            "horaires":
                course.get("horaires", {"depart": course.get("heure_depart", ""), "arret_des_jeux": ""}),

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

            "non_partants":
                course.get(
                    "non_partants",
                    []
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
                "Ces données sont des données de "
                "démonstration figées et ne "
                "correspondent pas à  une course "
                "réelle du jour."
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
                "Abonnement enregistré",

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


# =====================================
# JOURNAL HIPPIQUE (LONAB)
# =====================================
#
# Route additive : n'affecte aucune route existante ci-dessus.

@router.get("/journal")
def journal():

    try:

        aujourd_hui = datetime.now()

        resultat = recuperer_journal_lonab(
            aujourd_hui
        )

        if not resultat:

            raise HTTPException(
                status_code=503,
                detail=(
                    "Journal hippique LONAB indisponible "
                    "actuellement."
                )
            )

        return resultat

    except HTTPException:
        raise

    except Exception as erreur:

        print(
            "Erreur journal LONAB :",
            erreur
        )

        raise HTTPException(

            status_code=500,

            detail=(
                "Erreur journal : "
                f"{str(erreur)}"
            )

        )


# =====================================
# DEBUG TEMPORAIRE - JSON BRUT PMU
# =====================================
#
# Route temporaire, a retirer une fois le probleme d'hippodrome
# resolu. Retourne le dict "course" brut tel que recu de l'API PMU,
# AVANT toute transformation, pour identifier le vrai nom du champ
# hippodrome dans le schema reel de l'API client/61.

@router.get("/debug-pmu")
def debug_pmu():

    from pmu_source import trouver_quinte_du_jour

    aujourd_hui = datetime.now()
    date_pmu = aujourd_hui.strftime("%d%m%Y")

    try:

        programme, reunion, course = trouver_quinte_du_jour(
            date_pmu
        )

        return {
            "reunion": reunion,
            "programme_brut": programme,
            "course_brute": course,
        }

    except Exception as erreur:

        raise HTTPException(
            status_code=500,
            detail=f"Erreur debug PMU : {erreur}"
        )


# =====================================
# DEBUG TEMPORAIRE - JOURNAL LONAB
# =====================================
#
# Route temporaire, a retirer une fois le journal fonctionnel.
# Montre precisement a quelle etape la recuperation LONAB echoue.

@router.get("/debug-journal")
def debug_journal():

    aujourd_hui = datetime.now()

    try:

        diagnostic = diagnostiquer_journal_lonab(
            aujourd_hui
        )

        return diagnostic

    except Exception as erreur:

        raise HTTPException(
            status_code=500,
            detail=f"Erreur debug journal : {erreur}"
        )


# =====================================
# HISTORIQUE (SELECTION + RESULTATS)
# =====================================
#
# Route additive : n'affecte aucune route existante. Lit
# data/historique_az.json (rempli automatiquement par
# engine.lancer_analyse a chaque appel de /api/analyse) et tente
# de completer le vrai resultat (arrivee) des entrees passees dont
# la course est desormais terminee.
#
# LIMITE CONNUE : si l'hebergement Render ne dispose pas d'un
# disque persistant, ce fichier peut etre remis a zero a chaque
# redeploiement - l'historique ne survit alors pas dans le temps.

@app.route('/api/historique', methods=['GET'])
def api_historique():
    return jsonify(voir_historique())
    
@router.get("/historique")
def historique():

    try:

        entrees = lire_historique()

        for index, entree in enumerate(entrees):

            if entree.get("arrivee"):
                continue

            info_course = entree.get("course") or {}

            date = info_course.get("date")
            reunion = info_course.get("reunion")
            course_numero = info_course.get("course_numero")

            if not (date and reunion and course_numero):
                continue

            try:

                from pmu_source import recuperer_arrivee_pmu

                arrivee = recuperer_arrivee_pmu(
                    date, reunion, course_numero
                )

                if arrivee:
                    mettre_a_jour_arrivee(index, arrivee)
                    entree["arrivee"] = arrivee

            except Exception:
                pass

        return {
            "historique": list(reversed(entrees))
        }

    except Exception as erreur:

        raise HTTPException(
            status_code=500,
            detail=f"Erreur historique : {erreur}"
)
            
