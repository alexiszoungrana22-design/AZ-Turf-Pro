from scoring import calculer_score_az
from ranking import classer_chevaux


def lancer_analyse():

    chevaux = [
        {
            "numero": 1,
            "forme": 8,
            "regularite": 7,
            "gains": 6,
            "jockey": 8,
            "cote": 7
        },
        {
            "numero": 2,
            "forme": 9,
            "regularite": 8,
            "gains": 7,
            "jockey": 7,
            "cote": 8
        },
        {
            "numero": 3,
            "forme": 10,
            "regularite": 9,
            "gains": 8,
            "jockey": 9,
            "cote": 9
        },
        {
            "numero": 4,
            "forme": 6,
            "regularite": 6,
            "gains": 5,
            "jockey": 7,
            "cote": 6
        },
        {
            "numero": 5,
            "forme": 9,
            "regularite": 8,
            "gains": 8,
            "jockey": 8,
            "cote": 9
        }
    ]

    for cheval in chevaux:
        cheval["score"] = calculer_score_az(cheval)

    classement = classer_chevaux(chevaux)

    ticket = []

    for rang, cheval in enumerate(classement[:5], start=1):

        score = cheval["score"]

        if score >= 155:
            type_cheval = "Favori AZ"
        elif score >= 130:
            type_cheval = "Chance régulière"
        else:
            type_cheval = "Outsider"

        confiance = min(95, score // 2)

        ticket.append({
            "rang": rang,
            "numero": cheval["numero"],
            "indice_az": score,
            "confiance": confiance,
            "type": type_cheval
        })

    return ticket
