# =====================================
# AZ TURF PRO - CALCULATEUR VIP (bets.py)
# =====================================

def generer_champ_reduit(bases, associes, type_pari="QUINTO"):
    """
    Génère les combinaisons en champ réduit basées sur les numéros favoris et associés.
    """
    import itertools
    
    # Nombre de chevaux requis par type de jeu
    tailles = {"TIERCE": 3, "QUARTE": 4, "QUINTE": 5}
    taille_cible = tailles.get(type_pari.upper(), 5)
    
    places_restantes = taille_cible - len(bases)
    if places_restantes <= 0:
        return [bases[:taille_cible]]

    combinaisons = []
    for combo in itertools.combinations(associes, places_restantes):
        combinaisons.append(bases + list(combo))

    cost_base = 2.0  # Prix de base unitaire en Euro / FCFA
    return {
        "type_pari": type_pari,
        "bases": bases,
        "associes": associes,
        "nombre_tickets": len(combinaisons),
        "cout_total": len(combinaisons) * cost_base,
        "combinaisons": combinaisons
    }
