from scoring import calculer_score_az
from ranking import classer_chevaux
from quinte import generer_tickets_az


def lancer_analyse(chevaux):

    if not chevaux:
        return {
            "message": "Aucun cheval",
            "chevaux": [],
            "classement": [],
            "favori": {},
            "tickets": {}
        }


    chevaux_scores = []


    for cheval in chevaux:

        score = calculer_score_az(cheval)

        chevaux_scores.append({

            "numero": cheval.get("numero"),

            "nom": cheval.get(
                "nom",
                ""
            ),

            "indice_az": score

        })


    classement = classer_chevaux(
        chevaux_scores
    )


    tickets = generer_tickets_az(
        classement
    )


    return {

        "message": "Analyse AZ Turf terminée",

        # classement complet
        "chevaux": classement,

        "classement": classement,

        "favori": (
            classement[0]
            if classement
            else {}
        ),

        "tickets": tickets

    }
