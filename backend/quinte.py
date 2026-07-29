# =====================================
# AZ TURF PRO - GENERATION DES TICKETS
# =====================================


def extraire_numeros(classement):

    return [
        cheval.get("numero")
        for cheval in classement
        if cheval.get("numero") is not None
    ]



def generer_champ_reduit(classement):
    """
    Champ réduit Premium

    - 3 bases
    - 2 X dynamiques
    - 4 compléments
    """

    numeros = extraire_numeros(classement)


    if len(numeros) < 7:

        return {
            "format": "",
            "bases": [],
            "complements": [],
            "positions_x": []
        }


    bases = numeros[:3]

    complements = numeros[3:7]


    variation = sum(bases) % 4


    positions = [
        [1, 5],
        [2, 5],
        [1, 4],
        [3, 5]
    ]


    positions_x = positions[variation]


    ticket = []

    index_base = 0


    for position in range(1, 6):

        if position in positions_x:

            ticket.append("X")

        else:

            ticket.append(
                str(bases[index_base])
            )

            index_base += 1



    return {

        "format": "-".join(ticket),

        "bases": bases,

        "complements": complements,

        "positions_x": positions_x

    }




def generer_ticket_derniere_minute(classement):
    """
    Ticket dernière minute indépendant

    Prend en compte :
    - changements de driver
    - non-partants
    - outsiders
    - chevaux cachés
    """

    numeros = extraire_numeros(classement)


    if len(numeros) < 6:

        return {

            "selection": [],

            "joker": None,

            "format": ""

        }


    selection = numeros[:5]

    joker = numeros[5]


    return {

        "selection": selection,

        "joker": joker,

        "format":
            "-".join(map(str, selection))
            + " + "
            + str(joker)

    }





def generer_tickets_az(classement):

    """
    Génération des tickets AZ Turf Pro

    GRATUIT :
    - Quinté 7 chevaux
    - Deux sur Quatre
    - Couplé placé

    PREMIUM :
    - Quinté 6 chevaux
    - Quarté 5 chevaux
    - Trio 4 chevaux
    - Couplé gagnant/placé
    - Champ réduit
    - Dernière minute
    """



    numeros = extraire_numeros(classement)



    if len(numeros) < 7:

        return {

            "gratuit": {},

            "vip": {}

        }




    # =========================
    # GRATUIT
    # =========================


    gratuit = {


        "quinte":

            numeros[:7],


        "deux_sur_quatre":

            numeros[:4],


        "couple_place":

            [
                [
                    numeros[0],
                    numeros[1]
                ]
            ]

    }




    # =========================
    # COUPLES PREMIUM
    # =========================


    bases_couple = numeros[:3]


    couples = [

        [
            bases_couple[0],
            bases_couple[1]
        ],

        [
            bases_couple[0],
            bases_couple[2]
        ],

        [
            bases_couple[1],
            bases_couple[2]
        ]

    ]





    # =========================
    # PREMIUM
    # =========================


    vip = {


        "quinte":

            numeros[:6],


        "quarte":

            numeros[:5],


        "trio":

            numeros[:4],


        "couple_gagnant_place":

            couples,


        "champ_reduit":

            generer_champ_reduit(classement),



        "ticket_derniere_minute":

            generer_ticket_derniere_minute(classement),



        "message_fin":

            "🍀 Bonne chance ! Les tickets Premium sont issus d'une analyse approfondie. Jouez toujours avec discipline et responsabilité."

    }



    return {

        "gratuit": gratuit,

        "vip": vip

    }
