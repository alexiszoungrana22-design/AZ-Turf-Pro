from scoring import calculer_score_az
from ranking import classer_chevaux


def lancer_analyse():

    chevaux = [
        {
            "numero": 1,
            "forme": 8,
            "regularite": 7,
            "gains": 7,
            "jockey": 8,
            "cote": 7,
            "distance": 8,
            "terrain": 7,
            "experience": 8
        },
        {
            "numero": 2,
            "forme": 9,
            "regularite": 8,
            "gains": 8,
            "jockey": 7,
            "cote": 8,
            "distance": 9,
            "terrain": 8,
            "experience": 8
        },
        {
            "numero": 3,
            "forme": 10,
            "regularite": 9,
            "gains": 9,
            "jockey": 9,
            "cote": 9,
            "distance": 9,
            "terrain": 9,
            "experience": 10
        },
        {
            "numero": 4,
            "forme": 6,
            "regularite": 6,
            "gains": 6,
            "jockey": 7,
            "cote": 6,
            "distance": 7,
            "terrain": 6,
            "experience": 7
        },
        {
            "numero": 5,
            "forme": 9,
            "regularite": 8,
            "gains": 8,
            "jockey": 8,
            "cote": 9,
            "distance": 8,
            "terrain": 8,
            "experience": 9
        },
        {
            "numero": 6,
            "forme": 7,
            "regularite": 7,
            "gains": 7,
            "jockey": 8,
            "cote": 7,
            "distance": 7,
            "terrain": 8,
            "experience": 7
        },
        {
            "numero": 7,
            "forme": 8,
            "regularite": 8,
            "gains": 7,
            "jockey": 7,
            "cote": 8,
            "distance": 8,
            "terrain": 7,
            "experience": 8
        }
    ]


    for cheval in chevaux:
        cheval["score"] = calculer_score_az(cheval)


    classement = classer_chevaux(chevaux)


    ticket = []


    for rang, cheval in enumerate(classement[:7], start=1):

        score = cheval["score"]


        if rang == 1:
            type_cheval = "Favori AZ"

        elif rang <= 4:
            type_cheval = "Chance régulière"

        else:
            type_cheval = "Outsider"


        confiance = min(
            95,
            max(
                50,
                int((score / 250) * 100)
            )
        )


        ticket.append({
    "rang": rang,
    "numero": cheval["numero"],
    "indice_az": score,
    "confiance": confiance,
    "type": type_cheval
})

base = classement[0]["numero"]

associes = [
    cheval["numero"]
    for cheval in classement[1:4]
]

outsider = classement[4]["numero"]


return {
    "chevaux": ticket,
    "ticket_premium": {
        "base": base,
        "associes": associes,
        "outsider": outsider,
        "quinte": [
            cheval["numero"]
            for cheval in classement[:5]
        ]
    }
}
    return ticket
