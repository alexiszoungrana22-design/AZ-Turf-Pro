
"""
AZ TURF PRO EXPERT V13
Moteur de simulation avancée.
Couche complémentaire indépendante.
"""

def simuler_scenario(favori, outsiders=None, rythme="normal"):
    outsiders = outsiders or []

    scenarios = []

    scenarios.append({
        "nom": "Favori confirme",
        "impact": f"Le favori {favori} conserve son avantage.",
        "risque": "faible"
    })

    scenarios.append({
        "nom": "Favori battu",
        "impact": "Les outsiders peuvent prendre une place importante.",
        "risque": "moyen"
    })

    if outsiders:
        scenarios.append({
            "nom": "Outsider gagnant",
            "impact": f"Attention aux outsiders {outsiders}.",
            "risque": "élevé"
        })

    return {
        "rythme": rythme,
        "scenarios": scenarios
    }


def evaluer_robustesse_ticket(ticket, scenarios):
    score = 0

    for scenario in scenarios:
        if scenario.get("risque") == "faible":
            score += 30
        elif scenario.get("risque") == "moyen":
            score += 25
        else:
            score += 20

    return {
        "ticket": ticket,
        "robustesse": min(score, 100)
    }


def classer_combinaisons(combinaisons):
    resultats = []

    for c in combinaisons:
        resultats.append({
            "ticket": c,
            "indice_robustesse": len(c) * 10
        })

    return sorted(
        resultats,
        key=lambda x: x["indice_robustesse"],
        reverse=True
    )
