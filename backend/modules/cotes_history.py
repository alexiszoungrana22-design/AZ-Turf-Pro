"""Analyse robuste des mouvements de cotes disponibles."""
from __future__ import annotations


def _float(v, default=0.0):
    try:
        if isinstance(v, str): v=v.replace(',', '.')
        return float(v)
    except (TypeError, ValueError): return default


def analyser_tendances_cotes(data: dict) -> dict:
    if not isinstance(data, dict) or not isinstance(data.get("chevaux"), list):
        return {"status":"error","message":"Données de course manquantes ou invalides","resultats":[]}
    resultats=[]
    for cheval in data["chevaux"]:
        if not isinstance(cheval, dict) or cheval.get("numero") is None: continue
        matin=_float(cheval.get("cote_matin_brute", cheval.get("cote_matin", 0)))
        direct=_float(cheval.get("cote_brute", cheval.get("cote", 0)))
        variation=0.0; tendance="NON_DOCUMENTE"; signal="NON_DOCUMENTE"
        if matin>0 and direct>0:
            variation=round((direct-matin)/matin*100,2)
            if variation<=-20: tendance,signal="FORTE_BAISSE","SMART_MONEY"
            elif variation<=-5: tendance,signal="BAISSE","SOUTENU"
            elif variation>=20: tendance,signal="HAUSSE","DELAISSE"
            else: tendance,signal="STABLE","NEUTRE"
        resultats.append({"numero":cheval.get("numero"),"nom":cheval.get("nom","Inconnu"),"cote_matin":matin or None,"cote_direct":direct or None,"variation_pct":variation,"tendance":tendance,"signal":signal})
    return {"status":"success","total_analyses":len(resultats),"resultats":resultats}
