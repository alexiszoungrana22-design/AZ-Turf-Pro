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
# Importation corrigÃ©e
from lonab_source import recuperer_journal_lonab, diagnostiquer_journal_lonab

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
# =====================================

def charger_course():
    aujourd_hui = datetime.now()
    date_pmu = aujourd_hui.strftime("%d%m%Y")
    try:
        course = charger_course_pmu(date_pmu)
        if course and isinstance(course, dict) and course.get("chevaux"):
            return course, "pmu_live"
    except Exception as erreur:
        print("PMU indisponible :", erreur)
    try:
        course = charger_course_locale()
        if course and isinstance(course, dict) and course.get("chevaux"):
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
        
        resultat = lancer_analyse(chevaux)
        if not isinstance(resultat, dict):
            raise Exception("RÃ©ponse invalide du moteur AZ")
        
        classement = resultat.get("chevaux", [])
        if not classement:
            raise Exception("Le moteur AZ n'a retournÃ© aucun classement.")

        aujourd_hui = datetime.now()
        est_demo = (source == "demo")
        date_course = course.get("date") or aujourd_hui.strftime("%Y-%m-%d")
        reunion = course.get("reunion") or "R1"
        course_numero = course.get("course_numero") or "C1"

        # =================================
        # 5. RÃ‰PONSE API (CORRIGÃ‰E)
        # =================================
        horaires = {"depart": ""}
        try:
            donnees_lonab = recuperer_journal_lonab(datetime.now())
            if donnees_lonab and "horaires" in donnees_lonab:
                horaires = donnees_lonab["horaires"]
        except Exception as e:
            print("Note : Ã©chec rÃ©cupÃ©ration LONAB :", e)

        reponse = {
            "message": ("Analyse AZ Turf terminÃ©e" if not est_demo else "Analyse AZ Turf terminÃ©e (donnÃ©es de dÃ©monstration)"),
            "source": source,
            "donnees_demo": est_demo,
            "horaires": horaires,
            "course": course.get("course", "Course"),
            "date": date_course,
            "reunion": reunion,
            "course_numero": course_numero,
            "heure_depart": course.get("heure_depart", course.get("heureDepart", "")),
            "hippodrome": course.get("hippodrome", ""),
            "discipline": course.get("discipline", ""),
            "distance": course.get("distance_course", ""),
            "allocation": course.get("allocation", ""),
            "plus_joues": course.get("plus_joues", []),
            "source_plus_joues": course.get("source_plus_joues", "Non disponible"),
            "partants": len(chevaux),
            "chevaux": classement,
            "classement": classement,
            "favori": (classement[0] if classement else {}),
            "tickets": resultat.get("tickets", {})
        }

        if est_demo:
            reponse["avertissement"] = "Ces donnÃ©es sont des donnÃ©es de dÃ©monstration figÃ©es."
        return reponse

    except HTTPException:
        raise
    except Exception as erreur:
        print("Erreur analyse AZ :", erreur)
        raise HTTPException(status_code=500, detail=f"Erreur AZ : {str(erreur)}")

# =====================================
# ROUTES PREMIUM ET ADMIN (INCHANGÃ‰ES)
# =====================================

@router.post("/abonnement")
def abonnement(data: AbonnementRequest):
    try:
        resultat = creer_abonnement(data.model_dump())
        return {"message": "Abonnement enregistrÃ©", "abonnement": resultat}
    except Exception as erreur:
        raise HTTPException(status_code=500, detail=str(erreur))

@router.post("/activation")
def activation_premium(activation: ActivationRequest):
    abonnement = activer_abonnement(activation.telephone, activation.reference)
    if abonnement is None:
        raise HTTPException(status_code=404, detail="Aucun abonnement trouvÃ©")
    abonnement["date_fin"] = (datetime.now() + timedelta(days=int(abonnement.get("duree", 30)))).isoformat()
    return {"message": "Premium activÃ©", "statut": "ACTIF", "date_fin": abonnement["date_fin"]}

@router.get("/premium/{telephone}")
def premium(telephone: str):
    return verifier_premium(telephone)

@router.get("/admin/abonnements")
def admin_abonnements():
    return {"abonnements": lister_abonnements()}

@router.get("/admin/statistiques")
def admin_statistiques():
    return statistiques_abonnements()

@router.get("/journal")
def journal():
    try:
        resultat = recuperer_journal_lonab(datetime.now())
        if not resultat:
            raise HTTPException(status_code=503, detail="Journal hippique LONAB indisponible.")
        return resultat
    except Exception as erreur:
        raise HTTPException(status_code=500, detail=str(erreur))

@router.get("/debug-pmu")
def debug_pmu():
    from pmu_source import trouver_quinte_du_jour
    programme, reunion, course = trouver_quinte_du_jour(datetime.now().strftime("%d%m%Y"))
    return {"reunion": reunion, "programme_brut": programme, "course_brute": course}

@router.get("/debug-journal")
def debug_journal():
    return diagnostiquer_journal_lonab(datetime.now())
