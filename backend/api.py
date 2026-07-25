from scoring import calculer_score_az
from ranking import classer_chevaux
from quinte import generer_tickets_az

try:
    from learning import enregistrer_course
except Exception:
    enregistrer_course = None


def lancer_analyse(chevaux):

    if not chevaux:
        return {
            "message": "Aucun cheval trouvé",
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
            "nom": cheval.get("nom", ""),
            "indice_az": score,
            "forme": cheval.get("forme", 0),
            "regularite": cheval.get("regularite", 0),
            "cote": cheval.get("cote", 0)
        })


    classement = classer_chevaux(chevaux_scores)


    favori = classement[0] if classement else {}


    tickets = generer_tickets_az(classement)


    if enregistrer_course:

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
        "favori": favori,
        "tickets": tickets
    }
