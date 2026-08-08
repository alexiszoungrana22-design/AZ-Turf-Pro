```python
# =====================================
# AZ TURF PRO
# DATABASE
# Abonnements Premium + Historique
# =====================================

from datetime import datetime, timedelta


# =====================================
# HISTORIQUE DES TICKETS
# =====================================

historique = []


def enregistrer(ticket):
    historique.append(ticket)


def voir_historique():
    return historique


# =====================================
# ABONNEMENTS PREMIUM
# =====================================

abonnements = []


# =====================================
# CREATION ABONNEMENT
# =====================================

def creer_abonnement(data):

    telephone = str(
        data.get("telephone", "")
    ).strip()

    if not telephone:
        raise ValueError(
            "Numéro de téléphone obligatoire"
        )

    abonnement = {
        "telephone": telephone,
        "nom": data.get("nom", ""),
        "reference": data.get(
            "reference",
            ""
        ),
        "duree": int(
            data.get(
                "duree",
                30
            )
        ),
        "statut": "EN_ATTENTE",
        "date_creation":
            datetime.now().isoformat(),
        "date_activation": None,
        "date_fin": None
    }

    # Évite les doublons actifs/en attente
    for ancien in abonnements:

        if (
            ancien.get("telephone")
            == telephone
            and ancien.get("statut")
            in ["EN_ATTENTE", "ACTIF"]
        ):
            return ancien

    abonnements.append(abonnement)

    return abonnement


# =====================================
# ACTIVATION PREMIUM
# =====================================

def activer_abonnement(
    telephone,
    reference
):

    telephone = str(
        telephone
    ).strip()

    reference = str(
        reference
    ).strip()

    for abonnement in abonnements:

        if (
            abonnement.get("telephone")
            == telephone
            and (
                not reference
                or abonnement.get(
                    "reference",
                    ""
                )
                == reference
            )
        ):

            duree = int(
                abonnement.get(
                    "duree",
                    30
                )
            )

            maintenant = datetime.now()

            date_fin = (
                maintenant
                + timedelta(
                    days=duree
                )
            )

            abonnement[
                "statut"
            ] = "ACTIF"

            abonnement[
                "date_activation"
            ] = maintenant.isoformat()

            abonnement[
                "date_fin"
            ] = date_fin.isoformat()

            return abonnement

    return None


# =====================================
# VERIFICATION PREMIUM
# =====================================

def verifier_premium(
    telephone
):

    telephone = str(
        telephone
    ).strip()

    for abonnement in abonnements:

        if (
            abonnement.get(
                "telephone"
            )
            == telephone
        ):

            statut = abonnement.get(
                "statut",
                "INACTIF"
            )

            date_fin = abonnement.get(
                "date_fin"
            )

            # Vérification automatique
            # de l'expiration
            if (
                statut == "ACTIF"
                and date_fin
            ):

                try:

                    expiration = (
                        datetime.fromisoformat(
                            date_fin
                        )
                    )

                    if datetime.now() >= expiration:

                        abonnement[
                            "statut"
                        ] = "EXPIRE"

                        statut = "EXPIRE"

                except ValueError:
                    pass

            return {
                "telephone": telephone,
                "statut": statut,
                "date_fin": abonnement.get(
                    "date_fin"
                )
            }

    return {
        "telephone": telephone,
        "statut": "INACTIF",
        "date_fin": None
    }


# =====================================
# LISTE DES ABONNEMENTS
# =====================================

def lister_abonnements():

    return abonnements


# =====================================
# STATISTIQUES ABONNEMENTS
# =====================================

def statistiques_abonnements():

    total = len(abonnements)

    actifs = 0
    en_attente = 0
    expires = 0

    for abonnement in abonnements:

        statut = abonnement.get(
            "statut",
            "INACTIF"
        )

        if statut == "ACTIF":
            actifs += 1

        elif statut == "EN_ATTENTE":
            en_attente += 1

        elif statut == "EXPIRE":
            expires += 1

    return {
        "total": total,
        "actifs": actifs,
        "en_attente": en_attente,
        "expires": expires
    }
```
            
