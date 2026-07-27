def generer_tickets_az(classement):
    """
    Génération des tickets AZ Turf Pro :

    Partie gratuite :
    - Quinté : 8 chevaux
    - Quarté : 5 chevaux
    - Tiercé : 4 chevaux
    - 2 sur 4 : 4 chevaux

    Partie avancée :
    - Couplé gagnant
    - Couplé placé
    - Champ réduit
    """

    if not isinstance(classement, list) or not classement:

        return {
            "quinte": [],
            "quarte": [],
            "trio": [],
            "deux_sur_quatre": [],
            "couple_gagnant": [],
            "couple_place": [],
            "champ_reduit": {
                "bases": [],
                "complements": []
            }
        }


    numeros = []


    for cheval in classement:

        numero = cheval.get("numero")

        if numero is not None:
            numeros.append(numero)



    if len(numeros) < 2:

        return {

            "quinte": numeros,

            "quarte": numeros,

            "trio": numeros,

            "deux_sur_quatre": numeros,

            "couple_gagnant": [],

            "couple_place": [],

            "champ_reduit": {

                "bases": numeros,

                "complements": []

            }

        }



    # Base AZ principale

    base = numeros[:7]


    # Base gratuite élargie

    base_gratuite = numeros[:8]



    return {


        # =========================
        # TICKETS GRATUITS
        # =========================


        "quinte": base_gratuite[:8],


        "quarte": base_gratuite[:5],


        "trio": base_gratuite[:4],


        "deux_sur_quatre": base_gratuite[:4],





        # =========================
        # TICKETS AVANCES
        # =========================


        "couple_gagnant": [

            base[0],

            base[1]

        ],



        "couple_place": [

            [
                base[0],
                base[1]
            ],

            [
                base[0],
                base[2]
            ],

            [
                base[1],
                base[2]
            ]

        ],





        "champ_reduit": {

            "bases": base[:3],

            "complements": base[3:7]

        }


    }
