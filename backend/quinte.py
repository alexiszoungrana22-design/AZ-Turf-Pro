# =====================================
# AZ TURF PRO
# GENERATION DES TICKETS
# =====================================


# =====================================
# EXTRACTION DES NUMEROS
# =====================================

def extraire_numeros(classement):

    if not isinstance(classement, list):
        return []

    return [
        cheval.get("numero")
        for cheval in classement
        if isinstance(cheval, dict)
        and cheval.get("numero") is not None
    ]


# =====================================
# CHAMP REDUIT
# =====================================

def generer_champ_reduit(classement):

    numeros = extraire_numeros(classement)

    # Il faut au minimum 3 chevaux
    if len(numeros) < 3:
        return {
            "format": "",
            "bases": [],
            "complements": [],
            "disponible": False
        }

    # =================================
    # STRUCTURE DU CHAMP REDUIT
    #
    # Exemple souhaité :
    # 5-3-X-2-X / 1-4-8-7
    # =================================

    base_1 = numeros[0]
    base_2 = numeros[1]
    base_3 = numeros[2]

    bases = [
        base_1,
        base_2,
        "X",
        base_3,
        "X"
    ]

    # Le champ réduit AZ utilise exactement
    # 4 compléments après le "/".
    # Les compléments sont les 4 chevaux suivants
    # du classement AZ.
    complements = numeros[3:7]

    format_bases = "-".join(
        str(numero)
        for numero in bases
    )

    format_complements = "-".join(
        str(numero)
        for numero in complements
    )

    if format_complements:
        format_champ = (
            format_bases
            + " / "
            + format_complements
        )
    else:
        format_champ = format_bases

    return {
        "format": format_champ,
        "bases": bases,
        "complements": complements,
        "disponible": True
    }


# =====================================
# TICKET DERNIERE MINUTE
# =====================================

def generer_ticket_derniere_minute(classement):

    numeros = extraire_numeros(classement)

    # Le ticket dernière minute doit contenir
    # les 6 premiers chevaux disponibles.
    selection = numeros[:6]

    return {
        "selection": selection,
        "joker": None,
        "format": "-".join(
            map(str, selection)
        )
    }


# =====================================
# GENERATION DES TICKETS AZ
# =====================================

def generer_tickets_az(classement):

    numeros = extraire_numeros(classement)

    # =================================
    # Aucun cheval
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
        # Quinté gratuit : 7 chevaux maximum
        "quinte": numeros[:7],

        # 2 sur 4 : 4 chevaux
        "deux_sur_quatre": numeros[:4],

        # Couplé placé : 2 chevaux
        "couple_place": numeros[:2]
    }

    # =================================
    # PREMIUM
    # =================================

    # Sélection Premium :
    # toujours les 7 premiers disponibles
    selection_quinte = numeros[:7]

    # Quinté Premium :
    # 6 chevaux
    quinte = numeros[:6]

    # Quarté Premium :
    # 5 chevaux
    quarte = numeros[:5]

    # Trio Premium :
    # 3 chevaux
    trio = numeros[:3]

    # =================================
    # COUPLES GAGNANT / PLACE
    #
    # Exemple :
    # 5-3 / 5-2 / 3-2
    # =================================

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

        couples.append([
            numeros[1],
            numeros[2]
        ])

    # =================================
    # CHAMP REDUIT
    # =================================

    champ_reduit = generer_champ_reduit(
        classement
    )

    # =================================
    # DERNIERE MINUTE
    # =================================

    ticket_derniere_minute = (
        generer_ticket_derniere_minute(
            classement
        )
    )

    # =================================
    # PREMIUM COMPLET
    # =================================

    premium = {

        # Sélection Premium : 7 chevaux
        "selection_quinte":
            selection_quinte,

        # Quinté Premium : 6 chevaux
        "quinte":
            quinte,

        # Quarté Premium : 5 chevaux
        "quarte":
            quarte,

        # Trio Premium : 3 chevaux
        "trio":
            trio,

        # Couplé gagnant / placé
        "couple_gagnant_place":
            couples,

        # Champ réduit
        "champ_reduit":
            champ_reduit,

        # Ticket dernière minute : 6 chevaux
        "ticket_derniere_minute":
            ticket_derniere_minute,

        # Message
        "message_fin":
            "🍀 Bonne chance ! Les tickets Premium sont issus "
            "d'une analyse approfondie. Jouez toujours avec "
            "discipline et responsabilité."
    }

    # =================================
    # RESULTAT FINAL
    # =================================

    return {

        "gratuit":
            gratuit,

        "premium":
            premium

    }
    
