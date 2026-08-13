"""
AZ TURF PRO - SCORING AVANCÉ (Optimisé 85%)
Fichier complet à remplacer : scoring.py
"""

def calculer_score_az(cheval, discipline="TROT"):
    """
    Calcule l'indice AZ avec pondération dynamique selon la discipline.
    """
    score = 0
    disc = str(discipline).upper()

    # --- 1. PONDÉRATION PAR DISCIPLINE ---
    if "TROT" in disc:
        coef_forme = 4.5
        coef_regularite = 4.0
        coef_jockey = 3.5  # Driver
        coef_cote = 2.5
        coef_experience = 2.0
    elif "PLAT" in disc:
        coef_forme = 5.5
        coef_regularite = 3.0
        coef_jockey = 4.0  # Jockey & Corde
        coef_cote = 3.0
        coef_experience = 1.5
    else:  # OBSTACLE / HAIES / STEEPLE
        coef_forme = 4.0
        coef_regularite = 5.0
        coef_jockey = 3.0
        coef_cote = 2.0
        coef_experience = 4.0

    # --- 2. CALCUL DE BASE ---
    score += cheval.get("forme", 0) * coef_forme
    score += cheval.get("regularite", 0) * coef_regularite
    score += cheval.get("gains", 0) * 2.5
    score += cheval.get("jockey_score", 0) * coef_jockey
    score += cheval.get("cote", 0) * coef_cote
    score += cheval.get("distance", 0) * 2.5
    score += cheval.get("terrain", 0) * 2.0
    score += cheval.get("experience", 0) * coef_experience

    # --- 3. CRITÈRE OR AU TROT : DÉFERRAGE (D4, DP, DA) ---
    if "TROT" in disc:
        deferrage = str(cheval.get("deferre", "")).upper()
        if deferrage in ["D4", "DÉFERRÉ 4 PIEDS", "D4_4"]:
            score += 18.0  # Gros bonus pour déferré des 4
        elif deferrage in ["DP", "DA", "DÉFERRÉ ANTÉRIEURS", "DÉFERRÉ POSTÉRIEURS"]:
            score += 9.0   # Bonus modéré pour déferré 2 pieds

    # --- 4. CORDE / STALLE (PLAT) ---
    if "PLAT" in disc:
        num_corde = cheval.get("corde", 99)
        if isinstance(num_corde, (int, float)) and num_corde <= 4:
            score += 12.0  # Corde favorable (1 à 4)

    # --- 5. BONUS PERFORMANCES RÉCENTES (TOP 3) ---
    performances = cheval.get("performances", [])
    if performances:
        bonnes_places = 0
        for place in performances:
            if isinstance(place, (int, float)) and place <= 3:
                bonnes_places += 1
        score += bonnes_places * 6.0

    return round(score, 2)
