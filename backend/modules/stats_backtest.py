"""
AZ TURF PRO - STATISTIQUES & BACKTESTING
Les anciennes entrées utilisant 'arrivee' sont compatibles avec le nouveau format.
"""


def _arrivee(course):
    return [str(num) for num in (
        course.get("arrivee_officielle")
        or course.get("arrivee")
        or []
    )]


def _selection(course):
    selection = course.get("selection_az")
    if not selection:
        selection = (course.get("tickets") or {}).get("gratuit", {}).get("quinte", [])
    result = []
    for item in selection:
        if isinstance(item, dict):
            result.append(str(item.get("numero")))
        else:
            result.append(str(item))
    return result


def calculer_stats_performance(historique_courses: list) -> dict:
    if not historique_courses:
        return {
            "status": "warning",
            "message": "Aucune course enregistrée dans l'historique.",
            "stats": {}
        }

    total_courses = len(historique_courses)
    courses_avec_resultat = 0
    quinte_trouve_az = 0
    tierce_trouve_az = 0
    favori_a_l_arrivee = 0

    for course in historique_courses:
        arrivee = _arrivee(course)
        if not arrivee:
            continue

        courses_avec_resultat += 1
        selection = _selection(course)
        favori_data = course.get("favori") or {}
        favori = str(favori_data.get("numero", "") if isinstance(favori_data, dict) else favori_data)

        if favori and favori in arrivee[:3]:
            favori_a_l_arrivee += 1

        if len(set(selection[:3]).intersection(arrivee[:3])) == 3:
            tierce_trouve_az += 1

        if len(set(selection[:5]).intersection(arrivee[:5])) >= 4:
            quinte_trouve_az += 1

    denom = courses_avec_resultat or 1
    return {
        "status": "success",
        "courses_analysees": total_courses,
        "courses_avec_resultat": courses_avec_resultat,
        "taux_reussite_favori": round(favori_a_l_arrivee / denom * 100, 1),
        "taux_tierce_az": round(tierce_trouve_az / denom * 100, 1),
        "taux_quinte_az": round(quinte_trouve_az / denom * 100, 1),
    }


def simuler_backtest_filtre(historique_courses: list, filtres: dict) -> dict:
    mise_de_base = float(filtres.get("mise_de_base", 10.0))
    cote_min = float(filtres.get("cote_min", 0.0))
    cote_max = float(filtres.get("cote_max", 999.0))

    paris_touches = 0
    gains_totaux = 0.0
    mises_totales = 0.0

    for course in historique_courses:
        arrivee = _arrivee(course)
        chevaux = course.get("chevaux") or course.get("classement") or []

        for cheval in chevaux:
            cote = float(cheval.get("cote", 0) or 0)
            if cote_min <= cote <= cote_max:
                mises_totales += mise_de_base
                if arrivee and str(cheval.get("numero")) == arrivee[0]:
                    paris_touches += 1
                    gains_totaux += mise_de_base * cote

    roi = ((gains_totaux - mises_totales) / mises_totales * 100) if mises_totales else 0.0
    nb_paris = mises_totales / mise_de_base if mise_de_base > 0 else 0

    return {
        "status": "success",
        "mises_totales": round(mises_totales, 2),
        "gains_totaux": round(gains_totaux, 2),
        "profit_net": round(gains_totaux - mises_totales, 2),
        "roi_pourcent": round(roi, 2),
        "taux_gagnant": round(paris_touches / nb_paris * 100, 1) if nb_paris else 0.0
    }
