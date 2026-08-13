"""
AZ TURF PRO - MOTEUR D'INTELLIGENCE
Fichier complet à remplacer : engine.py
"""

from scoring import calculer_score_az
from ranking import classer_chevaux
from quinte import generer_tickets_az
from learning import enregistrer_course


def calculer_indice_premium(cheval, discipline="TROT"):
    """
    Indice Premium : combine l'Indice AZ avec une analyse croisée de valeur.
    Détecte les chevaux spéculatifs à fort potentiel de rapport.
    """
    indice_az = float(cheval.get("indice_az", 0) or 0)
    forme = float(cheval.get("forme", 5) or 5)
    regularite = float(cheval.get("regularite", 5) or 5)
    cote = float(cheval.get("cote", 5) or 5)
    experience = float(cheval.get("experience", 5) or 5)
    
    # Calcul des podiums
    bonnes_places = sum(
        1 for p in (cheval.get("performances") or []) 
        if isinstance(p, (int, float)) and p <= 3
    )

    # DÉTECTION OUTSIDER SOLIDE : Cote élevée (> 10) mais forme/régularité au Top
    bonus_outsider_chaud = 0.0
    if cote >= 10.0 and (forme >= 7.0 or regularite >= 7.0):
        bonus_outsider_chaud = 15.0  # Surpondération spéculative

    return round(
        indice_az
        + (forme * 1.35)
        + (regularite * 1.20)
        + (cote * 1.10)
        + (experience * 0.80)
        + (bonnes_places * 2.0)
        + bonus_outsider_chaud,
        2
    )


def lancer_analyse(chevaux, info_course=None):
    """
    Orchestre l'analyse complète d'une course.
    """
    if not chevaux:
        return {
            "message": "Aucun cheval analysé",
            "chevaux": [],
            "classement": [],
            "tickets": {},
        }

    discipline = "TROT"
    if info_course and isinstance(info_course, dict):
        discipline = info_course.get("discipline", "TROT")

    chevaux_scores = []

    for cheval in chevaux:
        # 1. Calcul du score AZ dynamique par discipline
        score_base = calculer_score_az(cheval, discipline=discipline)
        
        entree = dict(cheval)
        entree["numero"] = cheval.get("numero")
        entree["nom"] = cheval.get("nom", "")
        entree["indice_az"] = score_base
        
        # 2. Calcul du score Premium indépendant
        entree["indice_premium"] = calculer_indice_premium(entree, discipline=discipline)
        chevaux_scores.append(entree)

    # 3. Classement des chevaux
    classement = classer_chevaux(chevaux_scores)
    
    # 4. Génération des tickets
    tickets = generer_tickets_az(classement)

    # 5. Sauvegarde automatique dans le module d'apprentissage
    try:
        enregistrer_course({
            "chevaux": chevaux,
            "classement": classement,
            "tickets": tickets,
            "course": info_course or {},
        })
    except Exception:
        pass

    return {
        "message": "Analyse AZ Turf Pro (Mode Avancé) terminée",
        "chevaux": classement,
        "classement": classement,
        "favori": classement[0] if classement else {},
        "tickets": tickets,
    }
