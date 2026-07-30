from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from engine import lancer_analyse
import json
import os
from datetime import datetime, timedelta


router = APIRouter(
    prefix="/api",
    tags=["AZ Turf"]
)


# ==============================
# GESTION ABONNEMENTS PREMIUM
# ==============================

ABONNEMENTS_FILE = os.path.join(
    "data",
    "abonnements.json"
)


def charger_abonnements():

    if not os.path.exists(ABONNEMENTS_FILE):

        return []

    with open(
        ABONNEMENTS_FILE,
        "r",
        encoding="utf-8"
    ) as fichier:

        return json.load(fichier)



def sauvegarder_abonnements(abonnements):

    with open(
        ABONNEMENTS_FILE,
        "w",
        encoding="utf-8"
    ) as fichier:

        json.dump(
            abonnements,
            fichier,
            indent=4,
            ensure_ascii=False
        )



# ==============================
# MODELES PREMIUM
# ==============================

class AbonnementRequest(BaseModel):

    offre: str
    prix: int
    duree: int
    paiement: str
    telephone: str



class ActivationRequest(BaseModel):

    telephone: str
    reference: str




# ==============================
# ANALYSE COURSE EXISTANTE
# ==============================

@router.get("/analyse")
def analyse():

    try:

        chemin = os.path.join(
            "data",
            "courses.json"
        )


        with open(
            chemin,
            "r",
            encoding="utf-8"
        ) as fichier:

            course = json.load(fichier)



        chevaux = course.get(
            "chevaux",
            []
        )


        if not chevaux:

            raise Exception(
                "Aucun cheval trouvé dans courses.json"
            )



        resultat = lancer_analyse(
            chevaux
        )


        classement = resultat.get(
            "chevaux",
            []
        )



        return {

            "message": "Analyse AZ Turf terminée",

            "course": course.get(
                "course",
                "Course"
            ),

            "date": course.get(
                "date",
                ""
            ),

            "reunion": course.get(
                "reunion",
                ""
            ),

            "course_numero": course.get(
                "course_numero",
                ""
            ),

            "hippodrome": course.get(
                "hippodrome",
                ""
            ),

            "discipline": course.get(
                "discipline",
                ""
            ),

            "distance_course": course.get(
                "distance_course",
                0
            ),

            "allocation": course.get(
                "allocation",
                0
            ),

            "partants": len(chevaux),

            "chevaux": classement,

            "classement": classement,

            "favori": (
                classement[0]
                if classement
                else {}
            ),

            "tickets": resultat.get(
                "tickets",
                {}
            )

        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Erreur AZ : {str(e)}"
        )




# ==============================
# CREATION ABONNEMENT
# ==============================

@router.post("/abonnement")
def creer_abonnement(
    data: AbonnementRequest
):

    abonnements = charger_abonnements()


    abonnement = {

        "telephone": data.telephone,

        "offre": data.offre,

        "prix": data.prix,

        "duree": data.duree,

        "paiement": data.paiement,

        "statut": "EN_ATTENTE",

        "date_creation": datetime.now().isoformat()

    }


    abonnements.append(
        abonnement
    )


    sauvegarder_abonnements(
        abonnements
    )


    return {

        "message": "Demande Premium enregistrée",

        "statut": "EN_ATTENTE"

    }





# ==============================
# ACTIVATION PREMIUM
# ==============================

@router.post("/activation")
def activation_premium(
    data: ActivationRequest
):

    abonnements = charger_abonnements()



    for abonnement in abonnements:


        if abonnement["telephone"] == data.telephone:


            abonnement["statut"] = "ACTIF"


            abonnement["reference"] = data.reference


            debut = datetime.now()


            fin = debut + timedelta(
                days=abonnement["duree"]
            )


            abonnement["date_debut"] = debut.isoformat()

            abonnement["date_fin"] = fin.isoformat()



            sauvegarder_abonnements(
                abonnements
            )


            return {

                "message": "Premium activé",

                "statut": "ACTIF",

                "date_fin": abonnement["date_fin"]

            }



    raise HTTPException(
        status_code=404,
        detail="Aucun abonnement trouvé"
    )





# ==============================
# VERIFICATION ACCES PREMIUM
# ==============================

@router.get("/premium/{telephone}")
def verifier_premium(
    telephone: str
):

    abonnements = charger_abonnements()



    for abonnement in abonnements:


        if abonnement["telephone"] == telephone:

            return abonnement



    return {

        "statut": "INACTIF"

        }
