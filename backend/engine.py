from scoring import calculer_score_az
from ranking import classer_chevaux
from quinte import generer_tickets_az


def lancer_analyse(chevaux):

    print("CHEVAUX RECUS :", len(chevaux))

    chevaux_scores = []

    for cheval in chevaux:

        score = calculer_score_az(cheval)

        chevaux_scores.append({
            "numero": cheval.get("numero"),
            "nom": cheval.get("nom"),
            "indice_az": score
        })


    print("SCORES :", chevaux_scores)


    classement = classer_chevaux(chevaux_scores)


    print("CLASSEMENT :", classement)


    tickets = generer_tickets_az(classement)


    return {
        "message": "Analyse AZ Turf terminée",
        "chevaux": classement,
        "classement": classement,
        "favori": classement[0] if classement else {},
        "tickets": tickets
    }
