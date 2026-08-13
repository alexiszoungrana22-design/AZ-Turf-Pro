from scoring import calculer_score_az
from ranking import classer_chevaux
from quinte import generer_tickets_az
from learning import enregistrer_course


def calculer_indice_premium(cheval):
    """Indice Premium indépendant du simple classement AZ.

    Il conserve l'indice AZ comme socle mais réévalue légèrement
    forme, régularité, cote marché, expérience et performances afin
    que l'offre Premium apporte une lecture supplémentaire.
    """
    indice_az = float(cheval.get("indice_az", 0) or 0)
    forme = float(cheval.get("forme", 5) or 5)
    regularite = float(cheval.get("regularite", 5) or 5)
    cote = float(cheval.get("cote", 5) or 5)
    experience = float(cheval.get("experience", 5) or 5)
    bonnes_places = sum(1 for p in (cheval.get("performances") or []) if isinstance(p, (int, float)) and p <= 3)

    # Le Premium reste cohérent avec AZ, mais donne une pondération
    # supplémentaire aux signaux qui peuvent faire bouger une sélection.
    return round(
        indice_az
        + forme * 1.25
        + regularite * 1.10
        + cote * 1.35
        + experience * 0.75
        + bonnes_places * 1.50,
        4,
    )


def lancer_analyse(chevaux, info_course=None):
    if not chevaux:
        return {
            "message": "Aucun cheval",
            "chevaux": [],
            "classement": [],
            "tickets": {},
        }

    chevaux_scores = []

    for cheval in chevaux:
        score = calculer_score_az(cheval)
        entree = dict(cheval)
        entree["numero"] = cheval.get("numero")
        entree["nom"] = cheval.get("nom", "")
        entree["indice_az"] = score
        entree["indice_premium"] = calculer_indice_premium(entree)
        chevaux_scores.append(entree)

    classement = classer_chevaux(chevaux_scores)
    tickets = generer_tickets_az(classement)

    try:
        enregistrer_course({
            "chevaux": chevaux,
            "classement": classement,
            "tickets": tickets,
            "course": info_course or {},
        })
    except Exception:
        pass

    return {
        "message": "Analyse AZ Turf terminée",
        "chevaux": classement,
        "classement": classement,
        "favori": classement[0] if classement else {},
        "tickets": tickets,
    }
    
