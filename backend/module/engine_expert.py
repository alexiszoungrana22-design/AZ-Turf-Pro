
"""
AZ TURF PRO - Moteur Expert Hippique V2
Surcouche indépendante du moteur AZ existant.
"""

def analyser_course_expert(data: dict) -> dict:
    chevaux = data.get("chevaux", [])

    analyses = []

    for c in chevaux:
        score = 0
        raisons = []

        indice = float(c.get("indice_az", 0) or 0)

        if indice >= 80:
            score += 40
            raisons.append("Indice AZ élevé")

        cote = float(c.get("cote", 0) or 0)

        if 3 <= cote <= 15:
            score += 15
            raisons.append("Cote offrant une valeur possible")

        analyses.append({
            "numero": c.get("numero"),
            "nom": c.get("nom"),
            "score_expert": score,
            "raisons": raisons
        })

    analyses.sort(
        key=lambda x: x["score_expert"],
        reverse=True
    )

    return {
        "status": "success",
        "classement_expert": analyses
    }


def generer_avis_expert(cheval: dict) -> str:
    return (
        f"🎯 N°{cheval.get('numero')} : "
        f"score expert {cheval.get('score_expert')}. "
        + ", ".join(cheval.get("raisons", []))
    )
