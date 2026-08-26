
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
    classement = []

    for ticket in tickets:
        risque = ticket.get("risque", 0)
        potentiel = ticket.get("potentiel", 0)

        classement.append({
            "ticket": ticket,
            "score_rapport": potentiel - risque
        })

    return sorted(
        classement,
        key=lambda x: x["score_rapport"],
        reverse=True
    )


def optimiser_champ_reduit(bases, chevaux):
    selection = list(dict.fromkeys(bases + chevaux))

    return {
        "selection_optimisee": selection,
        "taille": len(selection)
    }
