
"""
AZ TURF PRO EXPERT V8
Moteur de décision final du pronostiqueur.
Couche supplémentaire, sans remplacement du moteur AZ.
"""

def analyser_chevaux(profils):
    if not profils:
        return {
            "message": "Aucune donnée cheval disponible.",
            "confiance": 0
        }

    tries = sorted(
        profils,
        key=lambda x: x.get("score_expert", 0),
        reverse=True
    )

    bases = [
        c for c in tries
        if c.get("score_expert", 0) >= 80
    ]

    outsiders = [
        c for c in tries
        if c.get("profil") == "OUTSIDER INTERESSANT"
    ]

    confiance = min(95, 50 + len(bases) * 10)

    return {
        "classement": tries,
        "bases": bases,
        "outsiders": outsiders,
        "confiance": confiance
    }


def generer_ticket(decision, type_ticket="quinte"):
    bases = [
        c.get("numero")
        for c in decision.get("bases", [])
    ]

    outsiders = [
        c.get("numero")
        for c in decision.get("outsiders", [])
    ]

    return {
        "type": type_ticket,
        "bases": bases,
        "outsiders": outsiders,
        "niveau_confiance": decision.get("confiance", 0)
    }


def synthese_pronostiqueur(decision):
    return {
        "avis": "Analyse Expert AZ Turf Pro générée.",
        "points_forts": len(decision.get("bases", [])),
        "confiance": decision.get("confiance", 0)
    }
