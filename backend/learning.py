import json
import os
from datetime import datetime


def enregistrer_course(classement, arrivee):

    dossier = "data"

    os.makedirs(
        dossier,
        exist_ok=True
    )


    fichier = os.path.join(
        dossier,
        "historique_az.json"
    )


    nouvelle_course = {

        "date_analyse": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "classement": classement,

        "arrivee": arrivee

    }


    historique = []


    if os.path.exists(fichier):

        try:

            with open(
                fichier,
                "r",
                encoding="utf-8"
            ) as f:

                historique = json.load(f)

        except:

            historique = []


    historique.append(
        nouvelle_course
    )


    with open(
        fichier,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            historique,
            f,
            indent=4,
            ensure_ascii=False
        )

