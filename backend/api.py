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

from pmu_source import charger_course_pmu, recuperer_programme, trouver_reunion, trouver_course

from lonab_source import recuperer_journal_lonab, diagnostiquer_journal_lonab

from learning import lire_historique, mettre_a_jour_arrivee

from modules.chatbot_turf import repondre_assistant_turf
from modules.stats_backtest import calculer_stats_performance, simuler_backtest_filtre

import json
import os
from datetime import datetime, timedelta


router = APIRouter(
    prefix="/api",
    tags=["AZ Turf"]
)


# =====================================
# CHARGEMENT COURSE PMU LIVE
# =====================================

def charger_course():
    """
    Charge uniquement la course rÃ©elle depuis PMU.

    Important : aucune donnÃ©e de demonstration locale n'est utilisÃ©e
    automatiquement. Cela empÃªche une ancienne course de courses.json
    d'Ãªtre prÃ©sentÃ©e comme la course du jour lorsque PMU est indisponible.
    """
    date_pmu = datetime.now().strftime("%d%m%Y")

    try:
        course = charger_course_pmu(date_pmu)
    except Exception as erreur:
        print("PMU indisponible :", erreur)
        return None, "none"

    if not isinstance(course, dict) or not course.get("chevaux"):
        print("PMU : aucune course exploitable pour", date_pmu)
        return None, "none"

    print("Source utilisee : PMU reel")
    return course, "pmu_live"


def _charger_partants_live():
    """Retourne la course et ses partants depuis PMU, sans fallback local."""
    course, source = charger_course()
    if source != "pmu_live" or not course:
        raise HTTPException(
            status_code=503,
            detail="Les donnÃ©es PMU rÃ©elles du jour sont indisponibles actuellement."
        )
    return course



# =====================================
# HORAIRE PMU DE LA COURSE
# =====================================

def _recuperer_horaire_course(course):
    """RÃ©cupÃ¨re l'heure brute de dÃ©part depuis le programme PMU.
    Le module pmu_source reste inchangÃ© ; on enrichit seulement la rÃ©ponse API.
    """
    if not isinstance(course, dict):
        return {"depart": "", "arret_des_jeux": ""}

    date = course.get("date")
    reunion = course.get("reunion")
    numero = course.get("course_numero")
    if not date or not reunion or not numero:
        return {"depart": "", "arret_des_jeux": ""}

    try:
        programme = recuperer_programme(date, reunion)
        reunion_data = trouver_reunion(programme, reunion)
        course_brute = trouver_course(reunion_data, numero)
        if not isinstance(course_brute, dict):
            return {"depart": "", "arret_des_jeux": ""}

        def premier(*cles):
            for cle in cles:
                valeur = course_brute.get(cle)
                if valeur not in (None, ""):
                    return valeur
            return ""

        depart = premier(
            "heureDepart", "heureDepartPrevue", "heureDepartCourse",
            "heure_depart", "heure", "heureDeDepart"
        )
        arret = premier(
            "heureArretDesJeux", "heureArretJeux",
            "arretDesJeux", "arret_des_jeux"
        )
        return {"depart": depart, "arret_des_jeux": arret}
    except Exception as erreur:
        print("Horaire PMU indisponible :", erreur)
        return {"depart": "", "arret_des_jeux": ""}


# =====================================
# ANALYSE AZ TURF
# =====================================

