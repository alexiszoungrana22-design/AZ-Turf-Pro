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

    # Sélection indépendante du Premium : on privilégie des
    # chevaux de complément / outsiders du classement plutôt que
    # de recopier automatiquement les 6 premiers.
    indices = [4, 5, 7, 9, 11, 13]
    selection = [
        numeros[i]
        for i in indices
        if i < len(numeros)
    ]

    # Si le classement est trop court, compléter sans doublon.
    if len(selection) < min(6, len(numeros)):
        for numero in numeros:
            if numero not in selection:
                selection.append(numero)
            if len(selection) >= min(6, len(numeros)):
                break

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

    # Le Premium ne doit PAS recopier le ticket gratuit.
    # Il conserve les meilleures bases AZ mais introduit des
    # chevaux de complément issus des rangs suivants pour créer
    # une sélection réellement différente.
    #
    # Sélection Premium : rangs 1-4 + 6 + 8 + 9
    # Quinté Premium : rangs 1-4 + 6 + 8
    # Quarté Premium : rangs 1-3 + 6 + 8
    # Trio Premium : rangs 1 + 2 + 6
    indices_premium = [0, 1, 2, 3, 5, 7, 8]

    selection_quinte = [
        numeros[i]
        for i in indices_premium
        if i < len(numeros)
    ]

    quinte = selection_quinte[:6]

    indices_quarte = [0, 1, 2, 5, 7]
    quarte = [
        numeros[i]
        for i in indices_quarte
        if i < len(numeros)
    ]

    indices_trio = [0, 1, 5]
    trio = [
        numeros[i]
        for i in indices_trio
        if i < len(numeros)
    ]

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

    # La Dernière Minute est volontairement indépendante de la
    # sélection Premium : elle ne doit pas simplement recopier le
    # Quinté Premium.
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

    
