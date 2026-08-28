"""Consensus presse : utilise uniquement les pronostics explicitement fournis."""
from __future__ import annotations


def analyser_consensus_presse(data: dict) -> dict:
    data = data if isinstance(data, dict) else {}
    course = data.get("info_course") if isinstance(data.get("info_course"), dict) else {}
    raw = data.get("presse") or data.get("pronostics_presse") or data.get("consensus_presse")
    if raw is None:
        raw = course.get("presse") or course.get("pronostics_presse") or course.get("consensus_presse")
    if raw is None:
        return {"status":"no_data", "consensus":[], "source":"aucune donnée presse fournie"}
    if isinstance(raw, dict):
        consensus = raw.get("consensus") or raw.get("selection") or raw.get("pronostics") or []
    elif isinstance(raw, list):
        consensus = raw
    else:
        consensus = [raw]
    return {"status":"success", "consensus":consensus, "source":"données presse fournies"}
