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


# =====================================
# LECTURE DE L'HISTORIQUE
# (additif - n'affecte pas enregistrer_course)
# =====================================

def lire_historique():
    """
    Lit l'integralite de l'historique sauvegarde. Retourne une
    liste vide si le fichier n'existe pas encore ou est illisible.
    """

    fichier = os.path.join("data", "historique_az.json")

    if not os.path.exists(fichier):
        return []

    try:
        with open(fichier, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def mettre_a_jour_arrivee(index_entree, arrivee):
    """
    Met a jour le champ 'arrivee' d'une entree existante de
    l'historique, identifiee par son index dans la liste.
    """

    fichier = os.path.join("data", "historique_az.json")

    historique = lire_historique()

    if index_entree < 0 or index_entree >= len(historique):
        return False

    historique[index_entree]["arrivee"] = arrivee

    with open(fichier, "w", encoding="utf-8") as f:
        json.dump(historique, f, indent=4, ensure_ascii=False)

    return True
    
