
"""Couche de raisonnement utilisant UNIQUEMENT les données déjà produites par le moteur du chatbot."""
from typing import Any

def _num(x):
    try: return int(x)
    except Exception: return None

def _score(c):
    """Score autonome basé sur les données brutes, sans indice AZ/Premium.

    Cette couche ne doit jamais reprendre un score déjà calculé par AZ Turf Pro.
    Elle construit donc son propre score à partir de forme, régularité, cote,
    tendance de cote et signaux jockey/driver lorsqu'ils sont disponibles.
    """
    def num(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    forme = num(c.get("forme"), 0.0)
    regularite = num(c.get("regularite"), 0.0)
    cote = num(c.get("cote"), 0.0)
    variation = num(c.get("variation_cote_pct"), 0.0)
    jockey = num(c.get("reussite_jockey"), 0.0)

    # Echelle 0-100. Les champs absents restent neutres.
    score = 0.0
    score += min(max(forme, 0), 10) * 4.0
    score += min(max(regularite, 0), 10) * 3.0
    score += min(max(jockey, 0), 100) * 0.10
    if cote > 0:
        # Bonus de valeur modéré : une cote intermédiaire est plus intéressante
        # qu'un très gros favori ou un très gros outsider, sans décider seule.
        if 3 <= cote <= 12:
            score += 8.0
        elif 12 < cote <= 25:
            score += 5.0
    if variation < 0:
        score += min(abs(variation), 20) * 0.20
    elif variation > 0:
        score -= min(variation, 20) * 0.10
    return round(max(0.0, min(score, 100.0)), 2)

def analyze_independently(contexte: dict, limit: int = 20) -> dict:
    moteur = (contexte or {}).get("moteur", {}) or {}
    classement = [c for c in (moteur.get("classement") or []) if isinstance(c, dict)]
    rows = []
    for c in classement[:limit]:
        rows.append({
            "numero": _num(c.get("numero")),
            "nom": c.get("nom"),
            "score": _score(c),
            "forme": c.get("forme"),
            "regularite": c.get("regularite"),
            "cote": c.get("cote"),
            "tendance_cote": c.get("tendance_cote") or c.get("tendance"),
            "driver": c.get("driver") or c.get("conducteur") or c.get("pilote") or c.get("jockey"),
            "entraineur": c.get("entraineur"),
            "corde": c.get("corde"),
            "ferrage": c.get("deferre"),
            "source": "moteur_propre_chatbot",
        })
    ranked = sorted(
        [r for r in rows if r["score"] is not None],
        key=lambda r: r["score"], reverse=True
    )
    return {"independent": True, "horses": ranked or rows, "tickets_existing": moteur.get("tickets", {})}

def make_tickets(result: dict) -> dict:
    horses = [h for h in result.get("horses", []) if h.get("numero") is not None]
    nums = [h["numero"] for h in horses]
    if not nums:
        return {}
    base = nums[:1]
    safe = nums[:4]
    balanced = nums[:5]
    speculative = nums[:7]
    return {
        "autonome_prudent": {"base": base, "selection": safe},
        "autonome_equilibre": {"base": base, "selection": balanced},
        "autonome_offensif": {"base": base, "selection": speculative},
    }

def compare_to_az(result: dict, contexte: dict) -> dict:
    az = (contexte or {}).get("moteur", {}).get("selection_az", []) or []
    own = [h["numero"] for h in result.get("horses", []) if h.get("numero") is not None][:7]
    return {
        "independent_selection": own,
        "az_selection": az[:7],
        "agreement": [n for n in own if n in az],
        "divergence": [n for n in own if n not in az],
    }
