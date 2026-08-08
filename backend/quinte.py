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
        if isinstance(cheval, dict)
        and cheval.get("numero") is not None
    ]


# =====================================
# CHAMP RÉDUIT
# =====================================

def generer_champ_reduit(classement):
    """
    Format Premium voulu :

    5-3-X-2-X / 1-4-8-7

    Les 2e et 4e positions correspondent aux chevaux
    classés n°2 et n°4 dans la sélection AZ.

    Les compléments utilisent les chevaux suivants
    du classement.
    """

    numeros = extraire_numeros(classement)

    if not numeros:
        return {
            "format": "",
            "bases": [],
            "complements": []
        }

    # Bases :
    # position 1 = cheval AZ n°1
    # position 2 = cheval AZ n°2
    # position 3 = X
    # position 4 = cheval AZ n°4
    # position 5 = X

    bases = [
        numeros[0] if len(numeros) > 0 else None,
        numeros[1] if len(numeros) > 1 else None,
        "X",
        numeros[3] if len(numeros) > 3 else None,
        "X"
    ]

    # Pour le format Premium normal, les compléments
    # correspondent aux chevaux 5, 6, 3 et 7 du classement.
    candidats_complements = []

    for index in (4, 5, 2, 6):
        if index < len(numeros):
            numero = numeros[index]
            if numero not in candidats_complements:
                candidats_complements.append(numero)

    bases_affichage = [
        "X" if numero is None else numero
        for numero in bases
    ]

    return {
        "format": (
            "-".join(map(str, bases_affichage))
            + " / "
            + "-".join(map(str, candidats_complements))
        ),
        "bases": bases_affichage,
        "complements": candidats_complements
    }


# =====================================
# TICKET DERNIÈRE MINUTE
# =====================================

def generer_ticket_derniere_minute(classement):
    """
    Ticket dernière minute :
    6 chevaux maximum, dans l'ordre du classement AZ.
    """

    numeros = extraire_numeros(classement)

    selection = numeros[:6]

    return {
        "selection": selection,
        "joker": None,
        "format": "-".join(map(str, selection))
    }


# =====================================
# COUPLÉS GAGNANT / PLACÉ
# =====================================

def generer_couples(classement):
    """
    Format voulu :

    5-3 / 5-2 / 3-2

    Les trois premiers chevaux du classement
    sont utilisés dans l'ordre AZ.
    """

    numeros = extraire_numeros(classement)

    if len(numeros) < 2:
        return []

    couples = []

    # 1er - 2e
    couples.append([
        numeros[0],
        numeros[1]
    ])

    # 1er - 3e
    if len(numeros) >= 3:
        couples.append([
            numeros[0],
            numeros[2]
        ])

    # 2e - 3e
    if len(numeros) >= 3:
        couples.append([
            numeros[1],
            numeros[2]
        ])

    return couples


def format_couples(couples):
    """
    Transforme :

    [[5, 3], [5, 2], [3, 2]]

    en :

    5-3 / 5-2 / 3-2
    """

    formats = []

    for couple in couples:
        if (
            isinstance(couple, list)
            and len(couple) == 2
        ):
            formats.append(
                f"{couple[0]}-{couple[1]}"
            )

    return " / ".join(formats)


# =====================================
# GENERATION PRINCIPALE DES TICKETS
# =====================================

def generer_tickets_az(classement):

    numeros = extraire_numeros(classement)

    # Aucun cheval
    if not numeros:
        return {
            "gratuit": {},
            "premium": {}
        }

    # =================================
    # GRATUIT
    # =================================

    gratuit = {

        # Quinté gratuit :
        # maximum 7 chevaux
        "quinte":
            numeros[:7],

        # 2 sur 4 :
        # 4 chevaux
        "deux_sur_quatre":
            numeros[:4],

        # Couplé placé :
        # 2 chevaux
        "couple_place":
            numeros[:2]
    }

    # =================================
    # PREMIUM
    # =================================

    # ---------------------------------
    # Sélection Premium
    # ---------------------------------
    #
    # Format cible : 7 chevaux
    #
    selection_quinte = numeros[:7]

    # ---------------------------------
    # Quinté Premium
    # ---------------------------------
    #
    # Format cible : 6 chevaux
    #
    quinte_premium = numeros[:6]

    # ---------------------------------
    # Quarté Premium
    # ---------------------------------
    #
    # Format cible : 5 chevaux
    #
    quarte_premium = numeros[:5]

    # ---------------------------------
    # Trio Premium
    # ---------------------------------
    #
    # Format cible : 3 chevaux
    #
    trio_premium = numeros[:3]

    # ---------------------------------
    # Couplés
    # ---------------------------------

    couples = generer_couples(classement)

    couples_format = format_couples(couples)

    # ---------------------------------
    # Champ réduit
    # ---------------------------------

    champ_reduit = generer_champ_reduit(
        classement
    )

    # ---------------------------------
    # Dernière minute
    # ---------------------------------

    derniere_minute = (
        generer_ticket_derniere_minute(
            classement
        )
    )

    # =================================
    # OBJET PREMIUM
    # =================================

    premium = {

        # Sélection Premium 7 chevaux
        "selection_quinte":
            selection_quinte,

        # Alias explicite
        "selection_premium":
            selection_quinte,

        # Quinté Premium 6 chevaux
        "quinte":
            quinte_premium,

        # Quarté Premium 5 chevaux
        "quarte":
            quarte_premium,

        # Trio Premium 3 chevaux
        "trio":
            trio_premium,

        # Couplé gagnant / placé
        "couple_gagnant_place":
            couples,

        "couples":
            couples,

        "couples_format":
            couples_format,

        # Champ réduit
        "champ_reduit":
            champ_reduit,

        # Dernière minute 6 chevaux
        "ticket_derniere_minute":
            derniere_minute,

        # Message Premium
        "message_fin":
            (
                "🍀 Bonne chance ! Les tickets Premium "
                "sont issus d'une analyse approfondie. "
                "Jouez toujours avec discipline et responsabilité."
            )
    }

    # =================================
    # RETOUR FINAL
    # =================================

    return {

        "gratuit":
            gratuit,

        "premium":
            premium

    }


# =====================================
# TEST DIRECT DU MODULE
# =====================================

if __name__ == "__main__":

    exemple = [
        {"numero": 5},
        {"numero": 3},
        {"numero": 1},
        {"numero": 2},
        {"numero": 4},
        {"numero": 8},
        {"numero": 7}
    ]

    tickets = generer_tickets_az(
        exemple
    )

    print("=====================================")
    print("AZ TURF PRO - TEST TICKETS")
    print("=====================================")

    print(
        "Sélection Premium :",
        tickets["premium"]["selection_premium"]
    )

    print(
        "Quinté Premium :",
        tickets["premium"]["quinte"]
    )

    print(
        "Quarté Premium :",
        tickets["premium"]["quarte"]
    )

    print(
        "Trio Premium :",
        tickets["premium"]["trio"]
    )

    print(
        "Couplés :",
        tickets["premium"]["couples_format"]
    )

    print(
        "Champ réduit :",
        tickets["premium"]["champ_reduit"]["format"]
    )

    print(
        "Dernière minute :",
        tickets["premium"]["ticket_derniere_minute"]["format"]
    )
