from itertools import combinations


def generer_ticket_derniere_minute(classement):
    """
    Ticket dernière minute VIP.
    Sélection indépendante du ticket principal.
    5 chevaux + 1 joker.
    """

    if not classement or len(classement) < 6:
        return {
            "selection": [],
            "joker": None,
            "format": ""
        }

    numeros = [
        cheval.get("numero")
        for cheval in classement
        if cheval.get("numero") is not None
    ]

    selection = numeros[:5]
    joker = numeros[5]

    return {
        "selection": selection,
        "joker": joker,
        "format": "-".join(map(str, selection)) + " + " + str(joker)
    }



def generer_champ_reduit(classement):
    """
    Champ réduit Premium :

    - 3 bases
    - 2 X dynamiques
    - 4 compléments

    Les X peuvent changer de position.
    """

    if not classement or len(classement) < 7:
        return {
            "format": "",
            "bases": [],
            "complements": [],
            "positions_x": []
        }


    numeros = [
        cheval.get("numero")
        for cheval in classement
        if cheval.get("numero") is not None
    ]


    bases = numeros[:3]

    complements = numeros[3:7]


    # Position dynamique des X
    # selon la course
    indice_total = sum(
        bases
    )


    positions_modeles = [
        [1, 5],
        [2, 5],
        [1, 4],
        [4, 5]
    ]


    choix = indice_total % len(positions_modeles)

    positions_x = positions_modeles[choix]


    ticket = []

    position_base = 0


    for position in range(1, 6):

        if position in positions_x:
            ticket.append("X")

        else:
            ticket.append(str(bases[position_base]))
            position_base += 1


    return {
        "format": "-".join(ticket),
        "bases": bases,
        "complements": complements,
        "positions_x": positions_x
    }



def generer_tickets_az(classement):
    """
    Génération complète AZ Turf Pro

    GRATUIT :
    - Quinté 7 chevaux
    - 2 sur 4
    - Couplé placé

    VIP :
    - Quinté Premium 6 chevaux
    - Quarté 5 chevaux
    - Trio 4 chevaux
    - Couplé gagnant/placé
    - Champ réduit dynamique
    - Ticket dernière minute
    """

    if not isinstance(classement, list) or not classement:

        return {
            "gratuit": {},
            "vip": {}
        }


    numeros = [
        cheval.get("numero")
        for cheval in classement
        if cheval.get("numero") is not None
    ]


    base7 = numeros[:7]


    # ------------------
    # COUPLES VIP
    # ------------------

    trois_premiers = numeros[:3]

    couples = []

    if len(trois_premiers) == 3:

        couples = [
            [
                trois_premiers[0],
                trois_premiers[1]
            ],
            [
                trois_premiers[0],
                trois_premiers[2]
            ],
            [
                trois_premiers[1],
                trois_premiers[2]
            ]
        ]


    return {

        "gratuit": {

            "quinte": base7,

            "deux_sur_quatre": numeros[:4],

            "couple_place": numeros[:2]

        },


        "vip": {

            # Quinté Premium 6 chevaux
            "quinte": numeros[:6],


            # Quarté Premium 5 chevaux
            "quarte": numeros[:5],


            # Trio Premium 4 chevaux
            "trio": numeros[:4],


            "couple_gagnant_place": couples,


            "champ_reduit": generer_champ_reduit(
                classement
            ),


            "ticket_derniere_minute":
                generer_ticket_derniere_minute(
                    classement
                ),


            "message_fin":
                "🏇 Bonne chance aux membres Premium AZ Turf Pro. Jouez avec stratégie et responsabilité. Que vos chevaux soient à l'arrivée !"

        }

    }
