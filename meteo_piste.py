def analyser_impact_terrain(data: dict) -> dict:
    info = (data or {}).get("info_course") or {}
    terrain = str(info.get("terrain") or info.get("etat_piste") or info.get("piste") or "").strip().lower()
    meteo = info.get("meteo") or {}
    pluie = meteo.get("pluie", meteo.get("precipitation", 0)) if isinstance(meteo, dict) else 0
    vent = meteo.get("vent", meteo.get("vent_kmh", 0)) if isinstance(meteo, dict) else 0

    try:
        pluie = float(pluie or 0)
    except (TypeError, ValueError):
        pluie = 0
    try:
        vent = float(vent or 0)
    except (TypeError, ValueError):
        vent = 0

    humide = any(k in terrain for k in ("souple", "lourd", "collant", "humide", "boue"))
    sec = any(k in terrain for k in ("bon", "sec", "ferme", "rapide"))

    if humide or pluie >= 5:
        impact = "FAVORABLE AUX PROFILS ADAPTES AU TERRAIN HUMIDE"
    elif vent >= 30:
        impact = "VENT FORT : IMPACT TACTIQUE POSSIBLE"
    elif sec:
        impact = "FAVORABLE AUX PROFILS ADAPTES AU TERRAIN SEC"
    elif terrain:
        impact = f"TERRAIN : {terrain.upper()}"
    else:
        impact = "NEUTRE"

    return {
        "status": "success",
        "impact": impact,
        "terrain": terrain or "non précisé",
        "pluie": pluie,
        "vent_kmh": vent,
    }
