"""Calcul des performances des pronostics à partir de l'archive PostgreSQL.

Module additif : ne modifie aucune route existante. Les calculs sont faits
uniquement sur les courses dont une arrivée officielle est présente.
"""
from __future__ import annotations


def _nums(values):
    out = []
    if not isinstance(values, list):
        return out
    for value in values:
        if isinstance(value, dict):
            value = value.get("numero")
        if value is None:
            continue
        text = str(value).strip()
        if text:
            out.append(text)
    return out


def calculer_performance(courses: list[dict]) -> dict:
    """Retourne des indicateurs simples et traçables sur les courses terminées."""
    terminees = [c for c in courses if _nums(c.get("arrivee_json"))]
    total = len(terminees)
    if total == 0:
        return {
            "status": "success",
            "courses_terminees": 0,
            "courses_analysees": 0,
            "favori_gagnant": 0,
            "favori_taux": 0.0,
            "selection_contient_gagnant": 0,
            "selection_taux_gagnant": 0.0,
            "selection_touchee": 0,
            "selection_taux_touchee": 0.0,
            "taux_couverture_moyenne_top5": 0.0,
            "taux_top5_complet": 0.0,
        }

    favori_gagnant = 0
    selection_gagnant = 0
    somme_couverture_top5 = 0.0
    top5_complet = 0

    for course in terminees:
        arrivee = _nums(course.get("arrivee_json"))
        gagnant = arrivee[0] if arrivee else None

        favori = course.get("favori_json") or {}
        if isinstance(favori, dict):
            numero_favori = favori.get("numero")
        else:
            numero_favori = None
        if gagnant is not None and str(numero_favori) == gagnant:
            favori_gagnant += 1

        selection = _nums(course.get("selection_az_json"))
        if gagnant is not None and gagnant in selection:
            selection_gagnant += 1
        top5 = arrivee[:5]
        if selection and top5:
            couverts = sum(1 for numero in top5 if numero in selection)
            somme_couverture_top5 += couverts / len(top5) * 100
            if all(numero in selection for numero in top5):
                top5_complet += 1

    pct = lambda n: round((n / total) * 100, 2)
    return {
        "status": "success",
        "courses_terminees": total,
        "courses_analysees": total,
        "favori_gagnant": favori_gagnant,
        "favori_taux": pct(favori_gagnant),
        "selection_contient_gagnant": selection_gagnant,
        "selection_taux_gagnant": pct(selection_gagnant),
        "selection_touchee": round(somme_couverture_top5 / 100 * total),
        "selection_taux_touchee": round(somme_couverture_top5 / total, 2),
        "taux_couverture_moyenne_top5": round(somme_couverture_top5 / total, 2),
        "taux_top5_complet": pct(top5_complet),
    }
