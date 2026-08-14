# =====================================
# AZ TURF PRO - API OFFICIELLE
# =====================================

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta
import json
import os

from engine import lancer_analyse
from database import (
    creer_abonnement,
    activer_abonnement,
    verifier_premium,
    lister_abonnements,
    statistiques_abonnements
)
from models import AbonnementRequest, ActivationRequest
from pmu_source import charger_course_pmu
from lonab_source import recuperer_journal_lonab, diagnostiquer_journal_lonab
from learning import lire_historique, mettre_a_jour_arrivee, mettre_a_jour_publications

router = APIRouter(
    prefix="/api",
    tags=["AZ Turf"]
)

def charger_course_locale():
    chemin = os.path.join(os.path.dirname(__file__), "data", "courses.json")
    with open(chemin, "r", encoding="utf-8") as fichier:
        return json.load(fichier)

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

@router.get("/analyse")
def analyse():
    try:
        course, source = charger_course()
        if not course:
            raise HTTPException(status_code=503, detail="Aucune donnée de course disponible actuellement.")
            
        chevaux = course.get("chevaux", [])
        if not chevaux:
            raise HTTPException(status_code=503, detail="Aucun cheval trouvé dans la course.")
            
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

        classement = resultat.get("chevaux", [])
        aujourd_hui = datetime.now()
        est_demo = (source == "demo")
        
        return {
            "message": "Analyse AZ Turf terminée",
            "source": source,
            "donnees_demo": est_demo,
            "course": course.get("course", "Course"),
            "date": course.get("date") or aujourd_hui.strftime("%Y-%m-%d"),
            "reunion": course.get("reunion") or "R1",
            "course_numero": course.get("course_numero") or "C1",
            "heure_depart": course.get("heure_depart", ""),
            "horaires": course.get("horaires", {}),
            "hippodrome": course.get("hippodrome", ""),
            "discipline": course.get("discipline", ""),
            "distance": course.get("distance_course", ""),
            "allocation": course.get("allocation", ""),
            "non_partants": resultat.get("non_partants", course.get("non_partants", [])),
            "chevaux": classement,
            "classement": classement,
            "favori": classement[0] if classement else {},
            "tickets": resultat.get("tickets", {})
        }
    except HTTPException:
        raise
    except Exception as erreur:
        raise HTTPException(status_code=500, detail=f"Erreur AZ : {str(erreur)}")

@router.post("/abonnement")
def abonnement(data: AbonnementRequest):
    return {"message": "Abonnement enregistré", "abonnement": creer_abonnement(data.model_dump())}

@router.post("/activation")
def activation_premium(activation: ActivationRequest):
    abonnement = activer_abonnement(activation.telephone, activation.reference)
    if abonnement is None:
        raise HTTPException(status_code=404, detail="Aucun abonnement trouvé")
    abonnement["date_fin"] = (datetime.now() + timedelta(days=int(abonnement.get("duree", 30)))).isoformat()
    return {"message": "Premium activé", "statut": "ACTIF", "date_fin": abonnement["date_fin"]}

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
        aujourd_hui = datetime.now()
        resultat = recuperer_journal_lonab(aujourd_hui)
        if not resultat:
            raise HTTPException(status_code=503, detail="Journal hippique LONAB indisponible.")
        return resultat
    except Exception as erreur:
        raise HTTPException(status_code=500, detail=f"Erreur journal : {str(erreur)}")

@router.get("/historique")
def historique():
    try:
        entrees = lire_historique()
        return {"historique": entrees}
    except Exception as erreur:
        raise HTTPException(status_code=500, detail=f"Erreur historique : {erreur}")

# =====================================
# SOURCES OFFICIELLES & BRUITS D'ÉCURIE
# =====================================

@router.get("/pdf/journal/aujourdhui")
async def get_pdf_journal_aujourdhui():
    # Redirection directe vers la source officielle LONAB configurée
    return RedirectResponse(url="https://www.lonab.bf/programme-pmub")

@router.get("/pdf/arrivees/dernieres")
async def get_pdf_arrivees():
    # Redirection directe vers la source officielle des résultats LONAB
    return RedirectResponse(url="https://www.lonab.bf/resultats-gains-pmub")

@router.get("/bruits-ecurie")
async def get_bruits_ecurie():
    # Source réelle connectée au fichier local JSON modifiable
    chemin = os.path.join(os.path.dirname(__file__), "data", "bruits.json")
    try:
        if os.path.exists(chemin):
            with open(chemin, "r", encoding="utf-8") as f:
                return JSONResponse(content=json.load(f))
    except Exception:
        pass
    
    # Valeur de secours si le fichier n'est pas encore créé
    return JSONResponse(content={
        "tuyau": "Information en cours d'actualisation.",
        "avis_pros": "En attente des déclarations des professionnels."
    })
