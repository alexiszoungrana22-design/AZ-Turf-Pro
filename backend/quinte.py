def generer_tickets_az(classement):
    """
    Génération des tickets AZ Turf Pro :
    - Quinté
    - Quarté
    - Trio
    - Champ réduit
    """

    if not classement:
        return {
            "quinte": [],
            "quarte": [],
            "trio": [],
            "champ_reduit": {
                "bases": [],
                "complements": []
            }
        }


    numeros = [
        cheval["numero"]
        for cheval in classement
    ]


    # Sélection AZ selon le classement

    base = numeros[:7]


    quinte = base[:5]

    quarte = base[:4]

    trio = base[:3]


    champ_reduit = {

        "bases": base[:3],

        "complements": base[3:7]

    }



    return {

        "quinte": quinte,

        "quarte": quarte,

        "trio": trio,

        "champ_reduit": champ_reduit

    }
