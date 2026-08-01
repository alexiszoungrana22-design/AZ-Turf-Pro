# =====================================
# AZ TURF PRO
# DATABASE
# Gestion historique + Premium
# =====================================


# Historique des tickets
historique = []


# Abonnements Premium
abonnements = []



# =====================================
# HISTORIQUE
# =====================================

def enregistrer(ticket):

    historique.append(ticket)



def voir_historique():

    return historique





# =====================================
# PREMIUM
# =====================================

def creer_abonnement(data):

    abonnements.append(data)

    return data





def trouver_abonnement(telephone):

    for abonnement in abonnements:

        if abonnement.get("telephone") == telephone:

            return abonnement


    return None





def activer_abonnement(telephone, reference):

    abonnement = trouver_abonnement(telephone)


    if abonnement is None:

        return None



    abonnement["statut"] = "ACTIF"

    abonnement["reference_activation"] = reference


    return abonnement





def verifier_premium(telephone):

    abonnement = trouver_abonnement(telephone)


    if abonnement is None:

        return {
            "statut": "INACTIF"
        }



    return {
        "statut": abonnement.get(
            "statut",
            "INACTIF"
        ),

        "date_fin": abonnement.get(
            "date_fin",
            ""
        )
    }
