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
    - génération des badges intelligents et du radar expert
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
# BADGES ET RADAR EXPERT
# =========================================================

def generer_badges_et_radar(cheval, info_course=None):
    """
    Génère les badges visuels et les notes du radar sur 100.
    """
    badges = []
    info_c = info_course if isinstance(info_course, dict) else {}

    # --- Badges Intelligents ---
    deferre = str(cheval.get("deferre", "") or "").strip().upper()

    if deferre in ("D4", "DP_DG"):
        badges.append({"code": "D4", "libelle": "Déferré D4", "couleur": "#28a745"})

    elif deferre in ("DA", "DP"):
        badges.append({"code": "DP", "libelle": "Déferré", "couleur": "#17a2b8"})


    taux_jockey = _float(cheval.get("reussite_jockey", 0), 0)
    confiance_ent = int(_float(cheval.get("confiance_entraineur", 1), 1))

    if taux_jockey >= 35 or confiance_ent == 2:
        badges.append({"code": "DUO_HOT", "libelle": "Duo Chaud 🔥", "couleur": "#ffc107"})


    hippodrome = str(info_c.get("hippodrome", "") or "").strip().upper()
    hippo_fav = str(cheval.get("hippodromes_favoris", "") or "").strip().upper()

    if hippodrome and hippodrome in hippo_fav:
        badges.append({"code": "TRACEE", "libelle": "Spécialiste 🎯", "couleur": "#17a2b8"})


    musique = str(cheval.get("musique", "") or "").strip().upper()
    cote = _float(cheval.get("cote", 20), 20)

    if ("DA" in musique or "DISQ" in musique) and cote < 8.0:
        badges.append({"code": "RACHAT", "libelle": "Rachat ⚡", "couleur": "#fd7e14"})


    # --- Notes Radar ---
    forme = min(100.0, _float(cheval.get("forme", 5), 5) * 10.0)

    dist_course = int(_float(info_c.get("distance", 2000), 2000))
    dist_pref = int(_float(cheval.get("distance_predilection", dist_course), dist_course))
    aptitude_dist = max(20.0, 100.0 - (abs(dist_course - dist_pref) / 5.0))

    jockey_score = min(100.0, max(30.0, taux_jockey * 2.0))

    gains = _float(cheval.get("gains_carriere", 0), 0)
    courses = max(1, int(_float(cheval.get("nombre_courses", 1), 1)))
    classe_valeur = min(100.0, max(20.0, (gains / courses) / 100.0))

    jours_repos = int(_float(cheval.get("jours_depuis_derniere_course", 20), 20))
    fraicheur = 100.0 if 12 <= jours_repos <= 30 else (50.0 if jours_repos > 90 else 75.0)


    radar = {
        "forme": round(forme, 1),
        "distance": round(aptitude_dist, 1),
        "jockey": round(jockey_score, 1),
        "classe": round(classe_valeur, 1),
        "fraicheur": round(fraicheur, 1)
    }

    return badges, radar


# =========================================================
# INDICE PREMIUM
# =========================================================

def calculer_indice_premium(cheval, info_course=None, discipline="TROT"):
    """
    Calcule l'Indice Premium AZ Pro.
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

            if isinstance(
                performance,
                (int, float)
            ):

                if performance <= 3:
                    bonnes_places += 1

                continue

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
    # Bonus Experts
    # -----------------------------------------------------

    bonus_expert = 0.0
    info_c = info_course if isinstance(info_course, dict) else {}

    dist_course = int(_float(info_c.get("distance", 2000), 2000))
    dist_pref = int(_float(cheval.get("distance_predilection", dist_course), dist_course))

    if abs(dist_course - dist_pref) <= 200:
        bonus_expert += 10.0

    deferre = str(cheval.get("deferre", "") or "").strip().upper()

    if deferre in ("D4", "DP_DG"):
        bonus_expert += 12.0
    elif deferre in ("DA", "DP"):
        bonus_expert += 6.0

    # -----------------------------------------------------
    # Smart Money (variation de cote entre le matin et le direct)
    # -----------------------------------------------------

    bonus_smart_money = 0.0
    variation_cote_pct = _float(cheval.get("variation_cote_pct", 0), 0)

    if variation_cote_pct <= -20.0:
        bonus_smart_money = 14.0
    elif variation_cote_pct <= -5.0:
        bonus_smart_money = 6.0
    elif variation_cote_pct >= 20.0:
        bonus_smart_money = -6.0

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
        + bonus_expert
        + bonus_smart_money
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
    """

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

            copie["est_non_partant"] = True
            copie["statut"] = "NON_PARTANT"
            copie["rang"] = "NP"

            copie["score_az"] = -999.0
            copie["indice_az"] = -999.0
            copie["indice_premium"] = -999.0
            copie["badges"] = []
            copie["radar"] = {}

            chevaux_complets.append(
                copie
            )

            continue


        copie["est_non_partant"] = False

        if not copie.get("statut"):
            copie["statut"] = "PARTANT"


        score_az = calculer_score_az(
            copie,
            discipline=discipline
        )


        copie["score_az"] = score_az
        copie["indice_az"] = score_az


        copie["indice_premium"] = (
            calculer_indice_premium(
                copie,
                info_course=info_course,
                discipline=discipline
            )
        )

        badges, radar = generer_badges_et_radar(
            copie,
            info_course=info_course
        )

        copie["badges"] = badges
        copie["radar"] = radar


        chevaux_complets.append(
            copie
        )

        chevaux_valides.append(
            copie
        )


    classement = classer_chevaux(
        chevaux_valides
    )


    rang = 1


    for cheval in classement:

        cheval["rang"] = rang
        cheval["est_non_partant"] = False
        cheval["statut"] = "PARTANT"

        rang += 1


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


    tickets = generer_tickets_az(
        classement
    )


    favori = (
        classement[0]
        if classement
        else {}
    )


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

        print(
            "Erreur enregistrement historique :",
            erreur
        )


    return {

        "message":
            "Analyse AZ Turf Pro terminée",

        "chevaux":
            chevaux_affichage,

        "classement":
            classement,

        "partants_complets":
            chevaux_affichage,

        "non_partants":
            sorted(
                list(np_nums),
                key=lambda x:
                    int(x)
                    if str(x).isdigit()
                    else 9999
            ),

        "favori":
            favori,

        "tickets":
            tickets,

    }
