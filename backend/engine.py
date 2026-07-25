from scoring import calculer_score_az
from ranking import classer_chevaux
from quinte import generer_tickets_az
from engine import lancer_analyse
>>>>>>> 5ad12a3 (Correction imports backend pour Render)



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



    # Classement des chevaux

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

            "numero": cheval.get("numero"),

            "nom": cheval.get("nom", ""),

            "age": cheval.get("age", 0),

            "sexe": cheval.get("sexe", ""),

            "jockey": cheval.get("jockey", ""),

            "entraineur": cheval.get("entraineur", ""),

            "performances": cheval.get(
                "performances",
                []
            ),

            "indice_az": score,

            "confiance": confiance,

            "type": categorie

        })




    # Génération des tickets AZ

    tickets = generer_tickets_az(
        resultat
    )



    # Enregistrement pour apprentissage futur

    enregistrer_course(
        resultat,
        []
    )



    return {

        "classement": resultat,

        "favori": resultat[0] if resultat else {},

        "tickets": tickets

    }
