# =====================================
# AZ TURF PRO
# DATABASE
# Gestion historique + Premium SQLite
# =====================================

import sqlite3
from datetime import datetime


DB_NAME = "az_turf.db"



# =====================================
# CONNEXION DATABASE
# =====================================

def connexion():

    return sqlite3.connect(DB_NAME)





# =====================================
# CREATION TABLES
# =====================================

def initialiser_database():

    conn = connexion()

    cursor = conn.cursor()


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS abonnements (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        telephone TEXT UNIQUE,

        offre TEXT,

        prix INTEGER,

        duree INTEGER,

        paiement TEXT,

        reference TEXT,

        statut TEXT,

        date_fin TEXT

    )
    """)



    conn.commit()

    conn.close()





initialiser_database()





# =====================================
# HISTORIQUE TICKETS
# =====================================

historique = []



def enregistrer(ticket):

    historique.append(ticket)



def voir_historique():

    return historique





# =====================================
# CREER ABONNEMENT
# =====================================

def creer_abonnement(data):

    conn = connexion()

    cursor = conn.cursor()



    cursor.execute(
        """
        INSERT OR REPLACE INTO abonnements
        (
            telephone,
            offre,
            prix,
            duree,
            paiement,
            reference,
            statut
        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,

        (
            data.get("telephone"),
            data.get("offre"),
            data.get("prix"),
            data.get("duree"),
            data.get("paiement"),
            data.get("reference"),
            "EN_ATTENTE"
        )

    )


    conn.commit()

    conn.close()


    return data





# =====================================
# TROUVER ABONNEMENT
# =====================================

def trouver_abonnement(telephone):

    conn = connexion()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT *
        FROM abonnements
        WHERE telephone = ?
        """,
        (telephone,)
    )


    resultat = cursor.fetchone()


    conn.close()



    if resultat is None:

        return None



    return {

        "id": resultat[0],

        "telephone": resultat[1],

        "offre": resultat[2],

        "prix": resultat[3],

        "duree": resultat[4],

        "paiement": resultat[5],

        "reference": resultat[6],

        "statut": resultat[7],

        "date_fin": resultat[8]

    }





# =====================================
# ACTIVER PREMIUM
# =====================================

def activer_abonnement(
    telephone,
    reference
):

    abonnement = trouver_abonnement(
        telephone
    )



    if abonnement is None:

        return None



    conn = connexion()

    cursor = conn.cursor()



    cursor.execute(
        """
        UPDATE abonnements

        SET statut = ?,
            reference = ?

        WHERE telephone = ?

        """,

        (
            "ACTIF",
            reference,
            telephone
        )

    )


    conn.commit()

    conn.close()



    abonnement["statut"] = "ACTIF"

    abonnement["reference"] = reference


    return abonnement





# =====================================
# VERIFIER PREMIUM
# =====================================

def verifier_premium(telephone):

    abonnement = trouver_abonnement(
        telephone
    )



    if abonnement is None:

        return {

            "statut": "INACTIF"

        }



    return {

        "statut":
        abonnement.get(
            "statut",
            "INACTIF"
        ),

        "date_fin":
        abonnement.get(
            "date_fin",
            ""
        )

    }
