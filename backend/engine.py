from ranking import classer_chevaux


def lancer_analyse():

    chevaux = [
        {"numero": 1, "score": 72},
        {"numero": 2, "score": 85},
        {"numero": 3, "score": 90},
        {"numero": 4, "score": 65},
        {"numero": 5, "score": 88},
        {"numero": 6, "score": 70},
        {"numero": 7, "score": 82}
    ]

    classement = classer_chevaux(chevaux)

    ticket = []

    for cheval in classement[:5]:
        ticket.append(cheval["numero"])

    return ticket
