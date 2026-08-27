"""
AZ TURF PRO - MODULE STATISTIQUES & BACKTESTING
Fichier : backend/modules/stats_backtest.py

Corrigé : accepte le format réel produit par learning.py (clé "arrivee",
sélections stockées comme simples numéros et non comme objets), et ne
compte dans les statistiques que les courses dont l'arrivée officielle
est réellement connue (sinon "0%" serait affiché à tort comme un vrai
taux d'échec).
"""


def _numero(valeur):
    if valeur is None:
        return None
    return str(valeur).strip() or None


def _liste_numeros(valeurs):
    """Normalise une liste de sélection qui peut contenir soit des
    numéros bruts (str/int), soit des dicts {"numero": ...}."""
    out = []
    for item in valeurs or []:
        if isinstance(item, dict):
            n = _numero(item.get("numero"))
        else:
            n = _numero(item)
        if n:
            out.append(n)
    return out


def calculer_stats_performance(historique_courses: list) -> dict:
    """
    Analyse l'historique réel des courses enregistrées (backend/data/historique_az.json,
    lu via learning.lire_historique) pour calculer le taux de réussite des
    sélections AZ. Seules les courses dont l'arrivée officielle a été
    renseignée (via /learning ou mettre_a_jour_arrivee) sont comptées.
    """
    if not isinstance(historique_courses, list) or not historique_courses:
        return {
            "status": "warning",
            "message": "Aucune course enregistrée dans l'historique.",
            "stats": {}
        }

    total_avec_arrivee = 0
    quinte_trouve_az = 0
    tierce_trouve_premium = 0
    favori_a_l_arrivee = 0

    for course in historique_courses:
        if not isinstance(course, dict):
            continue

        arrivee_officielle = _liste_numeros(
            course.get("arrivee_officielle") or course.get("arrivee")
        )
        if not arrivee_officielle:
            # Course pas encore courue, ou arrivée pas encore saisie :
            # on ne fabrique pas de statistique dessus.
            continue

        total_avec_arrivee += 1

        selection_az = _liste_numeros(course.get("selection_az"))[:5]

        favori = course.get("favori") or {}
        favori_num = _numero(favori.get("numero")) if isinstance(favori, dict) else _numero(favori)

        if favori_num and favori_num in arrivee_officielle[:3]:
            favori_a_l_arrivee += 1

        bonnes_tetes = set(selection_az[:3]).intersection(set(arrivee_officielle[:3]))
        if len(bonnes_tetes) == 3:
            tierce_trouve_premium += 1

        bonnes_places = set(selection_az[:5]).intersection(set(arrivee_officielle[:5]))
        if len(bonnes_places) >= 4:
            quinte_trouve_az += 1

    if total_avec_arrivee == 0:
        return {
            "status": "warning",
            "message": "Aucune course avec arrivée officielle connue pour le moment : "
                       "impossible de calculer un vrai taux de réussite.",
            "stats": {}
        }

    return {
        "status": "success",
        "courses_analysées": total_avec_arrivee,
        "taux_reussite_favori": round((favori_a_l_arrivee / total_avec_arrivee) * 100, 1),
        "taux_tierce_premium": round((tierce_trouve_premium / total_avec_arrivee) * 100, 1),
        "taux_quinte_az": round((quinte_trouve_az / total_avec_arrivee) * 100, 1),
    }


def simuler_backtest_filtre(historique_courses: list, filtres: dict) -> dict:
    """
    Simule la rentabilité théorique d'une stratégie sur l'historique réel.
    Exemple filtres: {"cote_min": 5.0, "cote_max": 15.0}
    Ne compte que les courses avec une arrivée officielle connue.
    """
    filtres = filtres or {}
    mise_de_base = float(filtres.get("mise_de_base", 10.0))
    cote_min = float(filtres.get("cote_min", 0.0))
    cote_max = float(filtres.get("cote_max", 999.0))

    paris_touches = 0
    gains_totaux = 0.0
    mises_totales = 0.0

    for course in historique_courses or []:
        if not isinstance(course, dict):
            continue

        arrivee = _liste_numeros(course.get("arrivee_officielle") or course.get("arrivee"))
        if not arrivee:
            continue

        chevaux = course.get("chevaux") or course.get("classement") or []

        for cheval in chevaux:
            if not isinstance(cheval, dict):
                continue
            num = _numero(cheval.get("numero"))
            cote = float(cheval.get("cote", 0) or 0)

            if num and cote_min <= cote <= cote_max:
                mises_totales += mise_de_base
                if num == arrivee[0]:
                    paris_touches += 1
                    gains_totaux += (mise_de_base * cote)

    roi = round(((gains_totaux - mises_totales) / mises_totales) * 100, 2) if mises_totales > 0 else 0.0

    return {
        "mises_totales": mises_totales,
        "gains_totaux": round(gains_totaux, 2),
        "profit_net": round(gains_totaux - mises_totales, 2),
        "roi_pourcent": roi,
        "taux_gagnant": round((paris_touches / (mises_totales / mise_de_base)) * 100, 1) if mises_totales > 0 else 0.0
    }
