# =====================================
# AZ TURF PRO - GENERATION DES TICKETS
# Fichier complet à remplacer : quinte.py
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


def generer_tickets_az(classement):
    """Génère la structure complète des tickets Gratuit et Premium avec garantie de différence."""
    if not classement or not isinstance(classement, list):
        return {"gratuit": {}, "premium": {}}

    # 1. CLASSEMENT GRATUIT (Basé strictement sur indice_az / Favoris)
    ordre_az = sorted(
        [c for c in classement if isinstance(c, dict) and c.get("numero") is not None],
        key=lambda c: float(c.get("indice_az", 0) or 0),
        reverse=True
    )
    numeros_az = [str(c.get("numero")) for c in ordre_az]

    # 2. CLASSEMENT PREMIUM (Basé sur indice_premium / Value & Spéculation)
    ordre_premium = sorted(
        [c for c in classement if isinstance(c, dict) and c.get("numero") is not None],
        key=lambda c: float(c.get("indice_premium", c.get("indice_az", 0)) or 0),
        reverse=True
    )
    numeros_premium = [str(c.get("numero")) for c in ordre_premium]

    # --- FORCER LA DIFFÉRENCIATION SI LES LISTES SONT IDENTIQUES ---
    if len(numeros_az) >= 4 and numeros_az[:4] == numeros_premium[:4]:
        # On intervertit le 3ème ou 4ème cheval par un outsider (rang 5 à 8) dans le Premium
        if len(numeros_premium) >= 5:
            outsider = numeros_premium[4]
            # On insère l'outsider en position 3 du ticket Premium
            numeros_premium.pop(4)
            numeros_premium.insert(2, outsider)

    # Construction des sélections
    gratuit = {
        "quinte": numeros_az[:7],
        "deux_sur_quatre": numeros_az[:4],
        "couple_place": numeros_az[:2],
    }

    selection_quinte = numeros_premium[:8]
    quinte = selection_quinte[:6]
    quarte = selection_quinte[:5]
    trio = selection_quinte[:3]

    couples = []
    if len(selection_quinte) >= 3:
        couples = [
            [selection_quinte[0], selection_quinte[1]],
            [selection_quinte[0], selection_quinte[2]],
            [selection_quinte[1], selection_quinte[2]]
        ]

    premium = {
        "selection_quinte": selection_quinte,
        "quinte": quinte,
        "quarte": quarte,
        "trio": trio,
        "couple_gagnant_place": couples,
        "champ_reduit": generer_champ_reduit(ordre_premium),
        "methode": "Analyse VLB / Indice Premium AZ Pro",
    }

    return {"gratuit": gratuit, "premium": premium}
