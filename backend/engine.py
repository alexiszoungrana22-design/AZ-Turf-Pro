"""
=========================================================
AZ TURF PRO - MOTEUR D'ANALYSE
=========================================================

Structure conservée :
    scoring.py
    ranking.py
    quinte.py
    learning.py

Fonctions principales :
    - calcul de l'Indice AZ
    - calcul de l'Indice Premium
    - détection des non-partants
    - conservation des non-partants pour affichage
    - exclusion stricte des non-partants des tickets
    - classement des partants
    - génération des tickets gratuits et Premium
    - enregistrement de la course dans l'historique
=========================================================
"""

from scoring import calculer_score_az
from ranking import classer_chevaux
from quinte import generer_tickets_az
from learning import enregistrer_course


# =========================================================
# OUTILS NUMERIQUES
# =========================================================

def _float(value, default=0.0):
    """
    Conversion sécurisée vers float.
    """
    try:
        if value is None or value == "":
            return float(default)

        return float(value)

    except (TypeError, ValueError):
        return float(default)


def _numero_str(numero):
    """
    Normalise un numéro de cheval en chaîne.
    """
    if numero is None:
        return ""

    return str(numero).strip()


# =========================================================
# INDICE PREMIUM
# =========================================================

def calculer_indice_premium(cheval, discipline="TROT"):
    """
    Calcule l'Indice Premium AZ Pro.

    Critères repris du moteur Premium précédent :

        - Indice AZ
        - Forme
        - Régularité
        - Cote
        - Expérience
        - Bonnes places dans les performances
        - Bonus outsider chaud

    Le calcul Premium est volontairement différent
    du simple classement AZ afin que les tickets Premium
    puissent être distincts des tickets gratuits.
    """

    indice_az = _float(
        cheval.get("indice_az", 0),
        0
    )

    forme = _float(
        cheval.get("forme", 5),
        5
    )

    regularite = _float(
        cheval.get("regularite", 5),
        5
    )

    cote = _float(
        cheval.get("cote", 5),
        5
    )

    experience = _float(
        cheval.get("experience", 5),
        5
    )

    # -----------------------------------------------------
    # Performances récentes
    # -----------------------------------------------------

    performances = cheval.get("performances") or []

    bonnes_places = 0

    if isinstance(performances, (list, tuple)):

        for performance in performances:

            # Cas classique : performance numérique
            if isinstance(
                performance,
                (int, float)
            ):

                if performance <= 3:
                    bonnes_places += 1

                continue

            # Cas où la performance arrive sous forme de texte
            if isinstance(
                performance,
                str
            ):

                texte = performance.strip()

                try:

                    valeur = float(texte)

                    if valeur <= 3:
                        bonnes_places += 1

                except (TypeError, ValueError):

                    # On ignore les valeurs non numériques
                    pass

    # -----------------------------------------------------
    # Bonus outsider chaud
    # -----------------------------------------------------

    bonus_outsider_chaud = 0.0

    if (
        cote >= 10.0
        and (
            forme >= 7.0
            or regularite >= 7.0
        )
    ):

        bonus_outsider_chaud = 15.0

    # -----------------------------------------------------
    # Calcul Premium
    # -----------------------------------------------------

    indice_premium = (
        indice_az
        + (forme * 1.35)
        + (regularite * 1.20)
        + (cote * 1.10)
        + (experience * 0.80)
        + (bonnes_places * 2.0)
        + bonus_outsider_chaud
    )

    return round(
        indice_premium,
        2
    )


# =========================================================
# LANCEMENT DE L'ANALYSE
# =========================================================

