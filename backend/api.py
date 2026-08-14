# =====================================
# AZ TURF PRO
# API
# Analyse + Premium
# =====================================
#
# Fichier complet : api.py
#
# CORRECTIONS APPORTEES SUR LA SECTION "NOUVELLES ROUTES" :
#
# - L'URL LONAB utilisee ("www.lonab.bf/journal-hippique") etait
#   fausse. La vraie URL, deja testee en direct avec succes, est
#   "https://lonab.bf/programme-pmub" (sans www, chemin different).
#   Les routes reutilisent maintenant directement les fonctions
#   deja verifiees de lonab_source.py au lieu de dupliquer un
#   scraper non teste avec httpx/BeautifulSoup.
#
# - "/pdf/programmes/mali" pointait vers "https://pmug.ml/programme.pdf",
#   une URL inventee (jamais vue dans aucune source reelle). Remplacee
#   par une vraie source verifiee : https://pmu.malijet.com (PMU
#   officiel du Mali, en partenariat avec Malijet.com), via le
#   nouveau module isole mali_source.py, teste sur de vraies donnees.
#
# - "/pdf/programmes/niger" retiree : aucune source fiable et
#   verifiable trouvee. Mieux vaut ne pas avoir cette route que
#   d'en avoir une qui pointe vers une URL inventee.
#
# - "/bruits-ecurie" retiree : son contenu etait entierement
#   fabrique ("Repere ce matin lors des derniers heats...", texte
#   fixe, jamais issu d'une vraie source). Presenter ca comme une
#   vraie information a des utilisateurs qui parient est trompeur.
#
# Tout le reste du fichier (routes /analyse, /abonnement,
# /activation, /premium, /admin/*, /journal, /historique,
# /debug-pmu, /debug-journal) est conserve tel quel.


from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

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
from lonab_source import (
    recuperer_journal_lonab,
    diagnostiquer_journal_lonab,
    trouver_url_pdf_du_jour,
)
from learning import lire_historique, mettre_a_jour_arrivee, mettre_a_jour_publications

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
    chemin = os.path.join(os.path.dirname(__file__), "data", "courses.json")
    with open(chemin, "r", encoding="utf-8") as fichier:
        return json.load(fichier)


# =====================================
# CHARGEMENT COURSE
# PMU PRIORITAIRE + FALLBACK LOCAL
# =====================================
def charger_course():
    aujourd_hui = datetime.now()
    date_pmu = aujourd_hui.strftime("%d%m%Y")

    try:
        course = charger_course_pmu(date_pmu)
        if course and isinstance(course, dict) and course.get("chevaux"):
            print("Source utilisÃ©e : PMU rÃ©el")
            return course, "pmu_live"
    except Exception as erreur:
        print("PMU indisponible :", erreur)

    try:
        course = charger_course_locale()
        if course and isinstance(course, dict) and course.get("chevaux"):
            print("Source utilisÃ©e : donnÃ©es locales (dÃ©mo)")
            course["donnees_demo"] = True
            return course, "demo"
    except Exception as erreur:
        print("Erreur chargement local :", erreur)

    return None, "none"


# =====================================
# ANALYSE AZ TURF
# =====================================
@router.get("/analyse")
def analyse():
    try:
        course, source = charger_course()
        if not course:
            raise HTTPException(status_code=503, detail="Aucune donnÃ©e de course disponible actuellement.")

        chevaux = course.get("chevaux", [])
        if not chevaux:
            raise HTTPException(status_code=503, detail="Aucun cheval trouvÃ© dans la course.")

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
                "non_partants": course.get("non_partants", []),
            }
        )

        if not isinstance(resultat, dict):
            raise Exception("RÃ©ponse invalide du moteur AZ")

        classement = resultat.get("chevaux", [])
        if not classement:
            raise Exception("Le moteur AZ n'a retournÃ© aucun classement.")

        aujourd_hui = datetime.now()
        est_demo = (source == "demo")
        date_course = (course.get("date") or aujourd_hui.strftime("%Y-%m-%d"))
        reunion = (course.get("reunion") or "R1")
        course_numero = (course.get("course_numero") or "C1")

        reponse = {
            "message": "Analyse AZ Turf terminÃ©e" if not est_demo else "Analyse AZ Turf terminÃ©e (donnÃ©es de dÃ©monstration, aucune course rÃ©elle disponible actuellement)",
            "source": source,
            "donnees_demo": est_demo,
            "course": course.get("course", "Course"),
            "date": date_course,
            "reunion": reunion,
            "course_numero": course_numero,
            "heure_depart": course.get("heure_depart", ""),
            "horaires": course.get("horaires", {"depart": course.get("heure_depart", ""), "arret_des_jeux": ""}),
            "hippodrome": course.get("hippodrome", ""),
            "discipline": course.get("discipline", ""),
            "distance": course.get("distance_course", ""),
            "allocation": course.get("allocation", ""),
            "non_partants": resultat.get("non_partants", course.get("non_partants", [])),
            "plus_joues": course.get("plus_joues", []),
            "source_plus_joues": course.get("source_plus_joues", "Non disponible"),
            "partants": len(course.get("chevaux", [])),
            "chevaux": classement,
            "partants_complets": resultat.get("partants_complets", course.get("chevaux", [])),
            "classement": classement,
            "favori": (classement[0] if classement else {}),
            "tickets": resultat.get("tickets", {})
        }

        if est_demo:
            reponse["avertissement"] = "Ces donnÃ©es sont des donnÃ©es de dÃ©monstration figÃ©es et ne correspondent pas Ã  une course rÃ©elle du jour."

        return reponse

    except HTTPException:
        raise
    except Exception as erreur:
        print("Erreur analyse AZ :", erreur)
        raise HTTPException(status_code=500, detail=f"Erreur AZ : {str(erreur)}")


