"""Validation hors-échantillon des coefficients AZ.

Ce module est volontairement en mode lecture seule : il ne modifie jamais
PostgreSQL et n'active jamais les facteurs candidats. Les lignes doivent être
fournies dans l'ordre chronologique (ancien -> récent), avec chevaux_json,
arrivee_json et, facultativement, course_json.
"""
from __future__ import annotations

from typing import Any


def _num(value: Any) -> str | None:
    return None if value is None else str(value)


def _score(cheval: dict, discipline: str, facteurs: dict) -> float:
    # Import local pour permettre l'exécution depuis le package backend.
    try:
        from scoring import calculer_score_az
    except ImportError:
        from ..scoring import calculer_score_az
    return float(calculer_score_az(cheval, discipline, calibration=facteurs))


def evaluer_calibration_hors_echantillon(
    lignes: list[dict],
    part_apprentissage: float = 0.70,
    seuil_courses_apprentissage: int = 30,
) -> dict:
    """Compare les facteurs candidats à la référence neutre sur des courses futures.

    `lignes` doit être trié de la plus ancienne à la plus récente. La première
    partie sert uniquement à calculer les facteurs ; la dernière partie sert
    uniquement à mesurer les résultats. Les courses incomplètes sont ignorées.
    """
    if not 0.5 <= float(part_apprentissage) <= 0.85:
        raise ValueError("part_apprentissage doit être comprise entre 0.50 et 0.85")

    valides = []
    for row in lignes or []:
        chevaux = row.get("chevaux_json")
        arrivee = row.get("arrivee_json")
        if isinstance(chevaux, list) and chevaux and isinstance(arrivee, list) and arrivee:
            valides.append(row)

    split = int(len(valides) * float(part_apprentissage))
    apprentissage, test = valides[:split], valides[split:]
    if len(apprentissage) < seuil_courses_apprentissage or not test:
        return {
            "status": "donnees_insuffisantes",
            "courses_valides": len(valides),
            "courses_apprentissage": len(apprentissage),
            "courses_test": len(test),
            "seuil_apprentissage": seuil_courses_apprentissage,
            "message": "Échantillon insuffisant : aucun facteur candidat ne doit être activé.",
        }

    try:
        from modules.learning_turf import calculer_calibration
    except ImportError:
        from .learning_turf import calculer_calibration
    calibration = calculer_calibration(apprentissage, seuil_min=seuil_courses_apprentissage)
    if calibration.get("status") != "success":
        return {
            "status": "calibration_indisponible",
            "courses_valides": len(valides),
            "courses_apprentissage": len(apprentissage),
            "courses_test": len(test),
            "calibration": calibration,
            "message": "Les facteurs actuels restent inchangés.",
        }

    factors = calibration.get("facteurs") or {}
    totals = {
        "reference": {"gagnant": 0, "couverture_top5": 0.0, "top5_complet": 0},
        "candidate": {"gagnant": 0, "couverture_top5": 0.0, "top5_complet": 0},
    }
    evaluated = 0
    for row in test:
        horses = [h for h in row["chevaux_json"] if isinstance(h, dict) and h.get("numero") is not None]
        arrival = [_num(n) for n in row["arrivee_json"][:5] if _num(n) is not None]
        if not horses or not arrival:
            continue
        course = row.get("course_json") or {}
        discipline = str(course.get("specialite") or course.get("discipline") or course.get("type_course") or "TROT")
        actual = set(arrival)
        rankings = {}
        for key, coeffs in (("reference", {}), ("candidate", factors)):
            ranked = sorted(horses, key=lambda h: _score(h, discipline, coeffs), reverse=True)
            selected = {_num(h.get("numero")) for h in ranked[:5]}
            selected.discard(None)
            winners = _num(row["arrivee_json"][0])
            totals[key]["gagnant"] += int(winners in selected)
            hits = len(selected.intersection(actual))
            totals[key]["couverture_top5"] += hits / max(1, len(actual))
            totals[key]["top5_complet"] += int(actual.issubset(selected))
        evaluated += 1

    if not evaluated:
        return {"status": "aucune_course_testable", "courses_apprentissage": len(apprentissage), "courses_test": len(test)}

    def metrics(item):
        return {
            "taux_gagnant_dans_top5": round(100 * item["gagnant"] / evaluated, 2),
            "couverture_moyenne_top5": round(100 * item["couverture_top5"] / evaluated, 2),
            "taux_top5_complet": round(100 * item["top5_complet"] / evaluated, 2),
        }

    base = metrics(totals["reference"])
    candidate = metrics(totals["candidate"])
    return {
        "status": "success",
        "mode": "shadow_read_only",
        "courses_apprentissage": len(apprentissage),
        "courses_test_evaluees": evaluated,
        "facteurs_candidats": factors,
        "reference": base,
        "candidate": candidate,
        "ecart_points": {k: round(candidate[k] - base[k], 2) for k in base},
        "activation_automatique": False,
        "message": "Résultat de test uniquement. Les facteurs candidats ne sont pas enregistrés ni appliqués.",
    }
