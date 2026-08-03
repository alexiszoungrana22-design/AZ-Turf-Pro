# =====================================
# AZ TURF PRO
# DATABASE
# Gestion historique + Premium SQLite
# =====================================

import sqlite3
from datetime import datetime, timedelta


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

        date_creation TEXT,

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
# CREER OU METTRE A JOUR ABONNEMENT
# =====================================

def creer_abonnement(data):

    conn = connexion()

    cursor = conn.cursor()


    ancien = trouver_abonnement(
        data.get("telephone")
    )


    if ancien:


        cursor.execute(
            """
            UPDATE abonnements

            SET offre=?,
                prix=?,
                duree=?,
                paiement=?,
                statut=?


            WHERE telephone=?

            """,

            (

                data.get("offre"),

                data.get("prix"),

                data.get("duree"),

                data.get("paiement"),

                "EN_ATTENTE",

                data.get("telephone")

            )

        )


    else:


        cursor.execute(
            """
            INSERT INTO abonnements

            (

            telephone,
            offre,
            prix,
            duree,
            paiement,
            reference,
            statut,
            date_creation,
            date_fin

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

            """,

            (

            data.get("telephone"),

            data.get("offre"),

            data.get("prix"),

            data.get("duree"),

            data.get("paiement"),

            "",

            "EN_ATTENTE",

            datetime.now().isoformat(),

            ""

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
        WHERE telephone=?

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

        "date_creation": resultat[8],

        "date_fin": resultat[9]

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



    duree = int(
        abonnement.get(
            "duree",
            30
        )
    )


    date_fin = (

        datetime.now()

        +

        timedelta(
            days=duree
        )

    ).isoformat()



    conn = connexion()

    cursor = conn.cursor()



    cursor.execute(
        """

        UPDATE abonnements

        SET statut=?,

            reference=?,

            date_fin=?


        WHERE telephone=?


        """,

        (

        "ACTIF",

        reference,

        date_fin,

        telephone

        )

    )



    conn.commit()

    conn.close()



    abonnement["statut"] = "ACTIF"

    abonnement["reference"] = reference

    abonnement["date_fin"] = date_fin



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

            "statut":"INACTIF"

        }



    statut = abonnement.get(
        "statut",
        "INACTIF"
    )



    date_fin = abonnement.get(
        "date_fin",
        ""
    )



    if statut == "ACTIF" and date_fin:


        try:


            expiration = datetime.fromisoformat(
                date_fin
            )


            if datetime.now() > expiration:


                conn = connexion()

                cursor = conn.cursor()


                cursor.execute(
                    """

                    UPDATE abonnements

                    SET statut=?

                    WHERE telephone=?

                    """,

                    (

                    "EXPIRE",

                    telephone

                    )

                )


                conn.commit()

                conn.close()


                statut = "EXPIRE"



        except Exception:


            pass




    return {


        "statut": statut,


        "date_fin": date_fin

    }




# =====================================
# ADMIN - LISTE DES ABONNEMENTS
# =====================================

def lister_abonnements():

    conn = connexion()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT *
        FROM abonnements
        ORDER BY id DESC
        """
    )


    resultats = cursor.fetchall()


    conn.close()


    abonnements = []


    for resultat in resultats:


        abonnements.append({

            "id": resultat[0],

            "telephone": resultat[1],

            "offre": resultat[2],

            "prix": resultat[3],

            "duree": resultat[4],

            "paiement": resultat[5],

            "reference": resultat[6],

            "statut": resultat[7],

            "date_creation": resultat[8],

            "date_fin": resultat[9]

        })


    return abonnements
# =====================================
# ADMIN - STATISTIQUES ABONNEMENTS
# =====================================

def statistiques_abonnements():

    conn = connexion()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT COUNT(*)
        FROM abonnements
        """
    )

    total = cursor.fetchone()[0]


    cursor.execute(
        """
        SELECT COUNT(*)
        FROM abonnements
        WHERE statut='ACTIF'
        """
    )

    actifs = cursor.fetchone()[0]


    cursor.execute(
        """
        SELECT COUNT(*)
        FROM abonnements
        WHERE statut='EN_ATTENTE'
        """
    )

    attente = cursor.fetchone()[0]


    cursor.execute(
        """
        SELECT COUNT(*)
        FROM abonnements
        WHERE statut='EXPIRE'
        """
    )

    expires = cursor.fetchone()[0]


    conn.close()


    return {

        "total": total,

        "actifs": actifs,

        "en_attente": attente,

        "expires": expires

    }