@router.get("/analyse")
def analyse():

    try:

        # =================================
        # 1. CHARGEMENT DES DONNÃƒâ€°ES
        # =================================

        course, source = charger_course()

        if not course:

            raise HTTPException(
                status_code=503,
                detail=(
                    "Aucune donnÃƒÂ©e de course "
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
                    "Aucun cheval trouvÃƒÂ© "
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
                "hippodrome": course.get("hippodrome"),
            }
        )

        if not isinstance(
            resultat,
            dict
        ):
            raise Exception(
                "RÃƒÂ©ponse invalide du moteur AZ"
            )

        classement = resultat.get(
            "chevaux",
            []
        )

        if not classement:

            raise Exception(
                "Le moteur AZ n'a retournÃƒÂ© "
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
        # 5. RÃƒâ€°PONSE API
        # =================================

        reponse = {

            "message": (
                "Analyse AZ Turf terminÃƒÂ©e"
                if not est_demo else
                "Analyse AZ Turf terminÃƒÂ©e "
                "(donnÃƒÂ©es de dÃƒÂ©monstration, "
                "aucune course rÃƒÂ©elle "
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

            "horaires":
                _recuperer_horaire_course(course),

            "heure_depart":
                _recuperer_horaire_course(course).get("depart", ""),

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
                "Ces donnÃƒÂ©es sont des donnÃƒÂ©es de "
                "dÃƒÂ©monstration figÃƒÂ©es et ne "
                "correspondent pas Ãƒ  une course "
                "rÃƒÂ©elle du jour."
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
# PARTANTS PMU LIVE
# =====================================

@router.get("/partants")
def partants():
    """Retourne les partants de la course PMU rÃ©elle du jour."""
    try:
        course = _charger_partants_live()
        chevaux = course.get("chevaux", [])

        return {
            "source": "pmu_live",
            "donnees_demo": False,
            "course": course.get("course", ""),
            "date": course.get("date") or datetime.now().strftime("%d%m%Y"),
            "reunion": course.get("reunion", ""),
            "course_numero": course.get("course_numero", ""),
            "hippodrome": course.get("hippodrome", ""),
            "discipline": course.get("discipline", ""),
            "distance": course.get("distance_course", ""),
            "allocation": course.get("allocation", ""),
            "horaires": _recuperer_horaire_course(course),
            "heure_depart": _recuperer_horaire_course(course).get("depart", ""),
            "non_partants": course.get("non_partants", []),
            "partants": len(chevaux),
            "chevaux": chevaux,
        }
    except HTTPException:
        raise
    except Exception as erreur:
        print("Erreur partants PMU :", erreur)
        raise HTTPException(status_code=500, detail=f"Erreur partants : {erreur}")


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
                "Abonnement enregistrÃƒÂ©",

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
                "Aucun abonnement trouvÃƒÂ©"

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
            "Premium activÃƒÂ©",

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
# ASSISTANT TURF
# =====================================

@router.post("/assistant/chat")
def assistant_chat(payload: dict):
    """RÃ©pond aux questions Ã  partir de l'analyse courante."""
    question = str(payload.get("question", "")).strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question obligatoire.")

    contexte = payload.get("contexte") or {}
    moteur = contexte.get("moteur")

    if not moteur:
        base, source = charger_course()
        if not base:
            raise HTTPException(
                status_code=503,
                detail="Aucune analyse PMU rÃ©elle disponible actuellement."
            )
        resultat = lancer_analyse(
            base.get("chevaux", []),
            info_course={
                "date": base.get("date"),
                "reunion": base.get("reunion"),
                "course_numero": base.get("course_numero"),
                "hippodrome": base.get("hippodrome"),
            },
        )
        moteur = {
            "classement": resultat.get("chevaux", []),
            "tickets": resultat.get("tickets", {}),
        }

    return repondre_assistant_turf(question, {"moteur": moteur})


# =====================================
# STATISTIQUES / BACKTEST
# =====================================

@router.post("/stats/backtest")
def stats_backtest(payload: dict):
    """Calcule les performances et le backtest sur l'historique fourni ou local."""
    historique = payload.get("historique")
    if not isinstance(historique, list) or not historique:
        historique = lire_historique()

    filtres = payload.get("filtres") or {}
    resultat = simuler_backtest_filtre(historique, filtres)
    resultat["performance"] = calculer_stats_performance(historique)
    return resultat


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

@router.get("/historique")
def historique():

    try:

        entrees = lire_historique()

        for index, entree in enumerate(entrees):

            if entree.get("arrivee") is not None:
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
