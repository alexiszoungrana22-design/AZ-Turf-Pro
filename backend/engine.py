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

    for cheval in classement[:5]:
        ticket.append(cheval["numero"])

    return ticket
