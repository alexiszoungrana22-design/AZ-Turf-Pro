"""
Statistiques de performance Expert
Fichier : backend/modules/performance_expert.py

Corrigé : la version précédente cherchait une clé "nombre_trouves" que
learning.py n'a jamais écrite nulle part -> le résultat était toujours
0% quel que soit l'historique réel. Le calcul se fait maintenant à
partir des données réellement disponibles (arrivee/arrivee_officielle
+ selection_az), et seules les courses avec une arrivée connue sont
comptées.
"""


def _numero(valeur):
    if valeur is None:
        return None
    return str(valeur).strip() or None


def _liste_numeros(valeurs):
    out = []
    for item in valeurs or []:
        if isinstance(item, dict):
            n = _numero(item.get("numero"))
        else:
            n = _numero(item)
        if n:
            out.append(n)
    return out


def statistiques_expert(historique) -> dict:
    if not isinstance(historique, list) or not historique:
        return {"courses": 0, "indice_confiance": 0}

    total = 0
    trouves = 0

    for h in historique:
        if not isinstance(h, dict):
            continue

        arrivee = _liste_numeros(h.get("arrivee_officielle") or h.get("arrivee"))
        if not arrivee:
            continue

        total += 1
        selection = _liste_numeros(h.get("selection_az"))[:5]
        nombre_trouves = len(set(selection).intersection(set(arrivee[:5])))
        if nombre_trouves >= 3:
            trouves += 1

    if total == 0:
        return {"courses": 0, "indice_confiance": 0}

    return {
        "courses": total,
        "indice_confiance": round((trouves / total) * 100, 1)
    }
