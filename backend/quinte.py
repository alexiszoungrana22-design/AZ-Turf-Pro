def generer_tickets_az(classement):
    """
    Génération des tickets AZ Turf Pro :
    - Quinté
    - Quarté
    - Trio
    - Champ réduit
    """

    if not isinstance(classement, list) or not classement:
        return {
            "quinte": [],
            "quarte": [],
            "trio": [],
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


    if not numeros:
        return {
            "quinte": [],
            "quarte": [],
            "trio": [],
            "champ_reduit": {
                "bases": [],
                "complements": []
            }
        }


    # Sélection AZ Turf Pro
    base = numeros[:7]


    return {
        "quinte": base[:5],

        "quarte": base[:4],

        "trio": base[:3],

        "champ_reduit": {
            "bases": base[:3],
            "complements": base[3:7]
        }
    }
