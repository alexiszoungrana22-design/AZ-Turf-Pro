
"""
AZ TURF PRO EXPERT V10
Moteur tactique de course.
Couche complémentaire indépendante.
"""

def analyser_rythme_course(chevaux):
    """
    Analyse simple du rythme probable.
    Les données détaillées peuvent être ajoutées plus tard.
    """
    animateurs = []
    attentistes = []

    for c in chevaux:
        style = str(c.get("style", "")).lower()

        if "leader" in style or "allant" in style:
            animateurs.append(c.get("numero"))

        if "attente" in style or "finisseur" in style:
            attentistes.append(c.get("numero"))

    return {
        "animateurs_probables": animateurs,
        "finisseurs_probables": attentistes
    }


def analyser_scenario_course(chevaux):
    rythme = analyser_rythme_course(chevaux)

    if len(rythme["animateurs_probables"]) > 2:
        scenario = "Rythme soutenu possible, avantage aux chevaux capables de finir."
    else:
        scenario = "Rythme modéré possible, les chevaux bien placés peuvent profiter."

    return {
        "rythme": rythme,
        "scenario": scenario
    }


def construire_strategie_quinte(selection):
    return {
        "base": selection[:2],
        "complement": selection[2:4],
        "coup_de_poker": selection[-1:] if selection else []
    }
