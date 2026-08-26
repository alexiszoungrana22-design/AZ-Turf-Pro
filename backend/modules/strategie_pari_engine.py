
"""
AZ TURF PRO EXPERT V11
Moteur de stratégie pari.
Couche complémentaire indépendante.
"""

def definir_profil_parieur(mode="equilibre"):
    profils = {
        "prudent": {
            "objectif": "sécuriser",
            "risque": "faible",
            "priorite": "bases solides"
        },
        "equilibre": {
            "objectif": "compromis",
            "risque": "moyen",
            "priorite": "bases + valeurs"
        },
        "offensif": {
            "objectif": "chercher le rapport",
            "risque": "élevé",
            "priorite": "outsiders"
        }
    }

    return profils.get(mode, profils["equilibre"])


def construire_ticket_strategique(selection, mode="equilibre"):
    profil = definir_profil_parieur(mode)

    if mode == "prudent":
        ticket = selection[:4]
    elif mode == "offensif":
        ticket = selection[-4:]
    else:
        ticket = selection[:5]

    return {
        "mode": mode,
        "profil": profil,
        "selection": ticket
    }


def evaluer_risque_ticket(ticket):
    nombre = len(ticket.get("selection", []))

    if nombre <= 3:
        niveau = "élevé"
    elif nombre <= 5:
        niveau = "modéré"
    else:
        niveau = "réduit"

    return {
        "niveau_risque": niveau,
        "selection": ticket.get("selection", [])
    }
