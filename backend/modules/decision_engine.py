
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

    # CORRECTION : analyse_cheval_engine.analyser_cheval() renvoie la clé
    # "score" (pas "score_expert") — la lecture précédente valait donc
    # toujours 0, rendant le tri et le seuil des bases inopérants.
    tries = sorted(
        profils,
        key=lambda x: x.get("score", 0),
        reverse=True
    )

    # CORRECTION : engine_expert.analyser_course_expert() plafonne
    # score_expert à 55 (40 pts indice AZ + 15 pts cote), donc le seuil de
    # 80 n'était jamais atteignable — aucune base n'était jamais retenue.
    # 40 correspond au cas où au moins le critère "Indice AZ élevé" est
    # rempli, seuil choisi pour rester cohérent avec l'échelle réelle.
    bases = [
        c for c in tries
        if c.get("score", 0) >= 40
    ]

    # CORRECTION : analyse_cheval_engine.analyser_cheval() ne produit que les
    # profils "PREMIERE CHANCE", "CHANCE REGULIERE", "OUTSIDER" ou
    # "A SURVEILLER" — le libellé "OUTSIDER INTERESSANT" attendu ici n'existe
    # nulle part, la liste des outsiders était donc toujours vide.
    # OBSERVATION (test) : sur l'échelle réelle (0-55), un même cheval peut
    # être à la fois "base" (score >= 40) et profilé "OUTSIDER" (score < 50).
    # On exclut les bases de la liste des outsiders pour éviter qu'un même
    # cheval apparaisse dans les deux catégories du ticket.
    outsiders = [
        c for c in tries
        if c.get("profil") == "OUTSIDER" and c not in bases
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
