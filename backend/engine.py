from scoring import calculer_score_az
from ranking import classer_chevaux
from quinte import generer_tickets_az
from learning import enregistrer_course


def lancer_analyse(chevaux):

    if not chevaux:
        return {
            "classement": [],
            "favori": {},
            "tickets": {}
        }

    # Calcul de l'indice AZ
    chevaux_scores = []

    for cheval in chevaux:
        score = calculer_score_az(cheval)

        chevaux_scores.append({
            "numero": cheval.get("numero"),
            "nom": cheval.get("nom", ""),
            "indice_az": score
        })

    # Classement AZ
    classement = classer_chevaux(chevaux_scores)

    # Génération des tickets
    tickets = generer_tickets_az(classement)

    # Enregistrement apprentissage
    enregistrer_course({
        "chevaux": chevaux,
        "classement": classement,
        "tickets": tickets
    })

    return {
        "message": "Analyse AZ Turf terminée",
        "classement": classement,
        "tickets": tickets
    }
