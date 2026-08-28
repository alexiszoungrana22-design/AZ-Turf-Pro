"""Analyse météo/piste à partir des données réellement fournies au moteur.
Aucune donnée externe n'est inventée : absence de source => NON_DOCUMENTE."""
from __future__ import annotations


def _pick(d, keys):
    if not isinstance(d, dict):
        return None
    for k in keys:
        v=d.get(k)
        if v not in (None, "", []):
            return v
    return None


def analyser_impact_terrain(data: dict) -> dict:
    data = data if isinstance(data, dict) else {}
    course = data.get("info_course") if isinstance(data.get("info_course"), dict) else data
    meteo = _pick(course, ("meteo", "weather", "conditions_meteo"))
    terrain = _pick(course, ("terrain", "etat_piste", "etat_piste", "piste", "going"))
    temperature = _pick(course, ("temperature", "température"))
    vent = _pick(course, ("vent", "wind"))
    pluie = _pick(course, ("pluie", "rain"))

    details=[]
    if terrain is not None: details.append(f"piste: {terrain}")
    if meteo is not None: details.append(f"météo: {meteo}")
    if temperature is not None: details.append(f"température: {temperature}")
    if vent is not None: details.append(f"vent: {vent}")
    if pluie is not None: details.append(f"pluie: {pluie}")

    if not details:
        return {"status":"no_data", "impact":"NON_DOCUMENTE", "source":"aucune donnée météo/piste fournie", "details":[]}

    texte=" ".join(str(x).lower() for x in (terrain, meteo, pluie) if x is not None)
    impact="NEUTRE"
    if any(k in texte for k in ("lourd", "souple", "boue", "pluie", "heavy")):
        impact="POTENTIELLEMENT_PERTURBANT"
    elif any(k in texte for k in ("bon", "sec", "rapide", "firme", "standard")):
        impact="PLUTOT_FAVORABLE"

    return {"status":"success", "impact":impact, "source":"données de course", "details":details}
