# =====================================
# AZ TURF PRO - GENERATION DES TICKETS
# Fichier complet corrigé : quinte.py
# =====================================


def extraire_numeros(classement):
    """Extrait la liste propre des numéros de chevaux."""
    if not isinstance(classement, list):
        return []
    return [
        str(c.get("numero"))
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
    """Ticket indépendant : marché + forme + régularité."""
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
    selection = [str(c.get("numero")) for c in ordre[:6]]
    joker = str(ordre[6].get("numero")) if len(ordre) > 6 else None

    return {
        "selection": selection,
        "joker": joker,
        "format": "-".join(map(str, selection)),
    }


def generer_tickets_az(classement):
    """Génère l'ensemble des tickets Gratuit et Premium avec Champ Réduit et Dernière Minute."""
    if not classement or not isinstance(classement, list):
        return {"gratuit": {}, "premium": {}}

    # 1. CLASSEMENT GRATUIT (Favoris purs basés sur l'indice AZ)
    ordre_az = sorted(
        [c for c in classement if isinstance(c, dict) and c.get("numero") is not None],
        key=lambda c: float(c.get("indice_az", 0) or 0),
        reverse=True
    )
    numeros_az = [str(c.get("numero")) for c in ordre_az]

    # 2. CLASSEMENT PREMIUM (Basé sur l'indice Premium)
    ordre_premium = sorted(
        [c for c in classement if isinstance(c, dict) and c.get("numero") is not None],
        key=lambda c: float(c.get("indice_premium", c.get("indice_az", 0)) or 0),
        reverse=True
    )
    numeros_premium = [str(c.get("numero")) for c in ordre_premium]

    # --- STRATÉGIE PREMIUM DIVERSIFIÉE ---
    selection_premium = []
    if len(numeros_premium) >= 6:
        base_favori = numeros_premium[0]       # Le Top favori
        challenger = numeros_premium[2]        # Le 3ème (Coup de cœur)
        outsider_1 = numeros_premium[4]        # Outsider rang 5
        outsider_2 = numeros_premium[5]        # Outsider rang 6
        
        selection_premium = [base_favori, challenger, outsider_1, outsider_2]
        
        for num in numeros_premium:
            if num not in selection_premium:
                selection_premium.append(num)
    else:
        selection_premium = numeros_premium

    # Formats des tickets Gratuit
    gratuit = {
        "quinte": numeros_az[:7],
        "deux_sur_quatre": numeros_az[:4],
        "couple_place": numeros_az[:2],
    }

    # Génération du Champ Réduit et de la Dernière Minute
    champ_reduit = generer_champ_reduit(ordre_premium)
    derniere_minute = generer_ticket_derniere_minute(classement)

    # Formats des tickets Premium complets
    premium = {
        "selection_quinte": selection_premium[:8],
        "quinte": selection_premium[:6],
        "quarte": selection_premium[:5],
        "trio": selection_premium[:3],
        "couple_gagnant_place": [
            [selection_premium[0], selection_premium[1]],
            [selection_premium[0], selection_premium[2]]
        ] if len(selection_premium) >= 3 else [],
        "champ_reduit": champ_reduit,
        "ticket_derniere_minute": derniere_minute,
        "methode": "Combinaison Optimisée AZ Pro (Base + Outsiders)",
        "message_fin": "🍀 Bonne chance ! Les tickets Premium incluent le champ réduit et l'analyse de dernière minute.",
    }

    return {"gratuit": gratuit, "premium": premium}
