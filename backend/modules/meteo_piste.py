"""Analyse piste/terrain à partir des données réellement disponibles."""
def analyser_impact_terrain(data: dict) -> dict:
    data = data or {}
    terrain = data.get("terrain") or data.get("meteo")
    if isinstance(terrain, dict):
        texte = terrain.get("etat") or terrain.get("condition") or terrain.get("libelle") or terrain.get("description")
    else:
        texte = terrain
    if not texte:
        return {"status":"warning", "impact":"INCONNU", "source":"aucune_donnee_terrain"}
    t=str(texte).lower()
    if any(x in t for x in ("lourd","très souple","tres souple","détrempé","detrempe")):
        impact="FAVORABLE_AUX_CHEVAUX_A_LAISE_SUR_TERRAIN_LENT"
    elif any(x in t for x in ("souple","bon souple")):
        impact="FAVORABLE_AUX_CHEVAUX_CONFIRMES_SUR_SOUPLE"
    elif any(x in t for x in ("sec","bon","rapide")):
        impact="FAVORABLE_AUX_CHEVAUX_A_LAISE_SUR_TERRAIN_RAPIDE"
    else:
        impact="NEUTRE"
    return {"status":"success", "impact":impact, "etat":str(texte), "source":"donnees_course"}
