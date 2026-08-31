
"""
AZ TURF PRO EXPERT V9
Analyse cheval par cheval.
Couche indépendante.
"""

def analyser_cheval(cheval):
    points_forts = []
    points_faibles = []

    if cheval.get("forme"):
        points_forts.append("Forme récente analysée")

    if cheval.get("distance"):
        points_forts.append("Aptitude distance disponible")

    if cheval.get("terrain"):
        points_forts.append("Aptitude terrain disponible")

    if cheval.get("risque"):
        points_faibles.append(cheval.get("risque"))

    score = cheval.get("score_expert", 0)

    profil = "A SURVEILLER"

    if score >= 85:
        profil = "PREMIERE CHANCE"
    elif score >= 70:
        profil = "CHANCE REGULIERE"
    elif score < 50:
        profil = "OUTSIDER"

    return {
        "numero": cheval.get("numero"),
        "nom": cheval.get("nom"),
        "profil": profil,
        "score": score,
        "points_forts": points_forts,
        "points_faibles": points_faibles
    }


def comparer_chevaux(chevaux):
    analyses = [
        analyser_cheval(c)
        for c in chevaux
    ]

    return sorted(
        analyses,
        key=lambda x: x["score"],
        reverse=True
    )


def justification_selection(cheval):
    return {
        "cheval": cheval.get("nom"),
        "raison": "Sélection basée sur le profil Expert."
    }