# =====================================
# CREATION ABONNEMENT PREMIUM
# =====================================
@router.post("/abonnement")
def abonnement(data: AbonnementRequest):
    try:
        resultat = creer_abonnement(data.model_dump())
        return {"message": "Abonnement enregistrÃ©", "abonnement": resultat}
    except Exception as erreur:
        raise HTTPException(status_code=500, detail=str(erreur))


# =====================================
# ACTIVATION PREMIUM ADMIN
# =====================================
@router.post("/activation")
def activation_premium(activation: ActivationRequest):
    abonnement = activer_abonnement(activation.telephone, activation.reference)
    if abonnement is None:
        raise HTTPException(status_code=404, detail="Aucun abonnement trouvÃ©")

    abonnement["date_fin"] = (datetime.now() + timedelta(days=int(abonnement.get("duree", 30)))).isoformat()
    return {"message": "Premium activÃ©", "statut": "ACTIF", "date_fin": abonnement["date_fin"]}


# =====================================
# VERIFICATION PREMIUM
# =====================================
@router.get("/premium/{telephone}")
def premium(telephone: str):
    return verifier_premium(telephone)


# =====================================
# ADMIN - ABONNEMENTS
# =====================================
@router.get("/admin/abonnements")
def admin_abonnements():
    return {"abonnements": lister_abonnements()}


# =====================================
# ADMIN - STATISTIQUES
# =====================================
@router.get("/admin/statistiques")
def admin_statistiques():
    return statistiques_abonnements()


# =====================================
# JOURNAL HIPPIQUE (LONAB) - CLASSIQUE
# =====================================
@router.get("/journal")
def journal():
    try:
        aujourd_hui = datetime.now()
        resultat = recuperer_journal_lonab(aujourd_hui)
        if not resultat:
            raise HTTPException(status_code=503, detail="Journal hippique LONAB indisponible actuellement.")

        actualites_az = []
        try:
            mettre_a_jour_publications()
            historiques = lire_historique()
            for entree in reversed(historiques):
                if entree.get("publication_statut") != "PUBLIE":
                    continue
                tickets = entree.get("tickets") or {}
                course = entree.get("course") or {}
                arrivee = entree.get("arrivee") or []
                actualites_az.append({
                    "date": entree.get("date_analyse", ""),
                    "course": course,
                    "selection_az": entree.get("selection_az") or (tickets.get("gratuit") or {}).get("quinte") or [],
                    "arrivee_quinte": arrivee[:5] if isinstance(arrivee, list) else [],
                    "tickets": tickets,
                    "heure_arrivee": entree.get("heure_arrivee"),
                    "date_publication": entree.get("date_publication"),
                    "titre": "RÃ©sultat et analyse AZ Turf Pro",
                    "statut": "PUBLIE",
                })
        except Exception as erreur:
            print("Actualites AZ indisponibles :", erreur)

        resultat["actualites_az"] = actualites_az
        return resultat
    except HTTPException:
        raise
    except Exception as erreur:
        print("Erreur journal LONAB :", erreur)
        raise HTTPException(status_code=500, detail=f"Erreur journal : {str(erreur)}")


