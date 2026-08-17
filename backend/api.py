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
import re
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
# ACTUALITES / ARRIVEES HISTORIQUES
# =====================================

def _normaliser_arrivee(arrivee):
    """Normalise une arrivee provenant de PMU/LONAB pour le frontend."""
    if not arrivee:
        return None

    if isinstance(arrivee, dict):
        resultat = dict(arrivee)
        arrivee_val = (
            resultat.get("arrivee")
            or resultat.get("ordre")
            or resultat.get("resultat")
            or resultat.get("numeros")
            or resultat.get("numbers")
        )
        if isinstance(arrivee_val, str):
            arrivee_val = [x.strip() for x in arrivee_val.replace(",", "-").split("-") if x.strip()]
        if isinstance(arrivee_val, (list, tuple)):
            resultat["arrivee"] = [str(x) for x in arrivee_val]
        return resultat if resultat.get("arrivee") else None

    if isinstance(arrivee, (list, tuple)):
        return {"arrivee": [str(x) for x in arrivee]}

    if isinstance(arrivee, str):
        nums = [x.strip() for x in arrivee.replace(",", "-").split("-") if x.strip()]
        return {"arrivee": nums} if nums else None

    return None


def _course_terminee(info_course):
    """Retourne True si la course est suffisamment ancienne pour chercher son arrivÃ©e."""
    if not isinstance(info_course, dict):
        return False

    date_str = str(info_course.get("date") or "").strip()
    heure = str(info_course.get("heure_depart") or "").strip()

    try:
        if re.match(r"^\d{8}$", date_str):
            dt = datetime.strptime(date_str, "%d%m%Y")
        else:
            dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
    except Exception:
        return False

    if heure:
        m = re.search(r"(\d{1,2})\s*[hH:](?:\s*(\d{1,2}))?", heure)
        if m:
            h = int(m.group(1))
            minute = int(m.group(2) or 0)
            dt = dt.replace(hour=h, minute=minute)

    return datetime.now() >= dt + timedelta(hours=2)


def _actualites_historique():
    """
    Recharge les arrivees des courses historiques non encore completees.
    Cette fonction est appelee aussi par /api/journal afin que la carte
    'Dernieres arrivees' ne reste pas bloquee sur le dernier PDF LONAB.
    """
    try:
        entrees = lire_historique() or []
    except Exception as erreur:
        print("Lecture historique pour journal impossible :", erreur)
        return []

    actualites = []

    for index, entree in enumerate(entrees):
        if not isinstance(entree, dict):
            continue

        info = entree.get("course") or {}
        if not _course_terminee(info):
            continue

        arrivee = _normaliser_arrivee(entree.get("arrivee"))

        if not arrivee:
            try:
                from pmu_source import recuperer_arrivee_pmu
                brut = recuperer_arrivee_pmu(
                    info.get("date"),
                    info.get("reunion"),
                    info.get("course_numero")
                )
                arrivee = _normaliser_arrivee(brut)
            except Exception as erreur:
                print("Arrivee PMU historique indisponible :", erreur)

            if arrivee:
                try:
                    mettre_a_jour_arrivee(index, arrivee)
                except Exception as erreur:
                    print("Mise a jour arrivee impossible :", erreur)

        if not arrivee:
            continue

        actualites.append({
            "type_pari": info.get("type_pari") or "QUINTE+",
            "date": info.get("date") or "",
            "course": info.get("course") or "Course",
            "reunion": info.get("reunion") or "",
            "course_numero": info.get("course_numero") or "",
            "arrivee": arrivee.get("arrivee", [])[:5],
            "rapport": arrivee.get("rapport") or arrivee.get("rapports") or {},
            "source": arrivee.get("source") or "pmu",
        })

    return actualites


def _fusionner_actualites(journal):
    """Fusionne les actualites LONAB du jour avec l'historique AZ."""
    if not isinstance(journal, dict):
        return journal

    existantes = journal.get("actualites") or []
    historiques = _actualites_historique()

    fusion = []
    cles = set()

    for item in existantes + historiques:
        if not isinstance(item, dict):
            continue
        arrivee = item.get("arrivee") or []
        cle = (
            str(item.get("date") or ""),
            str(item.get("course") or item.get("type_pari") or ""),
            tuple(str(x) for x in arrivee[:5]),
        )
        if cle in cles:
            continue
        cles.add(cle)
        fusion.append(item)

    def cle_date(item):
        valeur = str(item.get("date") or "")
        try:
            if re.match(r"^\d{8}$", valeur):
                return datetime.strptime(valeur, "%d%m%Y")
            return datetime.strptime(valeur[:10], "%Y-%m-%d")
        except Exception:
            return datetime.min

    fusion.sort(key=cle_date, reverse=True)
    journal["actualites"] = fusion[:20]
    journal["dernieres_arrivees"] = fusion[:20]

    # Les rapports historiques deviennent Ã©galement accessibles au frontend.
    rapports = [
        item for item in fusion
        if item.get("rapport")
    ]
    journal["rapports"] = rapports[:20]

    return journal


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
                "Ces donnÃ©es sont des donnÃ©es de "
                "dÃ©monstration figÃ©es et ne "
                "correspondent pas Ã   une course "
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

        # Ne pas dependre uniquement du PDF du jour : les arrivees
        # des courses deja analysees sont rechargees depuis l historique.
        if resultat:
            resultat = _fusionner_actualites(resultat)
        else:
            # Meme si le PDF LONAB du jour est temporairement indisponible,
            # le journal peut encore afficher les dernieres arrivees connues.
            resultat = _fusionner_actualites({
                "source": "historique",
                "actualites": [],
                "masses_a_partager": [],
            })

        if not resultat or not (resultat.get("actualites") or resultat.get("entete")):

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
