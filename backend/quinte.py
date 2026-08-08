# =====================================
# AZ TURF PRO - GENERATION DES TICKETS
# =====================================


def extraire_numeros(classement):
    """
    Extrait les numéros des chevaux dans l'ordre du classement AZ.
    """
    return [
        cheval.get("numero")
        for cheval in classement
        if cheval.get("numero") is not None
    ]


# =====================================
# CHAMP RÉDUIT
# =====================================

def generer_champ_reduit(classement):
    """
    Format :
    1er-2e-X-4e-X / 5e-6e-7e-8e

    Exemple avec :
    5, 3, 1, 2, 4, 8, 7, 6

    donne :
    5-3-X-2-X / 4-8-7-6
    """

    numeros = extraire_numeros(classement)

    if len(numeros) < 7:
        return {
            "format": "",
            "bases": [],
            "complements": []
        }

    bases = [
        numeros[0],
        numeros[1],
        "X",
        numeros[3],
        "X"
    ]

    complements = [
        numeros[4],
        numeros[5],
        numeros[6]
    ]

    # Le format demandé prévoit 4 compléments.
    # Si le classement contient au moins 8 chevaux,
    # le 8e est ajouté automatiquement.
    if len(numeros) >= 8:
        complements.append(numeros[7])

    return {
        "format": (
            "-".join(map(str, bases))
            + " / "
            + "-".join(map(str, complements))
        ),
        "bases": bases,
        "complements": complements
    }


# =====================================
# TICKET DERNIÈRE MINUTE
# =====================================

def generer_ticket_derniere_minute(classement):
    """
    Ticket dernière minute :
    6 chevaux.
    """

    numeros = extraire_numeros(classement)

    selection = numeros[:6]

    return {
        "selection": selection,
        "joker": None,
        "format": "-".join(map(str, selection))
    }


# =====================================
# GÉNÉRATION DES TICKETS AZ
# =====================================

def generer_tickets_az(classement):

    numeros = extraire_numeros(classement)

    # =================================
    # PROTECTION
    # =================================

    if not numeros:
        return {
            "gratuit": {},
            "premium": {}
        }

    # =================================
    # GRATUIT
    # =================================

    gratuit = {
        # Quinté gratuit : maximum 7 chevaux
        "quinte": numeros[:7],

        # 2 sur 4 : 4 chevaux
        "deux_sur_quatre": numeros[:4],

        # Couplé placé : 2 chevaux
        "couple_place": numeros[:2]
    }

    # =================================
    # COUPLÉS PREMIUM
    # =================================

    # Les 3 premiers chevaux du classement
    # donnent les trois couples :
    #
    # 1er-2e
    # 1er-3e
    # 2e-3e

    couples = []

    if len(numeros) >= 2:
        couples.append([
            numeros[0],
            numeros[1]
        ])

    if len(numeros) >= 3:
        couples.append([
            numeros[0],
            numeros[2]
        ])

    if len(numeros) >= 3:
        couples.append([
            numeros[1],
            numeros[2]
        ])

    # =================================
    # PREMIUM
    # =================================

    premium = {

        # -----------------------------
        # Sélection Premium
        # -----------------------------
        # Maximum 7 chevaux
        "selection_quinte":
            numeros[:7],

        # -----------------------------
        # Quinté Premium
        # -----------------------------
        # 6 chevaux
        "quinte":
            numeros[:6],

        # -----------------------------
        # Quarté Premium
        # -----------------------------
        # 5 chevaux
        "quarte":
            numeros[:5],

        # -----------------------------
        # Trio Premium
        # -----------------------------
        # 3 chevaux
        "trio":
            numeros[:3],

        # -----------------------------
        # Couplé gagnant / placé
        # -----------------------------
        "couple_gagnant_place":
            couples,

        # -----------------------------
        # Champ réduit
        # -----------------------------
        "champ_reduit":
            generer_champ_reduit(classement),

        # -----------------------------
        # Dernière minute
        # -----------------------------
        "ticket_derniere_minute":
            generer_ticket_derniere_minute(classement),

        # -----------------------------
        # Message
        # -----------------------------
        "message_fin":
            (
                "🍀 Bonne chance ! Les tickets Premium sont issus "
                "d'une analyse approfondie. Jouez toujours avec "
                "discipline et responsabilité."
            )
    }

    # =================================
    # RETOUR FINAL
    # =================================

    return {
        "gratuit": gratuit,
        "premium": premium
    }

