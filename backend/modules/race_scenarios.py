"""Scénarios déterministes à partir des données réellement disponibles."""
from __future__ import annotations
from .value_analysis import score_independant


def generer_scenarios(chevaux: list[dict], info_course: dict | None = None) -> list[dict]:
    chevaux = chevaux or []
    if not chevaux: return []
    ranked = sorted(chevaux, key=score_independant, reverse=True)
    bases = [str(c.get("numero")) for c in ranked[:3]]
    outsiders = [str(c.get("numero")) for c in sorted(chevaux, key=lambda c: float(c.get("cote") or 0), reverse=True)[:3]]
    return [
        {"nom":"Rythme régulier", "lecture":"Les profils les plus réguliers et bien notés gardent l'avantage.", "priorites":bases},
        {"nom":"Course rythmée", "lecture":"La fraîcheur, la régularité et la capacité à tenir l'effort deviennent prioritaires.", "priorites":bases[:2] + [x for x in outsiders if x not in bases][:1]},
        {"nom":"Course tactique", "lecture":"Les chevaux bien classés sur les critères bruts sont à privilégier ; les écarts faibles appellent une couverture.", "priorites":bases},
    ]


def resume_scenarios(chevaux: list[dict], info_course: dict | None = None) -> str:
    s = generer_scenarios(chevaux, info_course)
    if not s: return "Aucun scénario ne peut être calculé sans partants."
    return "\n".join(f"• **{x['nom']}** — {x['lecture']} Priorités : {', '.join(x['priorites'])}." for x in s)
