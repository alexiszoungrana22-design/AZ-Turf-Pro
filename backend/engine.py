from scoring import calculer_score_az
from ranking import classer_chevaux
from quinte import generer_tickets_az


def lancer_analyse(chevaux):

    if not chevaux:

        return {
            "classement": [],
            "favori": {},
            "tickets": {}
        }


    # Calcul de l'indice AZ

    for cheval in chevaux:

        cheval["score"] = calculer_score_az(cheval)



    # Classement

    classement = classer_chevaux(chevaux)



    resultat = []



    for rang, cheval in enumerate(classement, start=1):

        score = cheval.get(
            "score",
            0
        )


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

            "numero": cheval.get(
                "numero"
            ),

            "nom": cheval.get(
                "nom",
                ""
            ),

            "indice_az": score,

            "confiance": confiance,

            "type": categorie

        })



    tickets = generer_tickets_az(
        resultat
    )



    return {

        "classement": resultat,

        "favori": resultat[0] if resultat else {},

        "tickets": tickets

    }
