"""
Analyse prudente de l'impact piste/terrain à partir des informations réellement
présentes dans info_course. Aucune météo n'est inventée lorsqu'elle n'est pas fournie.
"""


def analyser_impact_terrain(data: dict) -> dict:
    info = (data or {}).get("info_course") or {}
    terrain = str(info.get("terrain") or info.get("etat_piste") or "").strip().lower()
    meteo = str(info.get("meteo") or info.get("conditions_meteo") or "").strip().lower()

    if not terrain and not meteo:
        return {
            "status": "success",
            "impact": "INCONNU",
            "niveau": "NEUTRE",
            "source": "donnees_course",
            "message": "Aucune information météo ou état de piste fournie."
        }

    mots_favorables = ("bon", "sec", "rapide", "souple")
    mots_defavorables = ("lourd", "collant", "détrempé", "detrempe", "boueux")

    score = 0
    if any(m in terrain for m in mots_favorables):
        score += 1
    if any(m in terrain for m in mots_defavorables):
        score -= 1

    if score > 0:
        impact = "FAVORABLE"
    elif score < 0:
        impact = "DEFAVORABLE"
    else:
        impact = "NEUTRE"

    return {
        "status": "success",
        "impact": impact,
        "niveau": impact,
        "terrain": terrain or "Non renseigné",
        "meteo": meteo or "Non renseignée",
        "source": "donnees_course",
        "message": "Impact déduit uniquement des informations disponibles."
    }
