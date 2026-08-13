"""
AZ TURF PRO - MOTEUR D'INTELLIGENCE (Avec filtrage automatique des non-partants)
Fichier complet à remplacer : engine.py
"""

from scoring import calculer_score_az
from ranking import classer_chevaux
from quinte import generer_tickets_az
from learning import enregistrer_course


def calculer_indice_premium(cheval, discipline="TROT"):
    """
    Indice Premium : combine l'Indice AZ avec une analyse croisée de valeur.
    """
    indice_az = float(cheval.get("indice_az", 0) or 0)
    forme = float(cheval.get("forme", 5) or 5)
    regularite = float(cheval.get("regularite", 5) or 5)
    cote = float(cheval.get("cote", 5) or 5)
    experience = float(cheval.get("experience", 5) or 5)
    
    bonnes_places = sum(
        1 for p in (cheval.get("performances") or []) 
        if isinstance(p, (int, float)) and p <= 3
    )

    bonus_outsider_chaud = 0.0
    if cote >= 10.0 and (forme >= 7.0 or regularite >= 7.0):
        bonus_outsider_chaud = 15.0

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
    Orchestre l'analyse complète d'une course en filtrant automatiquement les non-partants.
    """
    if not chevaux:
        return {
            "message": "Aucun cheval analysé",
            "chevaux": [],
            "classement": [],
            "tickets": {},
        }

    # =========================================================
    # 1. EXTRACTION ET FILTRAGE AUTOMATIQUE DES NON-PARTANTS
    # =========================================================
    non_partants = []
    if info_course and isinstance(info_course, dict):
        non_partants = info_course.get("non_partants", [])

    np_nums = set()
    for np in non_partants:
        if isinstance(np, dict):
            num = np.get("numero")
            if num is not None:
                np_nums.add(str(num))
        elif np is not None:
            np_nums.add(str(np))

    # Exclusion stricte des non-partants de la liste des chevaux à analyser
    chevaux_valides = []
    for cheval in chevaux:
        num = cheval.get("numero")
        if num is not None and str(num) in np_nums:
            continue  # Ignore le cheval s'il est non-partant
        chevaux_valides.append(cheval)

    discipline = "TROT"
    if info_course and isinstance(info_course, dict):
        discipline = info_course.get("discipline", "TROT")

    chevaux_scores = []

    for cheval in chevaux_valides:
        score_base = calculer_score_az(cheval, discipline=discipline)
        
        entree = dict(cheval)
        entree["numero"] = cheval.get("numero")
        entree["nom"] = cheval.get("nom", "")
        entree["indice_az"] = score_base
        entree["indice_premium"] = calculer_indice_premium(entree, discipline=discipline)
        chevaux_scores.append(entree)

    # 2. Classement des chevaux valides uniquement
    classement = classer_chevaux(chevaux_scores)
    
    # 3. Génération des tickets sans les non-partants
    tickets = generer_tickets_az(classement)

    # 4. Sauvegarde dans le module d'apprentissage
    try:
        enregistrer_course({
            "chevaux": chevaux_valides,
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
