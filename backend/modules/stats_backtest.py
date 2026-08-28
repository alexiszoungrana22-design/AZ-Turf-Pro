"""
AZ TURF PRO - MODULE STATISTIQUES & BACKTESTING
Fichier : backend/modules/stats_backtest.py
"""

def calculer_stats_performance(historique_courses: list) -> dict:
    """
    Analyse l'historique des courses enregistrées pour calculer
    le taux de réussite des algorithmes AZ et Premium.
    """
    if not historique_courses:
        return {
            "status": "warning",
            "message": "Aucune course enregistrée dans l'historique.",
            "stats": {}
        }

    total_courses = len(historique_courses)
    quinte_trouve_az = 0
    tierce_trouve_premium = 0
    favori_a_l_arrivee = 0

    for course in historique_courses:
        arrivee_officielle = [str(num) for num in course.get("arrivee_officielle", [])]
        selection_az = [str(c.get("numero")) for c in course.get("selection_az", [])[:5]]
        favori = str(course.get("favori", {}).get("numero", ""))

        if arrivee_officielle:
            # Vérification Favori dans le Top 3
            if favori in arrivee_officielle[:3]:
                favori_a_l_arrivee += 1

            # Vérification Tiercé Premium (3 premiers de la sélection dans le Top 3)
            bonnes_tetes = set(selection_az[:3]).intersection(set(arrivee_officielle[:3]))
            if len(bonnes_tetes) == 3:
                tierce_trouve_premium += 1

            # Vérification Quinté
            bonnes_places = set(selection_az[:5]).intersection(set(arrivee_officielle[:5]))
            if len(bonnes_places) >= 4:  # Bonus / Désordre
                quinte_trouve_az += 1

    return {
        "status": "success",
        "courses_analysées": total_courses,
        "taux_reussite_favori": round((favori_a_l_arrivee / total_courses) * 100, 1),
        "taux_tierce_premium": round((tierce_trouve_premium / total_courses) * 100, 1),
        "taux_quinte_az": round((quinte_trouve_az / total_courses) * 100, 1),
    }


def simuler_backtest_filtre(historique_courses: list, filtres: dict) -> dict:
    """
    Simule la rentabilité théorique d'une stratégie sur l'historique.
    Exemple filtres: {"cote_min": 5.0, "cote_max": 15.0, "deferre_seulement": True}
    """
    mise_de_base = float(filtres.get("mise_de_base", 10.0))
    cote_min = float(filtres.get("cote_min", 0.0))
    cote_max = float(filtres.get("cote_max", 999.0))

    paris_touches = 0
    gains_totaux = 0.0
    mises_totales = 0.0

    for course in historique_courses:
        arrivee = [str(num) for num in course.get("arrivee_officielle", [])]
        chevaux = course.get("chevaux", [])

        for cheval in chevaux:
            num = str(cheval.get("numero"))
            try:
                cote = float(cheval.get("cote", cheval.get("cote_brute", 0)) or 0)
            except (TypeError, ValueError):
                cote = 0.0
            
            if cote_min <= cote <= cote_max:
                mises_totales += mise_de_base
                if arrivee and num == arrivee[0]:  # Gagnant
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
