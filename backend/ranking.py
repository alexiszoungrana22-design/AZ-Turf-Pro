"""
AZ TURF PRO - RANKING (Version Sécurisée)
Fichier complet à remplacer : ranking.py
"""

def ajouter_raison_az(cheval, position):
    """Attribue un commentaire d'analyse selon la position et le score."""
    try:
        indice = float(cheval.get("indice_az", 0) or 0)
    except (ValueError, TypeError):
        indice = 0.0

    if position == 1:
        return "⭐ Favori AZ : meilleur indice et profil prioritaire"
    if position <= 3:
        return "🔥 Base solide : régularité et forte chance de podium"
    if position <= 5:
        return "🎯 Chance AZ : potentiel pour intégrer l'arrivée"
    if indice >= 180.0:
        return "💎 Outsider intéressant : peut surprendre"
        
    return "⚠️ Coup spéculatif"


def classer_chevaux(chevaux):
    """
    Trie les chevaux par indice AZ décroissant, attribue les rangs,
    les explications et calcule l'indice de confiance en %.
    """
    if not chevaux or not isinstance(chevaux, list):
        return []

    # 1. Tri sécurisé par indice_az (conversion en float pour éviter les erreurs de type)
    def obtenir_score(c):
        try:
            return float(c.get("indice_az", 0) or 0)
        except (ValueError, TypeError):
            return 0.0

    classement = sorted(chevaux, key=obtenir_score, reverse=True)

    # 2. Récupération du meilleur indice
    meilleur_indice = obtenir_score(classement[0]) if classement else 0.0

    # 3. Traitement de chaque cheval
    for index, cheval in enumerate(classement, start=1):
        cheval["rang"] = index
        cheval["raison"] = ajouter_raison_az(cheval, index)

        score_courant = obtenir_score(cheval)

        # Calcul sécurisé de la confiance (évite la division par zéro)
        if meilleur_indice > 0:
            confiance = round((score_courant / meilleur_indice) * 100)
        else:
            confiance = 0

        # Plafonne la confiance (1er = 100%, suivants = max 99%)
        cheval["confiance"] = max(0, min(confiance, 99 if index > 1 else 100))

    return classement
