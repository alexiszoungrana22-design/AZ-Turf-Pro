import json
import os
from datetime import datetime, timedelta


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

        "arrivee": data.get("arrivee"),
        "heure_arrivee": data.get("heure_arrivee"),
        "publication_at": data.get("publication_at"),
        "publication_statut": "EN ATTENTE"

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
    Enregistre l'arrivee officielle detectee et programme la publication
    de l'actualite AZ Turf Pro deux heures plus tard.
    """
    fichier = os.path.join("data", "historique_az.json")
    historique = lire_historique()

    if index_entree < 0 or index_entree >= len(historique):
        return False

    maintenant = datetime.now()
    entree = historique[index_entree]
    entree["arrivee"] = arrivee
    entree["heure_arrivee"] = maintenant.isoformat(timespec="seconds")
    entree["publication_at"] = (
        maintenant + timedelta(hours=2)
    ).isoformat(timespec="seconds")
    entree["publication_statut"] = "PROGRAMMEE"

    with open(fichier, "w", encoding="utf-8") as f:
        json.dump(historique, f, indent=4, ensure_ascii=False)

    return True


def mettre_a_jour_publications():
    """
    Passe les actualites dont le delai de deux heures est ecoule a PUBLIE.
    Retourne True si au moins une entree a ete modifiee.
    """
    fichier = os.path.join("data", "historique_az.json")
    historique = lire_historique()
    maintenant = datetime.now()
    modifie = False

    for entree in historique:
        if not entree.get("arrivee"):
            continue

        publication_at = entree.get("publication_at")
        if not publication_at:
            # Compatibilite avec les anciennes courses deja arrivees.
            heure_arrivee = entree.get("heure_arrivee")
            if heure_arrivee:
                try:
                    dt = datetime.fromisoformat(str(heure_arrivee))
                    publication_at = (dt + timedelta(hours=2)).isoformat(timespec="seconds")
                    entree["publication_at"] = publication_at
                except Exception:
                    continue
            else:
                continue

        try:
            date_publication = datetime.fromisoformat(str(publication_at))
        except Exception:
            continue

        if maintenant >= date_publication and entree.get("publication_statut") != "PUBLIE":
            entree["publication_statut"] = "PUBLIE"
            entree["date_publication"] = maintenant.isoformat(timespec="seconds")
            modifie = True

    if modifie:
        with open(fichier, "w", encoding="utf-8") as f:
            json.dump(historique, f, indent=4, ensure_ascii=False)

    return modifie

