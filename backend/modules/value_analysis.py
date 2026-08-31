"""Analyse locale de valeur : estimation indépendante vs cote disponible."""
from __future__ import annotations
import math


def _num(v, default=0.0):
    try: return float(v)
    except (TypeError, ValueError): return default


def score_independant(cheval: dict) -> float:
    # Ne lit jamais indice_az / indice_premium.
    vals = [
        (_num(cheval.get("forme"), 5), 0.25),
        (_num(cheval.get("regularite"), 5), 0.20),
        (_num(cheval.get("distance"), 5), 0.12),
        (_num(cheval.get("terrain"), 5), 0.10),
        (_num(cheval.get("jockey_score"), 5), 0.10),
        (_num(cheval.get("experience"), 5), 0.08),
        (_num(cheval.get("gains"), 5), 0.05),
    ]
    return round(sum(v*w for v,w in vals), 3)


def analyser_valeur(chevaux: list[dict]) -> list[dict]:
    # Probabilité indicative relative au peloton : elle n'est jamais présentée
    # comme une probabilité garantie. Cela évite de transformer arbitrairement
    # un score brut 0-10 en probabilité absolue.
    items = []
    for c in chevaux or []:
        items.append((c, score_independant(c)))
    if not items:
        return []
    # Softmax stable pour comparer les profils entre eux.
    mx = max(score for _, score in items)
    weights = [(c, score, math.exp((score-mx)/1.35)) for c, score in items]
    total = sum(w for _,_,w in weights) or 1.0
    result = []
    for c, score, w in weights:
        proba = w / total
        cote = _num(c.get("cote"), 0)
        cote_fair = round(1/proba, 2) if proba > 0 else None
        edge = round((cote/cote_fair - 1)*100, 1) if cote > 0 and cote_fair else None
        result.append({"numero": c.get("numero"), "nom": c.get("nom"), "score_independant": round(score,3),
                       "probabilite_indicative": round(proba*100,1), "cote": cote or None,
                       "cote_fair_indicative": cote_fair, "ecart_marche_pct": edge})
    return sorted(result, key=lambda x: (x["ecart_marche_pct"] if x["ecart_marche_pct"] is not None else -999), reverse=True)


def resume_valeur(chevaux: list[dict], limite=5) -> str:
    rows = analyser_valeur(chevaux)[:limite]
    if not rows: return "Aucune donnée de valeur disponible."
    lines = []
    for r in rows:
        edge = r["ecart_marche_pct"]
        signal = "valeur potentielle" if edge is not None and edge >= 10 else "neutre"
        lines.append(f"N°{r['numero']} {r['nom']} — cote {r['cote'] or '-'}, estimation {r['probabilite_indicative']}%, cote théorique {r['cote_fair_indicative']} → {signal}.")
    return "\n".join(lines)