# =====================================
# DEBUG TEMPORAIRE - JSON BRUT PMU
# =====================================
@router.get("/debug-pmu")
def debug_pmu():
    from pmu_source import trouver_quinte_du_jour, recuperer_participants, extraire_non_partants

    aujourd_hui = datetime.now()
    date_pmu = aujourd_hui.strftime("%d%m%Y")

    try:
        programme, reunion, course = trouver_quinte_du_jour(date_pmu)

        participants = []
        non_partants = []

        if course:
            course_numero = (
                course.get("numOrdre")
                or course.get("numCourse")
                or course.get("numero")
            )

            if course_numero is not None:
                participants = recuperer_participants(date_pmu, reunion, course_numero)
                non_partants = extraire_non_partants(course, participants)

        return {
            "reunion": reunion,
            "course_brute": course,
            "participants_bruts": participants,
            "non_partants_detectes": non_partants,
        }
    except Exception as erreur:
        raise HTTPException(status_code=500, detail=f"Erreur debug PMU : {erreur}")


# =====================================
# DEBUG TEMPORAIRE - JOURNAL LONAB
# =====================================
@router.get("/debug-journal")
def debug_journal():
    aujourd_hui = datetime.now()
    try:
        diagnostic = diagnostiquer_journal_lonab(aujourd_hui)
        return diagnostic
    except Exception as erreur:
        raise HTTPException(status_code=500, detail=f"Erreur debug journal : {erreur}")


# =====================================
# HISTORIQUE (SELECTION + RESULTATS)
# =====================================
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
                arrivee = recuperer_arrivee_pmu(date, reunion, course_numero)
                if arrivee:
                    mettre_a_jour_arrivee(index, arrivee)
                    entree["arrivee"] = arrivee
            except Exception:
                pass

        try:
            mettre_a_jour_publications()
            entrees = lire_historique()
        except Exception:
            pass

        historique_normalise = []
        for entree in reversed(entrees):
            tickets = entree.get("tickets") or {}
            gratuit = tickets.get("gratuit") or {}
            selection_az = (entree.get("selection_az") or gratuit.get("quinte") or [])
            arrivee = entree.get("arrivee") or []
            entree["selection_az"] = selection_az
            entree["arrivee_quinte"] = (arrivee[:5] if isinstance(arrivee, list) else [])
            entree["publication_statut"] = (entree.get("publication_statut") or ("PUBLIE" if entree.get("arrivee") else "EN ATTENTE"))
            historique_normalise.append(entree)

        return {"historique": historique_normalise}

    except Exception as erreur:
        raise HTTPException(status_code=500, detail=f"Erreur historique : {erreur}")


# =========================================================
# PROGRAMMES ET RESULTATS - SOURCES REELLES VERIFIEES
# =========================================================
#
# Chaque route redirige vers une vraie page/PDF officiel trouve en
# direct au moment de la requete (pas d'URL figee/inventee). Si la
# source est introuvable ce jour-la, retourne une erreur 503
# explicite plutot qu'un lien casse ou une redirection au hasard.


@router.get("/pdf/journal/lonab")
def pdf_journal_lonab_aujourdhui():
    """
    Redirige vers le vrai PDF du journal hippique LONAB du jour
    (source verifiee : https://lonab.bf/programme-pmub). Reutilise
    la fonction deja testee de lonab_source.py - aucune logique de
    scraping dupliquee.
    """

    aujourd_hui = datetime.now()

    try:
        url_pdf = trouver_url_pdf_du_jour(aujourd_hui)

        if not url_pdf:
            raise HTTPException(
                status_code=503,
                detail="Journal hippique LONAB du jour introuvable."
            )

        return RedirectResponse(url=url_pdf)

    except HTTPException:
        raise
    except Exception as erreur:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur rÃ©cupÃ©ration PDF LONAB : {erreur}"
        )


@router.get("/programme/mali")
def programme_mali_aujourdhui():
    """
    Redirige vers la vraie page de programme PMU Mali du jour
    (source verifiee : https://pmu.malijet.com, PMU officiel du
    Mali en partenariat avec Malijet.com).

    Note : contrairement a LONAB, cette source publie des pages
    HTML de detail par course, pas des PDF telechargeables.
    """

    from mali_source import trouver_url_programme_mali_du_jour

    aujourd_hui = datetime.now()

    try:
        url_programme = trouver_url_programme_mali_du_jour(aujourd_hui)

        if not url_programme:
            raise HTTPException(
                status_code=503,
                detail="Programme PMU Mali du jour introuvable."
            )

        return RedirectResponse(url=url_programme)

    except HTTPException:
        raise
    except Exception as erreur:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur rÃ©cupÃ©ration programme Mali : {erreur}"
        )
