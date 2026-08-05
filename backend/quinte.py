# AZ TURF PRO - GENERATION DES TICKETS
# =====================================


def extraire_numeros(classement):

    return [
        cheval.get("numero")
        for cheval in classement
        if cheval.get("numero") is not None
    ]



def generer_champ_reduit(classement):

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
        numeros[2],
        numeros[6]
    ]


    return {
        "format":
            "-".join(map(str, bases))
            + " / "
            + "-".join(map(str, complements)),

        "bases": bases,

        "complements": complements
    }





def generer_ticket_derniere_minute(classement):

    numeros = extraire_numeros(classement)


    if len(numeros) < 7:

        return {
            "selection": [],
            "joker": None,
            "format": ""
        }


    selection = numeros[:6]

    joker = numeros[6]


    return {
        "selection": selection,
        "joker": joker,
        "format":
            "-".join(map(str, selection))
            + " + "
            + str(joker)
    }





def generer_tickets_az(classement):


    numeros = extraire_numeros(classement)


    if len(numeros) < 7:

        return {
            "gratuit": {},
            "premium": {}
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
                numeros[0],
                numeros[1]
            ]

    }





    # =========================
    # PREMIUM
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



    premium = {

        # Sélection Quinté Premium affichée en haut
        "selection_quinte":
            numeros[:7],


        # Ticket Quinté Premium joué
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

        "premium": premium

    }
