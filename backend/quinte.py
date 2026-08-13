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
    # Exemple souhaitÃ© :
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

    # Le champ rÃ©duit AZ utilise exactement
    # 4 complÃ©ments aprÃ¨s le "/".
    # Les complÃ©ments sont les 4 chevaux suivants
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

    # Le ticket "derniÃ¨re minute" reflÃ¨te la tendance du marchÃ©
    # (cote), pas le classement AZ pur : il peut donc lÃ©gitimement
    # diffÃ©rer de la SÃ©lection/QuintÃ© Premium (basÃ©s sur l'indice
    # AZ). C'est cohÃ©rent avec l'idÃ©e rÃ©elle d'un ticket "derniÃ¨re
    # minute", gÃ©nÃ©ralement liÃ© aux derniers mouvements de cotes
    # avant le dÃ©part.

    if not isinstance(classement, list):
        return {
            "selection": [],
            "joker": None,
            "format": ""
        }

    chevaux_valides = [
        cheval
        for cheval in classement
        if isinstance(cheval, dict)
        and cheval.get("numero") is not None
    ]

    # Tri par cote (score de favori marchÃ©, 0-10, plus haut =
    # plus favori) plutÃ´t que par ordre du classement AZ.
    classement_par_cote = sorted(
        chevaux_valides,
        key=lambda c: c.get("cote", 0),
        reverse=True
    )

    selection = [
        cheval.get("numero")
        for cheval in classement_par_cote[:6]
    ]

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
        # QuintÃ© gratuit : 7 chevaux maximum
        "quinte": numeros[:7],

        # 2 sur 4 : 4 chevaux
        "deux_sur_quatre": numeros[:4],

        # CouplÃ© placÃ© : 2 chevaux
        "couple_place": numeros[:2]
    }

    # =================================
    # PREMIUM
    # =================================

    # SÃ©lection Premium :
    # 8 chevaux (le dÃ©tail complet de l'analyse AZ,
    # cohÃ©rent avec la "SÃ©lection du jour" affichÃ©e
    # sur la page Analyse). Volontairement diffÃ©rente
    # du QuintÃ© Gratuit (7 chevaux) pour ne pas offrir
    # exactement le mÃªme contenu aux deux niveaux.
    selection_quinte = numeros[:8]

    # QuintÃ© Premium :
    # 6 chevaux
    quinte = numeros[:6]

    # QuartÃ© Premium :
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

        # SÃ©lection Premium : 7 chevaux
        "selection_quinte":
            selection_quinte,

        # QuintÃ© Premium : 6 chevaux
        "quinte":
            quinte,

        # QuartÃ© Premium : 5 chevaux
        "quarte":
            quarte,

        # Trio Premium : 3 chevaux
        "trio":
            trio,

        # CouplÃ© gagnant / placÃ©
        "couple_gagnant_place":
            couples,

        # Champ rÃ©duit
        "champ_reduit":
            champ_reduit,

        # Ticket derniÃ¨re minute : 6 chevaux
        "ticket_derniere_minute":
            ticket_derniere_minute,

        # Message
        "message_fin":
            "ðŸ€ Bonne chance ! Les tickets Premium sont issus "
            "d'une analyse approfondie. Jouez toujours avec "
            "discipline et responsabilitÃ©."
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
    
