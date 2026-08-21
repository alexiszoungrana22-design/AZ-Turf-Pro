"""
AZ TURF PRO - MODULE TENDANCES DE COTES
Fichier : backend/modules/cotes_history.py
"""

def analyser_tendances_cotes(data: dict) -> dict:
    """
    Analyse la variation entre la cote matinale et la cote en direct
    pour identifier les chevaux joués (Smart Money) et les délaissés.
    """
    if not data or "chevaux" not in data:
        return {
            "status": "error",
            "message": "Données de course manquantes ou invalides",
            "resultats": []
        }

    chevaux = data.get("chevaux", [])
    resultats = []

    for cheval in chevaux:
        nom = cheval.get("nom", "Inconnu")
        numero = cheval.get("numero", "?")
        cote_matin = float(cheval.get("cote_matin_brute", 0) or 0)
        cote_direct = float(cheval.get("cote_brute", 0) or 0)

        variation = 0.0
        tendance = "STABLE"
        signal = "NEUTRE"

        if cote_matin > 0 and cote_direct > 0:
            # Calcul de la baisse/hausse en pourcentage
            variation = round(((cote_direct - cote_matin) / cote_matin) * 100, 2)

            if variation <= -20.0:
                tendance = "FORTE_BAISSE"
                signal = "SMART_MONEY 🔥"  # Gros volume d'argent sur ce cheval
            elif variation <= -5.0:
                tendance = "BAISSE"
                signal = "SOUTENU 📈"
            elif variation >= 20.0:
                tendance = "HAUSSE"
                signal = "DELAISSE 📉"

        resultats.append({
            "numero": numero,
            "nom": nom,
            "cote_matin": cote_matin,
            "cote_direct": cote_direct,
            "variation_pct": variation,
            "tendance": tendance,
            "signal": signal
        })

    return {
        "status": "success",
        "total_analyses": len(resultats),
        "resultats": resultats
    }
