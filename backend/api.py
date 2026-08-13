"""
AZ TURF PRO - API Backend Server (Corrigé sans import circulaire)
Fichier complet à remplacer : api.py
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from engine import lancer_analyse

app = FastAPI(title="AZ Turf Pro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/live-courses")
def get_live_courses() -> Dict[str, Any]:
    try:
        # IMPORT LOCAL : Évite l'import circulaire au démarrage de l'application
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
