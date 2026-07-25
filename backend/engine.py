from scoring import calculer_score_az
from ranking import classer_chevaux
from quinte import generer_tickets_az
from learning import enregistrer_course


def lancer_analyse(chevaux):

    if not chevaux:
        return {
            "message": "Aucun cheval",
            "chevaux": [],
            "classement": [],
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


    try:

        enregistrer_course({

            "chevaux": chevaux,

            "classement": classement,

            "tickets": tickets

        })

    except Exception:

        pass



    return {

        "message": "Analyse AZ Turf terminée",

        "chevaux": classement,

        "classement": classement,

        "favori": (
            classement[0]
            if classement
            else {}
        ),

        "tickets": tickets

    }
