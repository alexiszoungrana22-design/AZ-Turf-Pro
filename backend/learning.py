import json
import os
from datetime import datetime


def enregistrer_course(data):

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

        "course": data.get("course", {}),

        "classement": data.get("classement", []),

        "tickets": data.get("tickets", {}),

        "arrivee": data.get("arrivee")

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

