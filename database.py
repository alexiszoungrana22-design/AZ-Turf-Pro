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

    # Table des abonnements
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

    # Table de l'historique des courses
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historique_courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_course TEXT,
        course TEXT,
        favori TEXT,
        selection_az TEXT,
        arrivee TEXT
    )
    """)

    conn.commit()
    conn.close()


initialiser_database()


# =====================================
# HISTORIQUE TICKETS (PERSISTANT SQLITE)
# =====================================

def enregistrer(ticket):
    conn = connexion()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO historique_courses (date_course, course, favori, selection_az, arrivee)
        VALUES (?, ?, ?, ?, ?)
    """, (
        ticket.get("date", datetime.now().strftime("%Y-%m-%d")),
        ticket.get("course", ""),
        ticket.get("favori", ""),
        ticket.get("selection_az", ""),
        ticket.get("arrivee", "")
    ))

    conn.commit()
    conn.close()


def voir_historique():
    conn = connexion()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date_course, course, favori, selection_az, arrivee 
        FROM historique_courses 
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    liste_historique = []
    for row in rows:
        liste_historique.append({
            "date": row[0],
            "course": row[1],
            "favori": row[2],
            "selection_az": row[3],
            "arrivee": row[4]
        })

    return liste_historique


# =====================================
# CREER OU METTRE A JOUR ABONNEMENT
# =====================================

def creer_abonnement(data):
    conn = connexion()
    cursor = conn.cursor()

    ancien = trouver_abonnement(data.get("telephone"))

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
# PRE-VALIDER UNE REFERENCE DE PAIEMENT
# =====================================

def valider_reference_paiement(telephone, reference):
    telephone = (telephone or "").strip()
    reference = (reference or "").strip()

    if not telephone or not reference:
        return None

    abonnement = trouver_abonnement(telephone)
    if abonnement is None:
        return None

    conn = connexion()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE abonnements
        SET reference=?, statut=?
        WHERE telephone=?
        """,
        (reference, "REFERENCE_VALIDEE", telephone)
    )
    conn.commit()
    conn.close()

    abonnement["reference"] = reference
    abonnement["statut"] = "REFERENCE_VALIDEE"
    return abonnement


# =====================================
# ACTIVER PREMIUM
# =====================================

def activer_abonnement(telephone, reference):
    abonnement = trouver_abonnement(telephone)

    if abonnement is None:
        return None

    # Une activation publique n'est possible que si la référence a
    # auparavant été validée côté serveur par l'administrateur.
    if abonnement.get("statut") != "REFERENCE_VALIDEE":
        return None

    if not reference or reference.strip() != (abonnement.get("reference") or "").strip():
        return None

    duree = int(abonnement.get("duree", 30))
    date_fin = (datetime.now() + timedelta(days=duree)).isoformat()

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
    abonnement = trouver_abonnement(telephone)

    if abonnement is None:
        return {"statut": "INACTIF"}

    statut = abonnement.get("statut", "INACTIF")
    date_fin = abonnement.get("date_fin", "")

    if statut == "ACTIF" and date_fin:
        try:
            expiration = datetime.fromisoformat(date_fin)
            if datetime.now() > expiration:
                conn = connexion()
                cursor = conn.cursor()

                cursor.execute(
                    """
                    UPDATE abonnements
                    SET statut=?
                    WHERE telephone=?
                    """,
                    ("EXPIRE", telephone)
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

    cursor.execute("SELECT COUNT(*) FROM abonnements")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM abonnements WHERE statut='ACTIF'")
    actifs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM abonnements WHERE statut='EN_ATTENTE'")
    attente = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM abonnements WHERE statut='EXPIRE'")
    expires = cursor.fetchone()[0]

    conn.close()

    return {
        "total": total,
        "actifs": actifs,
        "en_attente": attente,
        "expires": expires
    }
