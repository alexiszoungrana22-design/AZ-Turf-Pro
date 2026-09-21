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
from learning import enregistrer_course, lire_historique
from race_analyzer import analyser_course_premium, bonus_premium_cheval
from modules.engine_complementary import construire_analyse_complementaire
from intelligence.history_manager import enregistrer_pronostic

try:
    from archive_store import archiver_course
except Exception:
    archiver_course = None


# Enregistrement V25 (non bloquant)
def _sauvegarder_v25(data):
    try:
        enregistrer_pronostic(data)
    except Exception:
        pass


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

def calculer_indice_premium(cheval, info_course=None, discipline="TROT", analyse_premium=None):
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

    cote_score = _float(
        cheval.get("cote", 5),
        5
    )
    cote_brute = _float(
        cheval.get("cote_brute", cote_score),
        cote_score
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
    # CORRECTION : la condition précédente (cote >= 10 ET (forme >= 7 OU
    # régularité >= 7)) se déclenchait pour environ 40% des chevaux d'une
    # course type (vérifié : 5 chevaux sur 12 sur un jeu de données
    # réaliste), avec un bonus fixe de +15 — suffisant pour effacer un
    # écart d'Indice AZ légitime et faire remonter des outsiders peu
    # fiables devant de vrais favoris. Resserré : les DEUX critères de
    # forme doivent être réunis (pas l'un ou l'autre), le seuil de cote
    # est relevé, et le bonus est réduit pour rester un simple coup de
    # pouce sur une course serrée plutôt qu'un facteur qui redistribue le
    # classement.
    bonus_outsider_chaud = 0.0

    if (
        cote_brute >= 12.0
        and forme >= 7.5
        and regularite >= 7.0
    ):

        bonus_outsider_chaud = 8.0

    # -----------------------------------------------------
    # Bonus Experts
    # -----------------------------------------------------

    bonus_expert = 0.0
    info_c = info_course if isinstance(info_course, dict) else {}

    # CORRECTION : "distance_predilection" n'est jamais réellement fournie
    # par les sources de données actuelles ; l'ancien code utilisait la
    # distance de la course elle-même comme valeur par défaut, ce qui
    # rendait l'écart toujours nul et donnait ce bonus à TOUS les chevaux
    # sans exception — un signal présenté comme réel alors qu'il ne l'était
    # jamais. Il ne s'applique désormais que si la donnée est vraiment
    # connue (jamais inventée), sinon aucun bonus n'est appliqué plutôt
    # que d'en simuler un.
    dist_pref_brute = cheval.get("distance_predilection")
    if dist_pref_brute not in (None, ""):
        dist_course = int(_float(info_c.get("distance", 2000), 2000))
        dist_pref = int(_float(dist_pref_brute, dist_course))
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
    # Lecture contextuelle de la course - PREMIUM UNIQUEMENT
    # -----------------------------------------------------

    bonus_contexte_course = bonus_premium_cheval(
        analyse_premium,
        cheval
    )

    # -----------------------------------------------------
    # Calcul Premium
    # -----------------------------------------------------

    # CORRECTION : forme et régularité étaient comptées jusqu'à 3 fois au
    # total dans le pipeline Premium — une fois dans indice_az (déjà pondéré
    # par discipline dans scoring.py), une deuxième fois ici (forme*1.35,
    # regularite*1.20), une troisième fois dans bonus_contexte_course
    # (race_analyzer._horse_context). Ce n'était pas une analyse
    # supplémentaire : c'était le même signal amplifié plusieurs fois,
    # déformant l'équilibre entre critères sans rien ajouter de nouveau.
    # indice_az reste l'unique source de vérité pour forme/régularité ;
    # les termes redondants ont été retirés ici (voir aussi
    # race_analyzer._horse_context pour la 3e occurrence retirée).
    #
    # CORRECTION (même famille) : cote et expérience étaient elles aussi
    # comptées deux fois — une fois dans indice_az, une deuxième fois ici
    # (cote_score*1.10, experience*0.80). Retiré pour la même raison :
    # indice_az reste l'unique source de vérité pour ces deux critères
    # aussi. cote_score reste calculée ci-dessus car elle sert de repli
    # pour cote_brute (utilisée par bonus_outsider_chaud) ; experience
    # n'a plus d'autre usage dans cette fonction.
    indice_premium = (
        indice_az
        + (bonnes_places * 2.0)
        + bonus_outsider_chaud
        + bonus_expert
        + bonus_smart_money
        + bonus_contexte_course
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

    # Calibration issue de l'historique réel (modules.learning_turf +
    # archive_store) : chargée une seule fois par analyse, jamais
    # bloquante. Tant qu'aucune calibration n'a été calculée (ou que la
    # base n'est pas configurée), calibration_facteurs reste vide et le
    # moteur se comporte exactement comme avant.
    calibration_facteurs = {}
    try:
        from archive_store import lire_calibration
        _calib = lire_calibration()
        if _calib:
            calibration_facteurs = _calib.get("facteurs") or {}
    except Exception:
        calibration_facteurs = {}


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

    # Nouvelle couche additive : elle n'alimente que le Premium.
    # Le classement AZ gratuit et son scoring restent inchangés.
    analyse_premium = analyser_course_premium(
        info_course,
        chevaux
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
            discipline=discipline,
            calibration=calibration_facteurs
        )


        copie["score_az"] = score_az
        copie["indice_az"] = score_az


        copie["indice_premium"] = (
            calculer_indice_premium(
                copie,
                info_course=info_course,
                discipline=discipline,
                analyse_premium=analyse_premium
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

    # Les détails de lecture contextuelle sont stockés exclusivement
    # dans la branche Premium des tickets. Aucun champ nouveau n'est
    # ajouté au ticket gratuit.
    premium = tickets.get("premium")
    if isinstance(premium, dict):
        profile = analyse_premium.get("profil_course", {})
        signaux = analyse_premium.get("signaux", {})
        premium["lecture_course"] = {
            "profil": profile,
            "points_forts": signaux.get("points_forts", []),
            "points_attention": signaux.get("points_attention", []),
            "methode": (
                "Lecture contextuelle Premium : parcours + scénario + engagement + entourage + marché, "
                "sans remplacer l'Indice AZ existant."
            ),
        }


    # =====================================================
    # BRANCHEMENT RÉEL DES MODULES COMPLÉMENTAIRES
    # =====================================================
    # Additif : le classement et les indices AZ ci-dessus restent inchangés.
    # Chaque module reçoit les données réellement disponibles et son résultat
    # est conservé dans la réponse du moteur pour être consommé par le chatbot,
    # Analyse et Premium.
    analyse_complementaire = construire_analyse_complementaire(
        classement,
        info_course=info_course,
        historique=lire_historique(),
    )

    # Enrichissement non destructif : aucun score AZ/Premium n'est recalculé.
    signal_valeur = {
        str(x.get("numero")): x
        for x in analyse_complementaire.get("valeur", [])
        if isinstance(x, dict)
    }
    signal_cotes = {
        str(x.get("numero")): x
        for x in analyse_complementaire.get("tendances_cotes", [])
        if isinstance(x, dict)
    }
    for cheval in classement:
        numero = str(cheval.get("numero"))
        cheval["analyse_valeur"] = signal_valeur.get(numero, {})
        cheval["tendance_cote"] = signal_cotes.get(numero, {})

    favori = (
        classement[0]
        if classement
        else {}
    )

    # Provenance explicite : le frontend/chatbot peut distinguer une donnée
    # réellement fournie d'une valeur neutre de secours.
    total = max(1, len(classement))
    nb_cotes_brutes = sum(1 for c in classement if c.get("cote_brute") not in (None, ""))
    nb_jockey_stats = sum(1 for c in classement if c.get("reussite_jockey") not in (None, ""))
    nb_variations = sum(1 for c in classement if c.get("variation_cote_pct") not in (None, ""))
    qualite_donnees = {
        "partants": f"{len(classement)}/{len(chevaux_valides) or total}",
        "cotes_brutes": f"{nb_cotes_brutes}/{total}",
        "statistiques_jockey_driver": f"{nb_jockey_stats}/{total}",
        "variations_cotes": f"{nb_variations}/{total}",
        "presse": "disponible" if analyse_complementaire.get("presse") and analyse_complementaire.get("presse", {}).get("consensus") else "non_documentee",
        "meteo_piste": str(analyse_complementaire.get("meteo_piste", {}).get("impact", "NON_DOCUMENTE")),
        "historique_performance": analyse_complementaire.get("performance", {}).get("courses_evaluees", 0),
    }


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


    # Archive PostgreSQL persistante — ajout non bloquant.
    # L'historique existant ci-dessus reste inchangé.
    if archiver_course is not None:
        try:
            archiver_course({
                "chevaux": chevaux_valides,
                "classement": classement,
                "tickets": tickets,
                "selection_az": (
                    tickets.get("gratuit", {}).get("quinte", [])
                ),
                "selection_premium": (
                    tickets.get("premium", {}).get("selection_quinte", [])
                ),
                "favori": favori,
                "non_partants": sorted(
                    list(np_nums),
                    key=lambda x: int(x) if str(x).isdigit() else 9999
                ),
                "course": info_course,
            })
        except Exception as erreur:
            print("Erreur archive PostgreSQL :", erreur)


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

        # Résultats des modules complémentaires réellement exécutés.
        "analyse_complementaire": analyse_complementaire,

        # Transparence : indique si une calibration issue de l'historique
        # réel a été appliquée à cette analyse, et sur quels critères.
        # Vide tant qu'aucune calibration n'a été calculée (voir
        # /archive/calibrer) — comportement par défaut inchangé.
        "calibration_appliquee": calibration_facteurs,
        "qualite_donnees": qualite_donnees,
        "interpretation_confiance": (
            "Le champ confiance est une proximité de l'indice AZ au leader, "
            "pas une probabilité statistique de victoire."
        ),

    }
