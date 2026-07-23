def generer_tickets_az(classement):
    """
    Génération des tickets AZ Turf Pro
    à partir du classement des chevaux
    """

    if not classement or len(classement) < 3:
        return {
            "quinte": [],
            "quarte": [],
            "trio": [],
            "champ_reduit": []
        }


    numeros = [
        cheval["numero"]
        for cheval in classement
    ]


    # Les meilleurs chevaux AZ

    base = numeros[:7]


    ticket = {

        "quinte": base[:5],

        "quarte": base[:4],

        "trio": base[:3],

        "champ_reduit": {
            "bases": base[:3],
            "complements": base[3:7]
        }

    }


    return ticket
