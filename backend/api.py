"""
AZ TURF PRO - API Backend Server
Fichier complet à remplacer : api.py
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from main import obtenir_donnees_courses_pmu
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
        courses = obtenir_donnees_courses_pmu()
        
        for course in courses:
            partants = course.get("partants", [])
            if partants:
                # Exécution du moteur d'analyse complet
                analyse = lancer_analyse(partants, info_course=course)
                
                # Injection des résultats et des tickets calculés
                course["partants"] = analyse.get("classement", partants)
                course["tickets"] = analyse.get("tickets", {})

        return {
            "success": True,
            "total": len(courses),
            "courses": courses
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
