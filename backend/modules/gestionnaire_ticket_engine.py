
"""
AZ TURF PRO EXPERT V12
Gestionnaire de tickets et simulation.
Couche complémentaire indépendante.
"""

def calculer_cout_ticket(combinaison, prix_unitaire=1):
    return len(combinaison) * prix_unitaire


def evaluer_couverture(ticket):
    selection = ticket.get("selection", [])

    if len(selection) >= 8:
        couverture = "large"
    elif len(selection) >= 5:
        couverture = "équilibrée"
    else:
        couverture = "réduite"

    return {
        "couverture": couverture,
        "nombre_chevaux": len(selection)
    }


def comparer_tickets(tickets):
    """Compare des tickets sans planter si le risque est un objet descriptif."""
    classement = []
    poids_risque = {"faible": 1.0, "moyen": 2.0, "élevé": 3.0, "eleve": 3.0}

    for ticket in tickets:
        risque = ticket.get("risque", 0)
        potentiel = ticket.get("potentiel", 0)

        if isinstance(risque, dict):
            niveau = str(risque.get("niveau_risque", "moyen")).lower()
            risque_num = poids_risque.get(niveau, 2.0)
        else:
            try:
                risque_num = float(risque or 0)
            except (TypeError, ValueError):
                risque_num = 0.0

        try:
            potentiel_num = float(potentiel or 0)
        except (TypeError, ValueError):
            potentiel_num = 0.0

        classement.append({
            "ticket": ticket,
            "score_rapport": round(potentiel_num - risque_num, 3)
        })

    return sorted(classement, key=lambda x: x["score_rapport"], reverse=True)


def optimiser_champ_reduit(bases, chevaux):
    selection = list(dict.fromkeys(bases + chevaux))

    return {
        "selection_optimisee": selection,
        "taille": len(selection)
    }
