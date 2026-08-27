
"""Couche de raisonnement utilisant UNIQUEMENT les données déjà produites par le moteur du chatbot."""
from typing import Any

def _num(x):
    try: return int(x)
    except Exception: return None

def _score(c):
    for key in ("confiance", "score_ia", "score", "indice_ia", "indice_premium", "indice_az"):
        v = c.get(key)
        try:
            return float(v)
        except Exception:
            pass
    return None

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
