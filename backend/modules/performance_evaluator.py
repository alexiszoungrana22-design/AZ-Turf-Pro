"""Mesure simple des sélections historiques lorsque l'arrivée est disponible."""
from __future__ import annotations


def evaluer(entrees: list[dict]) -> dict:
    total = 0; top5 = 0; gagnant = 0
    for e in entrees or []:
        arr = [str(x) for x in (e.get("arrivee") or [])]
        sel = [str(x) for x in (e.get("selection_az") or [])]
        if not arr or not sel: continue
        total += 1
        if arr[0] in sel: gagnant += 1
        if any(x in sel for x in arr[:5]): top5 += 1
    return {"courses_evaluees": total, "favori_dans_selection": gagnant, "selection_touche_top5": top5,
            "taux_favori_pct": round(gagnant/total*100,1) if total else None,
            "taux_top5_pct": round(top5/total*100,1) if total else None}
