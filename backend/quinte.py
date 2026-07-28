def generer_tickets_az(classement):
    """
    Génération des tickets AZ Turf Pro

    GRATUIT :
    - Quinté 7 chevaux
    - 2 sur 4 4 chevaux
    - Couplé placé 2 chevaux

    VIP :
    - Quinté Premium 7 chevaux
    - Quarté 5 chevaux
    - Trio 4 chevaux
    - Champ réduit
    - Couplé gagnant/placé 3 chevaux
    """

    if not isinstance(classement, list) or not classement:
        return {}


    numeros = []

    for cheval in classement:
        numero = cheval.get("numero")
        if numero is not None:
            numeros.append(numero)


    base7 = numeros[:7]
    base5 = numeros[:5]
    base4 = numeros[:4]


    # Couplé VIP 3 chevaux
    couple_vip = base7[:3]

    couples = [
        [couple_vip[0], couple_vip[1]],
        [couple_vip[0], couple_vip[2]],
        [couple_vip[1], couple_vip[2]]
    ]


    # Couplé placé gratuit 2 chevaux
    couple_place_gratuit = [
        base7[0],
        base7[1]
    ]


    # Champ réduit
    bases = base7[:5]

    champ = [
        bases[0],
        "X",
        bases[1],
        bases[2],
        "X"
    ]

    complements = base7[3:7]


    format_champ = (
        f"{champ[0]}-{champ[1]}-{champ[2]}-"
        f"{champ[3]}-{champ[4]}/"
        f"{'-'.join(map(str, complements))}"
    )


    return {


        # GRATUIT

        "gratuit": {

            "quinte": base7,

            "deux_sur_quatre": base4,

            "couple_place": couple_place_gratuit

        },


        # VIP

        "vip": {

            "quinte": base7,

            "quarte": base5,

            "trio": base4,

            "couple_gagnant_place": couples,

            "champ_reduit": {

                "format": format_champ,

                "bases": champ,

                "complements": complements

            }

        }

    }
