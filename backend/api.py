"""
AZ TURF PRO - API Router
Fichier complet à remplacer : api.py
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from engine import lancer_analyse

# On définit un routeur au lieu d'une application FastAPI globale
router = APIRouter()


@router.get("/live-courses")
def get_live-courses() -> Dict[str, Any]:
    try:
        # Import local pour éviter l'import circulaire avec main.py
        from main import obtenir_donnees_courses_pmu
        
        courses = obtenir_donnees_courses_pmu()
        
        for course in courses:
            partants = course.get("partants", [])
            if partants:
                analyse = lancer_analyse(partants, info_course=course)
                course["partants"] = analyse.get("classement", partants)
                course["tickets"] = analyse.get("tickets", {})

        return {
            "success": True,
            "total": len(courses),
            "courses": courses
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
