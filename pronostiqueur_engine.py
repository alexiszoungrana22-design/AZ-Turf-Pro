
"""
AZ TURF PRO - Pronostiqueur Engine V3
Couche de synthèse expert indépendante.
"""

def analyser_profils_chevaux(chevaux):
    resultats = []

    for c in chevaux:
        score = float(c.get("score_expert", 0) or 0)
        cote = float(c.get("cote", 0) or 0)

        profil = "NEUTRE"
        risques = []
        arguments = []

        if score >= 80:
            profil = "BASE FIABLE"
            arguments.append("Score expert élevé")

        elif score >= 60:
            profil = "CHANCE REGULIERE"
            arguments.append("Profil équilibré")

        elif cote >= 10:
            profil = "OUTSIDER INTERESSANT"
            arguments.append("Rapport potentiel intéressant")

        if cote > 20:
            risques.append("Cote élevée")

        resultats.append({
            "numero": c.get("numero"),
            "nom": c.get("nom"),
            "profil": profil,
            "arguments": arguments,
            "risques": risques
        })

    return resultats


def comparer_az_expert(cheval):
    return {
        "numero": cheval.get("numero"),
        "indice_az": cheval.get("indice_az", 0),
        "score_expert": cheval.get("score_expert", 0),
        "analyse": "Comparaison complémentaire AZ / Expert"
    }


def generer_synthese(profils):
    bases = []
    outsiders = []

    for p in profils:
        if p["profil"] == "BASE FIABLE":
            bases.append(p["numero"])
        elif p["profil"] == "OUTSIDER INTERESSANT":
            outsiders.append(p["numero"])

    return {
        "bases": bases,
        "outsiders": outsiders,
        "message": "Analyse expert générée"
    }
