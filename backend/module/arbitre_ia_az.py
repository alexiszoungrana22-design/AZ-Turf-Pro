"""Arbitre entre classement AZ existant et classement autonome."""
from __future__ import annotations
from .value_analysis import score_independant


def comparer(classement_az: list[dict]) -> dict:
    az = [c for c in classement_az or []]
    autonome = sorted([dict(c) for c in az], key=score_independant, reverse=True)
    az_nums = [str(c.get("numero")) for c in az[:7]]
    ia_nums = [str(c.get("numero")) for c in autonome[:7]]
    communs = [n for n in ia_nums if n in az_nums]
    divergences = [n for n in ia_nums if n not in az_nums]
    return {"az": az_nums, "autonome": ia_nums, "communs": communs, "divergences_autonome": divergences}


def resume(classement_az: list[dict]) -> str:
    r = comparer(classement_az)
    return (f"🤖 IA autonome : {' - '.join(r['autonome']) or 'indisponible'}\n"
            f"🏆 AZ Turf-Pro : {' - '.join(r['az']) or 'indisponible'}\n"
            f"🤝 Convergences : {', '.join(r['communs']) or 'aucune'}\n"
            f"🔎 Différences IA : {', '.join(r['divergences_autonome']) or 'aucune' }.")
