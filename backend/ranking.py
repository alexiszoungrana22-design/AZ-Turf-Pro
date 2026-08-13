"""
AZ TURF PRO - RANKING
Fichier complet à remplacer : ranking.py
"""

def ajouter_raison_az(cheval, position):
    """Attribue un commentaire d'analyse selon la position et le score."""
    indice = cheval.get("indice_az", 0)[cite: 4]

    if position == 1:[cite: 4]
        return "⭐ Favori AZ : meilleur indice et profil prioritaire"[cite: 4]
    if position <= 3:[cite: 4]
        return "🔥 Base solide : régularité et forte chance de podium"[cite: 4]
    if position <= 5:[cite: 4]
        return "🎯 Chance AZ : potentiel pour intégrer l'arrivée"[cite: 4]
    if indice >= 180:[cite: 4]
        return "💎 Outsider intéressant : peut surprendre"[cite: 4]
        
    return "⚠️ Coup spéculatif"[cite: 4]


def classer_chevaux(chevaux):
    """Trie les chevaux et calcule leur indice de confiance."""
    classement = sorted(
        chevaux,
        key=lambda x: x.get("indice_az", 0),
        reverse=True
    )[cite: 4]

    meilleur_indice = classement[0].get("indice_az", 0) if classement else 0[cite: 4]

    for index, cheval in enumerate(classement, start=1):[cite: 4]
        cheval["rang"] = index[cite: 4]
        cheval["raison"] = ajouter_raison_az(cheval, index)[cite: 4]

        # Indice de confiance : pourcentage par rapport au meilleur de la course
        if meilleur_indice > 0:[cite: 4]
            confiance = round((cheval.get("indice_az", 0) / meilleur_indice) * 100)[cite: 4]
        else:[cite: 4]
            confiance = 0[cite: 4]

        # Plafonne la confiance (le 1er peut avoir 100%, les autres max 99%)
        cheval["confiance"] = max(0, min(confiance, 99 if index > 1 else 100))[cite: 4]

    return classement[cite: 4]
