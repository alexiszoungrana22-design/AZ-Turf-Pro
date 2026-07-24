from scoring import calculer_score_az
from ranking import classer_chevaux
from quinte import generer_tickets_az


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


    if not classement:
        return {
            "classement": [],
            "favori": {},
            "tickets": {}
        }


    resultat = []


    for rang, cheval in enumerate(classement, start=1):

        score = cheval.get("score", 0)

        if rang == 1:
            categorie = "Favori AZ"
        elif rang <= 4:
            categorie = "Chance régulière"
        else:
            categorie = "Outsider"


        confiance = min(
            95,
            max(
                50,
                int(score * 0.4)
            )
        )


        resultat.append({
            "rang": rang,
            "numero": cheval["numero"],
            "indice_az": score,
            "confiance": confiance,
            "type": categorie
        })


    try:
        tickets = generer_tickets_az(resultat)
    except Exception:
        tickets = {}


    return {
        "classement": resultat,
        "favori": resultat[0],
        "tickets": tickets
    }
