"""Intégration réelle des modules complémentaires au moteur AZ Turf-Pro.

Ce module est volontairement ADDITIF : il ne modifie ni le scoring AZ, ni le
classement AZ, ni les routes API. Il reçoit le résultat du moteur principal,
exécute les briques complémentaires disponibles et restitue leurs résultats
ainsi que les signaux par cheval.
"""
from __future__ import annotations

from typing import Any

from modules.value_analysis import analyser_valeur
from modules.race_scenarios import generer_scenarios
from modules.arbitre_ia_az import comparer
from modules.cotes_history import analyser_tendances_cotes
from modules.meteo_piste import analyser_impact_terrain
from modules.pronos_presse import analyser_consensus_presse
from modules.performance_evaluator import evaluer


def _safe_call(fn, default, *args, **kwargs):
    try:
        result = fn(*args, **kwargs)
        return result if result is not None else default
    except Exception as exc:  # un module complémentaire ne doit jamais casser le moteur AZ
        return {"status": "error", "message": str(exc), **(default if isinstance(default, dict) else {})}


def _numero(v: Any) -> str:
    return "" if v is None else str(v).strip()


def construire_analyse_complementaire(
    classement_az: list[dict],
    info_course: dict | None = None,
    historique: list[dict] | None = None,
) -> dict:
    """Exécute les modules complémentaires sur les mêmes données que le moteur."""
    info_course = info_course if isinstance(info_course, dict) else {}
    classement_az = [c for c in (classement_az or []) if isinstance(c, dict) and not c.get("est_non_partant")]
    historique = historique if isinstance(historique, list) else []

    cotes = _safe_call(analyser_tendances_cotes, {"status": "error", "resultats": []}, {"chevaux": classement_az})
    presse = _safe_call(analyser_consensus_presse, {"status": "error", "consensus": []}, {"info_course": info_course, "chevaux": classement_az})
    meteo = _safe_call(analyser_impact_terrain, {"status": "error", "impact": "NON_DOCUMENTE"}, {"info_course": info_course, "chevaux": classement_az})
    valeur = _safe_call(analyser_valeur, [], classement_az)
    scenarios = _safe_call(generer_scenarios, [], classement_az, info_course)
    arbitre = _safe_call(comparer, {"az": [], "autonome": [], "communs": [], "divergences_autonome": []}, classement_az)
    performance = _safe_call(evaluer, {"courses_evaluees": 0}, historique)

    # Index des signaux par numéro pour enrichir les chevaux sans toucher aux scores AZ.
    valeur_map = {_numero(x.get("numero")): x for x in valeur if isinstance(x, dict)}
    cotes_map = {_numero(x.get("numero")): x for x in (cotes.get("resultats", []) if isinstance(cotes, dict) else []) if isinstance(x, dict)}

    chevaux = []
    for cheval in classement_az:
        numero = _numero(cheval.get("numero"))
        enrichi = {
            "numero": cheval.get("numero"),
            "nom": cheval.get("nom"),
            "valeur": valeur_map.get(numero, {}),
            "cotes": cotes_map.get(numero, {}),
        }
        chevaux.append(enrichi)

    return {
        "modules_executes": [
            "valeur", "scenarios", "cotes", "presse", "meteo_piste", "performance", "arbitre_ia_az"
        ],
        "moteur_az_conserve": True,
        "valeur": valeur,
        "scenarios": scenarios,
        "tendances_cotes": cotes.get("resultats", []) if isinstance(cotes, dict) else [],
        "presse": presse,
        "meteo_piste": meteo,
        "performance": performance,
        "arbitre": arbitre,
        "chevaux": chevaux,
    }
