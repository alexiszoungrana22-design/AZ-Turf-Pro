"""Validation chronologique hors-échantillon des facteurs AZ et Premium.

Lecture seule : aucune écriture PostgreSQL et aucune activation directe.
Les facteurs sont appris séparément par spécialité et évalués uniquement
sur les courses postérieures à la période d'apprentissage.
"""
from __future__ import annotations
from typing import Any


def _num(value: Any) -> str | None:
    if isinstance(value, dict):
        value = value.get("numero", value.get("numPmu", value.get("number")))
    return None if value is None else str(value)


def _discipline(course: dict) -> str:
    try:
        from scoring import classifier_discipline
    except ImportError:
        from .scoring import classifier_discipline
    return classifier_discipline(
        (course or {}).get("specialite") or (course or {}).get("discipline")
        or (course or {}).get("type_course") or ""
    )


def _score_az(cheval: dict, discipline: str, facteurs: dict) -> float:
    try:
        from scoring import calculer_score_az
    except ImportError:
        from .scoring import calculer_score_az
    return float(calculer_score_az(cheval, discipline, calibration=facteurs))


def _score_premium(cheval: dict, course: dict, discipline: str, facteurs: dict, score_az: float) -> float:
    try:
        from engine import calculer_indice_premium
    except ImportError:
        from .engine import calculer_indice_premium
    copie = dict(cheval)
    copie["indice_az"] = score_az
    return float(calculer_indice_premium(copie, info_course=course, discipline=discipline, calibration=facteurs))


def _mesures(acc, total):
    if not total:
        return {"taux_gagnant_dans_selection": 0.0, "couverture_arrivee_top5": 0.0, "taux_top5_complet": 0.0}
    return {
        "taux_gagnant_dans_selection": round(100 * acc["gagnant"] / total, 2),
        "couverture_arrivee_top5": round(100 * acc["couverture"] / total, 2),
        "taux_top5_complet": round(100 * acc["complet"] / total, 2),
    }


