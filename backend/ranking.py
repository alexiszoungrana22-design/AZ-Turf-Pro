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
        cheval["confiance_type"] = "proximite_indice_au_leader"
        cheval["confiance_interpretation"] = (
            "Proximité de l'indice AZ du leader, pas une probabilité de victoire."
        )

        # CORRECTION (cahier des charges, section 6) : "confiance" est
        # conservée telle quelle (le frontend en dépend dans accueil.js,
        # analyse.js, live-premium.js et ticket-premium.js) mais elle ne
        # mesure qu'une proximité de score. Les concepts sont désormais
        # exposés séparément, sous leur vrai nom, en plus :
        #  - proximite_au_leader : la même valeur, honnêtement nommée.
        #  - confiance_donnees : % de critères reposant sur une vraie
        #    donnée plutôt qu'une valeur neutre par défaut (calculé dans
        #    pmu_source.py ; absent pour des chevaux saisis à la main).
        #  - score_robustesse : combine proximité au leader et fiabilité
        #    des données — un cheval proche du leader MAIS basé sur peu de
        #    vraies données est moins robuste qu'un cheval proche du leader
        #    ET bien documenté.
        # Aucune "probabilité de victoire" n'est exposée : aucune
        # calibration statistique réelle n'en existe à ce jour.
        cheval["proximite_au_leader"] = cheval["confiance"]
        confiance_donnees = cheval.get("confiance_donnees")
        if confiance_donnees is not None:
            cheval["score_robustesse"] = round(
                (cheval["proximite_au_leader"] + confiance_donnees) / 2
            )

    return classement
