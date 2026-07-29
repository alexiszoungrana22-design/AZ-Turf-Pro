from scoring import calculer_score_az
from ranking import classer_chevaux
from quinte import generer_tickets_az

try:
    from database import enregistrer_course
except Exception:
    def enregistrer_course(data):
        pass


def lancer_analyse(chevaux):

    print("NOMBRE CHEVAUX RECUS :", len(chevaux))


    chevaux_scores = []


    for cheval in chevaux:

        score = calculer_score_az(cheval)

        chevaux_scores.append({

            "numero": cheval.get("numero"),

            "nom": cheval.get("nom", ""),

            "indice_az": score

        })


    print("CHEVAUX SCORES :", chevaux_scores)


    classement = classer_chevaux(
        chevaux_scores
    )


    print("CLASSEMENT :", classement)


    tickets = generer_tickets_az(
        classement
    )


    print("TICKETS :", tickets)


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
    "favori": classement[0] if classement else {},
    "tickets": tickets
    }
