def generer_tickets_az(classement):
    """
    Génération des tickets AZ Turf Pro :
    - Quinté
    - Quarté
    - Trio
    - Couplé gagnant
    - Couplé placé
    - Champ réduit
    """

    if not isinstance(classement, list) or not classement:

        return {
            "quinte": [],
            "quarte": [],
            "trio": [],
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
            "couple_gagnant": [],
            "couple_place": [],
            "champ_reduit": {
                "bases": numeros,
                "complements": []
            }
        }



    base = numeros[:7]


    return {

        "quinte": base[:5],

        "quarte": base[:4],

        "trio": base[:3],


        # Les 2 premiers AZ
        # pour le couplé gagnant
        "couple_gagnant": [
            base[0],
            base[1]
        ],


        # Plusieurs possibilités couplé placé
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