def lancer_analyse(
    chevaux,
    info_course=None
):
    """
    Orchestre l'analyse complète d'une course.

    IMPORTANT :

    Les non-partants restent présents dans la réponse
    pour permettre au frontend de les afficher en rouge.

    En revanche, ils sont totalement exclus :
        - du classement utile ;
        - des tickets gratuits ;
        - des tickets Premium ;
        - du champ réduit ;
        - de la dernière minute.
    """

    # =====================================================
    # AUCUN CHEVAL
    # =====================================================

    if not chevaux:

        return {
            "message": "Aucun cheval analysé",
            "chevaux": [],
            "classement": [],
            "partants_complets": [],
            "non_partants": [],
            "favori": {},
            "tickets": {},
        }


    # =====================================================
    # INFORMATIONS COURSE
    # =====================================================

    if not isinstance(
        info_course,
        dict
    ):

        info_course = {}


    discipline = (
        info_course.get(
            "discipline",
            "TROT"
        )
        or "TROT"
    )


    # =====================================================
    # RECUPERATION DES NON-PARTANTS OFFICIELS
    # =====================================================

    non_partants_bruts = (
        info_course.get(
            "non_partants",
            []
        )
        or []
    )


    np_nums = set()


    for np in non_partants_bruts:

        if isinstance(
            np,
            dict
        ):

            numero = np.get(
                "numero"
            )

            if numero is not None:

                np_nums.add(
                    _numero_str(numero)
                )

        elif np is not None:

            np_nums.add(
                _numero_str(np)
            )


    # =====================================================
    # SEPARATION PARTANTS / NON-PARTANTS
    # =====================================================

    chevaux_complets = []

    chevaux_valides = []


    for cheval in chevaux:

        if not isinstance(
            cheval,
            dict
        ):
            continue


        copie = dict(cheval)

        numero = (
            copie.get("numero")
        )

        numero_str = _numero_str(
            numero
        )


        # -------------------------------------------------
        # Détection non-partant
        # -------------------------------------------------

        statut_original = str(
            copie.get(
                "statut",
                ""
            )
            or ""
        ).strip().upper()


        est_np = (
            numero_str in np_nums
            or statut_original in (
                "NON_PARTANT",
                "NON-PARTANT",
                "NP"
            )
            or copie.get(
                "est_non_partant",
                False
            ) is True
        )


        if est_np:

            # Conservation pour affichage
            copie["est_non_partant"] = True
            copie["statut"] = "NON_PARTANT"
            copie["rang"] = "NP"

            # Score volontairement très faible
            copie["score_az"] = -999.0
            copie["indice_az"] = -999.0
            copie["indice_premium"] = -999.0

            chevaux_complets.append(
                copie
            )

            continue


        # -------------------------------------------------
        # Partant valide
        # -------------------------------------------------

        copie["est_non_partant"] = False

        if not copie.get("statut"):
            copie["statut"] = "PARTANT"


        # =================================================
        # INDICE AZ
        # =================================================

        score_az = calculer_score_az(
            copie,
            discipline=discipline
        )


        copie["score_az"] = score_az
        copie["indice_az"] = score_az


        # =================================================
        # INDICE PREMIUM
        # =================================================

        copie["indice_premium"] = (
            calculer_indice_premium(
                copie,
                discipline=discipline
            )
        )


        chevaux_complets.append(
            copie
        )

        chevaux_valides.append(
            copie
        )


    # =====================================================
    # CLASSEMENT DES PARTANTS
    # =====================================================

    classement = classer_chevaux(
        chevaux_valides
    )


    # =====================================================
    # ATTRIBUTION DES RANGS
    # =====================================================

    rang = 1


    for cheval in classement:

        cheval["rang"] = rang
        cheval["est_non_partant"] = False
        cheval["statut"] = "PARTANT"

        rang += 1


    # =====================================================
    # RECONSTITUTION DE LA LISTE COMPLETE
    #
    # Les partants sont classés par rang.
    # Les NP restent à la fin pour l'affichage.
    # =====================================================

    non_partants_affichage = [
        cheval
        for cheval in chevaux_complets
        if cheval.get(
            "est_non_partant"
        )
    ]


    non_partants_affichage.sort(
        key=lambda cheval:
            int(
                _numero_str(
                    cheval.get("numero")
                )
            )
            if _numero_str(
                cheval.get("numero")
            ).isdigit()
            else 9999
    )


    chevaux_affichage = (
        list(classement)
        + non_partants_affichage
    )


    # =====================================================
    # GENERATION DES TICKETS
    # =====================================================
    #
    # quinte.py reçoit UNIQUEMENT les vrais partants.
    #
    # Il peut donc utiliser :
    #
    #   indice_az
    #   indice_premium
    #
    # sans jamais intégrer un NP.
    # =====================================================

    tickets = generer_tickets_az(
        classement
    )


    # =====================================================
    # FAVORI
    # =====================================================

    favori = (
        classement[0]
        if classement
        else {}
    )


    # =====================================================
    # SAUVEGARDE HISTORIQUE
    # =====================================================

    try:

        enregistrer_course({

            "chevaux":
                chevaux_valides,

            "classement":
                classement,

            "tickets":
                tickets,

            "selection_az":
                (
                    tickets
                    .get("gratuit", {})
                    .get("quinte", [])
                ),

            "selection_premium":
                (
                    tickets
                    .get("premium", {})
                    .get("selection_quinte", [])
                ),

            "favori":
                favori,

            "non_partants":
                sorted(
                    list(np_nums),
                    key=lambda x:
                        int(x)
                        if str(x).isdigit()
                        else 9999
                ),

            "course":
                info_course,

        })


    except Exception as erreur:

        # L'analyse ne doit jamais être bloquée
        # si le module historique rencontre une erreur.
        print(
            "Erreur enregistrement historique :",
            erreur
        )


    # =====================================================
    # REPONSE API
    # =====================================================

    return {

        "message":
            "Analyse AZ Turf Pro terminée",

        # Liste destinée notamment au tableau
        # des partants avec les NP visibles.
        "chevaux":
            chevaux_affichage,

        # Classement des vrais partants uniquement.
        "classement":
            classement,

        # Tous les chevaux reçus.
        "partants_complets":
            chevaux_affichage,

        # Numéros des NP.
        "non_partants":
            sorted(
                list(np_nums),
                key=lambda x:
                    int(x)
                    if str(x).isdigit()
                    else 9999
            ),

        # Favori AZ.
        "favori":
            favori,

        # Tickets gratuits + Premium.
        "tickets":
            tickets,

        }