def evaluer_calibration_hors_echantillon(lignes: list[dict], part_apprentissage: float = 0.70,
                                         seuil_courses_apprentissage: int = 30) -> dict:
    if not 0.5 <= float(part_apprentissage) <= 0.85:
        raise ValueError("part_apprentissage doit être comprise entre 0.50 et 0.85")

    valides = []
    for row in lignes or []:
        if isinstance(row.get("chevaux_json"), list) and row["chevaux_json"] and isinstance(row.get("arrivee_json"), list) and row["arrivee_json"]:
            valides.append(row)
    # Le lecteur PostgreSQL renvoie déjà l'ordre chronologique. On ne réordonne
    # pas ici pour préserver les tests et les appels qui fournissent cet ordre.
    split = int(len(valides) * float(part_apprentissage))
    apprentissage, test = valides[:split], valides[split:]
    if len(apprentissage) < seuil_courses_apprentissage or not test:
        return {"status": "donnees_insuffisantes", "courses_valides": len(valides),
                "courses_apprentissage": len(apprentissage), "courses_test": len(test),
                "seuil_apprentissage": seuil_courses_apprentissage,
                "message": "Échantillon insuffisant : aucun facteur candidat ne doit être activé."}

    try:
        from modules.learning_turf import calculer_calibrations_par_discipline
    except ImportError:
        from .modules.learning_turf import calculer_calibrations_par_discipline
    apprentissage_calibre = calculer_calibrations_par_discipline(apprentissage, seuil_min=seuil_courses_apprentissage)
    facteurs = {"facteurs_par_discipline": apprentissage_calibre.get("facteurs_par_discipline", {})}
    if not factores_valide(facteurs):
        return {"status": "calibration_indisponible", "courses_valides": len(valides),
                "courses_apprentissage": len(apprentissage), "courses_test": len(test),
                "details": apprentissage_calibre, "message": "Les facteurs actuels restent inchangés."}

    accum = {
        "az_reference": {"gagnant": 0, "couverture": 0.0, "complet": 0},
        "az_candidate": {"gagnant": 0, "couverture": 0.0, "complet": 0},
        "premium_reference": {"gagnant": 0, "couverture": 0.0, "complet": 0},
        "premium_candidate": {"gagnant": 0, "couverture": 0.0, "complet": 0},
    }
    evalues = 0
    for row in test:
        chevaux = [h for h in row["chevaux_json"] if isinstance(h, dict) and h.get("numero") is not None]
        arrivee = [_num(n) for n in row["arrivee_json"][:5] if _num(n) is not None]
        if not chevaux or not arrivee:
            continue
        course = row.get("course_json") or {}
        discipline = _discipline(course)
        actual = set(arrivee)
        az_ref = sorted(chevaux, key=lambda h: float(h.get("indice_az", h.get("score_az", _score_az(h, discipline, {}))) or 0), reverse=True)[:5]
        az_cand_scores = {id(h): _score_az(h, discipline, facteurs) for h in chevaux}
        az_cand = sorted(chevaux, key=lambda h: az_cand_scores[id(h)], reverse=True)[:5]
        premium_ref = sorted(chevaux, key=lambda h: float(h.get("indice_premium", h.get("indice_az", 0)) or 0), reverse=True)[:6]
        premium_cand = sorted(chevaux, key=lambda h: _score_premium(h, course, discipline, facteurs, az_cand_scores[id(h)]), reverse=True)[:6]

        for key, selection in (("az_reference", az_ref), ("az_candidate", az_cand),
                               ("premium_reference", premium_ref), ("premium_candidate", premium_cand)):
            nums = {_num(h) for h in selection}
            nums.discard(None)
            accum[key]["gagnant"] += int(arrivee[0] in nums)
            hits = len(nums.intersection(actual))
            accum[key]["couverture"] += hits / len(actual)
            accum[key]["complet"] += int(actual.issubset(nums))
        evalues += 1

    if not evalues:
        return {"status": "aucune_course_testable", "courses_apprentissage": len(apprentissage), "courses_test": len(test)}

    mesures = {key: _mesures(value, evalues) for key, value in accum.items()}
    ecarts = {"az": {k: round(mesures["az_candidate"][k] - mesures["az_reference"][k], 2) for k in mesures["az_reference"]},
              "premium": {k: round(mesures["premium_candidate"][k] - mesures["premium_reference"][k], 2) for k in mesures["premium_reference"]}}
    # Alias historiques conservés pour les outils et tests qui lisaient
    # l'ancien résultat centré uniquement sur l'Indice AZ.
    ref_az = dict(mesures["az_reference"])
    cand_az = dict(mesures["az_candidate"])
    ref_az.update({"taux_gagnant_dans_top5": ref_az["taux_gagnant_dans_selection"],
                   "couverture_moyenne_top5": ref_az["couverture_arrivee_top5"]})
    cand_az.update({"taux_gagnant_dans_top5": cand_az["taux_gagnant_dans_selection"],
                    "couverture_moyenne_top5": cand_az["couverture_arrivee_top5"]})
    return {"status": "success", "mode": "shadow_read_only", "courses_apprentissage": len(apprentissage),
            "courses_test_evaluees": evalues, "facteurs_candidats": facteurs,
            "details_calibration": apprentissage_calibre.get("details_par_discipline", {}),
            "reference": ref_az, "candidate": cand_az,
            "reference_detail": {"az": mesures["az_reference"], "premium": mesures["premium_reference"]},
            "candidate_detail": {"az": mesures["az_candidate"], "premium": mesures["premium_candidate"]},
            "ecart_points": ecarts, "activation_automatique": False,
            "message": "Résultat de test uniquement. Les facteurs candidats ne sont pas enregistrés ni appliqués."}


def factores_valide(facteurs):
    return any(bool(v) for v in (facteurs.get("facteurs_par_discipline") or {}).values())
