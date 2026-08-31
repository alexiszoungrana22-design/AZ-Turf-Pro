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
        }

    favori_gagnant = 0
    selection_gagnant = 0
    selection_touchee = 0

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
        if selection and any(numero in arrivee for numero in selection):
            selection_touchee += 1

    pct = lambda n: round((n / total) * 100, 2)
    return {
        "status": "success",
        "courses_terminees": total,
        "courses_analysees": total,
        "favori_gagnant": favori_gagnant,
        "favori_taux": pct(favori_gagnant),
        "selection_contient_gagnant": selection_gagnant,
        "selection_taux_gagnant": pct(selection_gagnant),
        "selection_touchee": selection_touchee,
        "selection_taux_touchee": pct(selection_touchee),
    }
