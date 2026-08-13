# =====================================
# AZ TURF PRO - GENERATION DES TICKETS
# Fichier complet à remplacer : quinte.py
# =====================================


def extraire_numeros(classement):
    """Extrait la liste propre des numéros de chevaux à partir du classement."""
    if not isinstance(classement, list):
        return []
    return [
        c.get("numero")
        for c in classement
        if isinstance(c, dict) and c.get("numero") is not None
    ]


def generer_champ_reduit(classement):
    """Génère une formule en Champ Réduit pour le ticket Premium."""
    numeros = extraire_numeros(classement)
    if len(numeros) < 3:
        return {"format": "", "bases": [], "complements": [], "disponible": False}

    bases = [numeros[0], numeros[1], "X", numeros[2], "X"]
    complements = numeros[3:7] if len(numeros) >= 4 else []

    format_str = "-".join(map(str, bases))
    if complements:
        format_str += " / " + "-".join(map(str, complements))

    return {
        "format": format_str,
        "bases": bases,
        "complements": complements,
        "disponible": True,
    }


def generer_ticket_derniere_minute(classement):
    """Ticket indépendant basique : marché + forme (pas le simple top AZ)."""
    if not isinstance(classement, list):
        return {"selection": [], "joker": None, "format": ""}

    valides = [
        c
        for c in classement
        if isinstance(c, dict) and c.get("numero") is not None
    ]

    def score_marche(c):
        cote = float(c.get("cote", 0) or 0)
        forme = float(c.get("forme", 5) or 5)
        regularite = float(c.get("regularite", 5) or 5)
        return cote * 2.0 + forme * 1.2 + regularite * 0.8

    ordre = sorted(valides, key=score_marche, reverse=True)
    selection = [c.get("numero") for c in ordre[:6]]
    joker = ordre[6].get("numero") if len(ordre) > 6 else None

    return {
        "selection": selection,
        "joker": joker,
        "format": "-".join(map(str, selection)),
    }


def generer_tickets_az(classement):
    """Génère la structure complète des tickets Gratuit et Premium."""
    numeros_az = extraire_numeros(classement)
    if not numeros_az:
        return {"gratuit": {}, "premium": {}}

    # =========================================================
    # 1. TICKET GRATUIT (Basé strictement sur l'indice AZ)
    # =========================================================
    gratuit = {
        "quinte": numeros_az[:7],
        "deux_sur_quatre": numeros_az[:4],
        "couple_place": numeros_az[:2],
    }

    # =========================================================
    # 2. TICKET PREMIUM (Basé sur l'indice Premium indépendant)
    # =========================================================
    premium_ordre = sorted(
        [
            c
            for c in classement
            if isinstance(c, dict) and c.get("numero") is not None
        ],
        key=lambda c: float(
            c.get("indice_premium", c.get("indice_az", 0)) or 0
        ),
        reverse=True,
    )
    premium_numeros = [c.get("numero") for c in premium_ordre]

    # Définition de la sélection Premium (jusqu'à 8 chevaux)
    selection_quinte = premium_numeros[:8]

    # Force la différenciation : si les 7 premiers Premium sont identiquement les 7 premiers AZ,
    # on remplace le 8e par le 8e du classement AZ.
    if (
        len(numeros_az) > 7
        and len(selection_quinte) >= 8
        and not any(n not in numeros_az[:7] for n in selection_quinte[:7])
    ):
        selection_quinte = selection_quinte[:7] + [numeros_az[7]]

    quinte = selection_quinte[:6]
    quarte = selection_quinte[:5]
    trio = selection_quinte[:3]

    # Génération sécurisée des couples (évite IndexError si < 3 partants)
    couples = []
    if len(selection_quinte) >= 3:
        for a, b in (
            (selection_quinte[0], selection_quinte[1]),
            (selection_quinte[0], selection_quinte[2]),
            (selection_quinte[1], selection_quinte[2]),
        ):
            couples.append([a, b])
    elif len(selection_quinte) == 2:
        couples.append([selection_quinte[0], selection_quinte[1]])

    champ_reduit = generer_champ_reduit(premium_ordre)
    derniere = generer_ticket_derniere_minute(classement)

    premium = {
        "selection_quinte": selection_quinte,
        "quinte": quinte,
        "quarte": quarte,
        "trio": trio,
        "couple_gagnant_place": couples,
        "champ_reduit": champ_reduit,
        "ticket_derniere_minute": derniere,
        "methode": "Indice Premium : AZ + forme + régularité + marché + expérience + performances",
        "message_fin": "🍀 Bonne chance ! Les tickets Premium utilisent une lecture complémentaire de l'analyse AZ. Jouez avec discipline et responsabilité.",
    }

    return {"gratuit": gratuit, "premium": premium}
