def generer_tickets_az(classement):
    """
    Génération des tickets AZ Turf Pro

    GRATUIT :
    - Quinté 8 chevaux
    - Quarté 5 chevaux
    - Tiercé 4 chevaux
    - 2 sur 4 4 chevaux

    VIP :
    - Ticket 7 chevaux
    - Ticket 5 chevaux
    - Champ réduit dynamique
    - Couplé gagnant
    - Couplé placé
    """

    if not isinstance(classement, list) or not classement:
        return {
            "quinte": [],
            "quarte": [],
            "trio": [],
            "deux_sur_quatre": [],
            "couple_gagnant": [],
            "couple_place": [],
            "vip": {
                "ticket_7": [],
                "ticket_5": [],
                "champ_reduit": {
                    "format": "",
                    "bases": [],
                    "complements": []
                }
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
            "vip": {
                "ticket_7": numeros,
                "ticket_5": numeros,
                "champ_reduit": {
                    "format": "",
                    "bases": numeros,
                    "complements": []
                }
            }
        }


    # Base analyse AZ
    base_az = numeros[:7]

    # Base gratuite
    base_gratuite = numeros[:8]


    # -------------------------
    # Champ réduit dynamique
    # -------------------------

    bases = base_az[:5]

    # Placement dynamique des X
    champ = [
        bases[0],
        "X",
        bases[1],
        bases[2],
        "X"
    ]

    complements = base_az[3:7]

    format_champ = (
        f"{champ[0]}-{champ[1]}-{champ[2]}-"
        f"{champ[3]}-{champ[4]}/"
        f"{'-'.join(map(str, complements))}"
    )


    return {

        # GRATUIT

        "quinte": base_gratuite[:8],

        "quarte": base_gratuite[:5],

        "trio": base_gratuite[:4],

        "deux_sur_quatre": base_gratuite[:4],



        # COUPLES

        "couple_gagnant": [
            base_az[0],
            base_az[1]
        ],


        "couple_place": [
            [
                base_az[0],
                base_az[1]
            ],
            [
                base_az[0],
                base_az[2]
            ],
            [
                base_az[1],
                base_az[2]
            ]
        ],



        # VIP

        "vip": {

            "ticket_7": base_az[:7],

            "ticket_5": base_az[:5],

            "champ_reduit": {

                "format": format_champ,

                "bases": champ,

                "complements": complements

            }

        }

    }
