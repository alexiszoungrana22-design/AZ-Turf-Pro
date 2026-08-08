# =====================================
# AZ TURF PRO
# SOURCE PMU
# Connexion aux donnÃ©es PMU rÃ©elles
# =====================================
#
# VERSION DEFINITIVE - fichier complet, pret a remplacer
# backend/pmu_source.py directement.
#
# CE QUI A CHANGE PAR RAPPORT A LA VERSION PRECEDENTE :
#
# - _contient_quinte() ne fait plus une recherche de texte "QUINTE"
#   dans TOUS les champs de la course (trop permissif : provoquait
#   un faux positif sur une course ordinaire a 6 partants). La
#   detection se fait desormais en 2 temps :
#     1. Recherche ciblee dans la liste des types de paris proposes
#        sur la course (champ "paris"/"parisPMU"/"typesParis" selon
#        ce que l'API expose reellement - plusieurs noms possibles
#        tentes, car non garanti par une documentation officielle).
#     2. A defaut, repli sur une recherche textuelle du libelle,
#        MAIS uniquement si le nombre de partants declares est >= 10
#        (un vrai Quinte+ reunit toujours un grand champ - c'est
#        cette condition qui elimine le faux positif observe).
# - Fonctions dupliquees (recuperer_programme/trouver_reunion
#   presentes deux fois dans le fichier fourni precedemment)
#   nettoyees : une seule definition propre de chacune.
#
# CE QUI N'A PAS CHANGE :
# - PMU_BASE_URL (client 61, turfinfo.api.prd.pmutech.fr) conserve.
# - Toutes les formules de score (forme, regularite, gains, cote,
#   experience), transformer_participant, transformer_course :
#   identiques, non touchees.
# - charger_course_pmu(date, reunion=None, course_numero=None) :
#   signature identique, compatible avec api.py.
# - quinte.py : aucune dependance, non concerne, non touche. Les
#   tailles de tickets (Quinte 6, Quarte 5, Trio 3, etc.) restent
#   sous la responsabilite exclusive de quinte.py, jamais de ce
#   fichier.


import math
import requests


# =====================================
# CONFIGURATION
# =====================================

PMU_BASE_URL = (
    "https://turfinfo.api.prd.pmutech.fr"
    "/rest/client/61/programme"
)

TIMEOUT = 8


# =====================================
# OUTILS
# =====================================

def limiter_score(valeur):
    try:
        valeur = float(valeur)
    except (TypeError, ValueError):
        return 5.0

    return max(0.0, min(10.0, valeur))


def extraire_positions(musique):
    if not musique:
        return []

    texte = str(musique).upper()

    positions = []
    nombre = ""

    for caractere in texte:
        if caractere.isdigit():
            nombre += caractere
        else:
            if nombre:
                try:
                    position = int(nombre)

                    if position > 0:
                        positions.append(position)

                except ValueError:
                    pass

                nombre = ""

    if nombre:
        try:
            position = int(nombre)

            if position > 0:
                positions.append(position)

        except ValueError:
            pass

    return positions


# =====================================
# FORME
# =====================================

def calculer_forme(positions):
    if not positions:
        return 5.0

    recentes = positions[:5]

    moyenne = (
        sum(recentes) / len(recentes)
    )

    score = 10.0 - moyenne

    return limiter_score(score)


# =====================================
# REGULARITE
# =====================================

def calculer_regularite(positions):
    if len(positions) < 2:
        return 5.0

    recentes = positions[:8]

    moyenne = (
        sum(recentes) / len(recentes)
    )

    variance = sum(
        (position - moyenne) ** 2
        for position in recentes
    ) / len(recentes)

    ecart_type = math.sqrt(variance)

    score = 10.0 - ecart_type

    return limiter_score(score)


# =====================================
# EXPERIENCE
# =====================================

def calculer_experience(nombre_courses):
    try:
        nombre_courses = float(
            nombre_courses or 0
        )
    except (TypeError, ValueError):
        nombre_courses = 0

    return limiter_score(
        nombre_courses / 10.0
    )


# =====================================
# NORMALISATION
# =====================================

def normaliser(valeur, minimum, maximum):
    try:
        valeur = float(valeur)
        minimum = float(minimum)
        maximum = float(maximum)
    except (TypeError, ValueError):
        return 5.0

    if maximum == minimum:
        return 5.0

    score = (
        (valeur - minimum)
        / (maximum - minimum)
    ) * 10.0

    return limiter_score(score)


# =====================================
# EXTRACTION COTE
# =====================================

def obtenir_cote(participant):
    rapport_data = participant.get(
        "dernierRapportDirect",
        {}
    )

    if not isinstance(rapport_data, dict):
        rapport_data = {}

    rapport = rapport_data.get(
        "rapport"
    )

    try:
        rapport = float(rapport)
    except (TypeError, ValueError):
        return None

    if rapport <= 0:
        return None

    return rapport


# =====================================
# SCORES COTES
# =====================================

def calculer_scores_cotes(participants):
    cotes = []

    for participant in participants:
        cote = obtenir_cote(participant)

        if cote is not None:
            cotes.append(cote)

    if not cotes:
        return {}

    minimum = min(cotes)
    maximum = max(cotes)

    resultats = {}

    for participant in participants:
        numero = participant.get(
            "numPmu"
        )

        cote = obtenir_cote(
            participant
        )

        if cote is None:
            resultats[numero] = {
                "score": 5.0,
                "cote": None
            }
            continue

        if maximum == minimum:
            score = 5.0
        else:
            score = (
                (maximum - cote)
                / (maximum - minimum)
            ) * 10.0

        resultats[numero] = {
            "score": limiter_score(score),
            "cote": cote
        }

    return resultats


# =====================================
# SCORES GAINS
# =====================================

def obtenir_gains(participant):
    gains_data = participant.get(
        "gainsParticipant",
        {}
    )

    if not isinstance(gains_data, dict):
        gains_data = {}

    gains = gains_data.get(
        "gainsCarriere",
        0
    )

    try:
        return float(gains or 0)
    except (TypeError, ValueError):
        return 0.0


def calculer_scores_gains(participants):
    valeurs = [
        obtenir_gains(p)
        for p in participants
    ]

    if not valeurs:
        return {}

    minimum = min(valeurs)
    maximum = max(valeurs)

    resultats = {}

    for participant in participants:
        numero = participant.get(
            "numPmu"
        )

        gains = obtenir_gains(
            participant
        )

        resultats[numero] = normaliser(
            gains,
            minimum,
            maximum
        )

    return resultats


# =====================================
# TERRAIN
# =====================================

def obtenir_terrain(course):
    penetrometre = course.get(
        "penetrometre",
        {}
    )

    if isinstance(
        penetrometre,
        dict
    ):
        return penetrometre.get(
            "intitule",
            "Non disponible"
        )

    return "Non disponible"


# =====================================
# EXTRACTION NOMBRE DE COURSES
# =====================================

def obtenir_nombre_courses(participant):
    for cle in (
        "nombreCourses",
        "nombreCoursesCarriere",
        "nbCourses"
    ):
        valeur = participant.get(cle)

        if valeur not in (
            None,
            ""
        ):
            return valeur

    return 0


# =====================================
# TRANSFORMATION PARTICIPANT
# =====================================

def transformer_participant(
    participant,
    course,
    scores_cotes,
    scores_gains
):

    numero = participant.get(
        "numPmu"
    )

    nom = participant.get(
        "nom",
        ""
    )

    age = participant.get(
        "age",
        0
    )

    sexe = participant.get(
        "sexe",
        ""
    )

    if str(sexe).upper() == "HONGRES":
        sexe = "M"

    jockey = (
        participant.get("driver")
        or participant.get("jockey")
        or participant.get("pilote")
        or ""
    )

    entraineur = (
        participant.get("entraineur")
        or participant.get("trainer")
        or ""
    )

    musique = participant.get(
        "musique",
        ""
    )

    performances = extraire_positions(
        musique
    )

    forme = calculer_forme(
        performances
    )

    regularite = calculer_regularite(
        performances
    )

    gains = scores_gains.get(
        numero,
        5.0
    )

    cote_data = scores_cotes.get(
        numero,
        {}
    )

    cote = cote_data.get(
        "score",
        5.0
    )

    cote_brute = cote_data.get(
        "cote"
    )

    nombre_courses = obtenir_nombre_courses(
        participant
    )

    experience = calculer_experience(
        nombre_courses
    )

    # =================================
    # VALEURS NEUTRES
    # =================================

    distance_score = 5.0
    terrain_score = 5.0
    jockey_score = 5.0

    terrain_info = obtenir_terrain(
        course
    )

    return {

        "numero": numero,

        "nom": nom,

        "age": age,

        "sexe": sexe,

        "jockey": jockey,

        "entraineur": entraineur,

        "performances": performances,

        "forme": forme,

        "regularite": regularite,

        "gains": gains,

        "jockey_score": jockey_score,

        "cote": cote,

        "distance": distance_score,

        "terrain": terrain_score,

        "terrain_info": terrain_info,

        "experience": experience,

        "cote_brute": cote_brute,

        "gains_carriere_brute":
            obtenir_gains(participant),

        "musique_brute": musique
    }


# =====================================
# EXTRACTION INFOS COURSE
# =====================================

def obtenir_hippodrome(course):
    hippodrome = course.get(
        "hippodrome",
        ""
    )

    if isinstance(
        hippodrome,
        dict
    ):
        return (
            hippodrome.get("libelle")
            or hippodrome.get("nom")
            or ""
        )

    return hippodrome


def obtenir_discipline(course):
    discipline = course.get(
        "discipline",
        ""
    )

    if isinstance(
        discipline,
        dict
    ):
        return (
            discipline.get("libelle")
            or discipline.get("nom")
            or ""
        )

    return discipline


# =====================================
# TRANSFORMATION COURSE
# =====================================

def transformer_course(
    course,
    participants
):

    if not participants:
        return None

    scores_cotes = (
        calculer_scores_cotes(
            participants
        )
    )

    scores_gains = (
        calculer_scores_gains(
            participants
        )
    )

    chevaux = []

    for participant in participants:

        cheval = transformer_participant(
            participant,
            course,
            scores_cotes,
            scores_gains
        )

        if cheval.get("numero") is not None:
            chevaux.append(cheval)

    if not chevaux:
        return None

    date_course = (
        course.get("date")
        or course.get("dateCourse")
        or ""
    )

    reunion = (
        course.get("numReunion")
        or course.get("reunion")
        or ""
    )

    course_numero = (
        course.get("numOrdre")
        or course.get("numCourse")
        or course.get("numero")
        or ""
    )

    return {

        "course":
            course.get(
                "libelle",
                course.get(
                    "nom",
                    "Course"
                )
            ),

        "date":
            date_course,

        "reunion":
            reunion,

        "course_numero":
            course_numero,

        "hippodrome":
            obtenir_hippodrome(course),

        "discipline":
            obtenir_discipline(course),

        "distance_course":
            course.get(
                "distance",
                ""
            ),

        "allocation":
            course.get(
                "montantPrix",
                course.get(
                    "allocation",
                    ""
                )
            ),

        "chevaux":
            chevaux,

        "plus_joues":
            [],

        "source_plus_joues":
            "non disponible via API PMU",

        "source":
            "pmu_live"
    }


# =====================================
# RECUPERATION PROGRAMME
# =====================================

def recuperer_programme(date, reunion=None):
    """
    RÃ©cupÃ¨re le programme d'une rÃ©union PMU.

    reunion=None est volontairement acceptÃ© afin que la recherche
    automatique (trouver_quinte_du_jour) puisse parcourir les
    rÃ©unions de la journÃ©e. Sans rÃ©union prÃ©cisÃ©e, retourne None.
    """

    if reunion is None:
        return None

    reunion_numero = (
        str(reunion)
        .upper()
        .replace("R", "")
        .strip()
    )

    if not reunion_numero.isdigit():
        return None

    url = (
        f"{PMU_BASE_URL}/"
        f"{date}/"
        f"R{reunion_numero}"
    )

    try:
        response = requests.get(
            url,
            params={"specialisation": "INTERNET"},
            timeout=TIMEOUT,
            headers={
                "Accept": "application/json",
                "User-Agent": "AZ-Turf-Pro/1.0",
            },
        )

        response.raise_for_status()

        donnees = response.json()

        if not isinstance(donnees, dict):
            return None

        return donnees

    except Exception as erreur:
        print(
            f"Erreur programme PMU R{reunion_numero} :",
            erreur
        )
        return None


# =====================================
# RECHERCHE REUNION
# =====================================

def trouver_reunion(programme, reunion):
    """
    Avec l'API PMU client/61, l'appel /programme/date/R{n} retourne
    directement les donnÃ©es de la rÃ©union (pas une liste de
    rÃ©unions Ã  filtrer) : cette fonction vÃ©rifie simplement que la
    rÃ©ponse correspond bien Ã  la rÃ©union demandÃ©e, ou qu'elle
    contient au moins une liste de courses exploitable.
    """

    if not programme or not isinstance(programme, dict):
        return None

    code_reunion = str(reunion or "").upper().strip()

    if not code_reunion:
        return None

    if not code_reunion.startswith("R"):
        code_reunion = f"R{code_reunion}"

    numero_recherche = code_reunion[1:]

    numero = str(
        programme.get("numOfficiel")
        or programme.get("numReunion")
        or programme.get("numero")
        or ""
    ).strip()

    if numero and numero == numero_recherche:
        return programme

    if isinstance(programme.get("courses"), list):
        return programme

    return None


# =====================================
# RECHERCHE COURSE
# =====================================

def trouver_course(
    reunion_data,
    course_numero
):

    if not reunion_data:
        return None

    courses = reunion_data.get(
        "courses",
        []
    )

    if not isinstance(
        courses,
        list
    ):
        return None

    numero_recherche = str(
        course_numero or ""
    ).upper().strip()

    if numero_recherche.startswith("C"):
        numero_recherche = (
            numero_recherche[1:]
        )

    for course in courses:

        if not isinstance(
            course,
            dict
        ):
            continue

        numero = (
            course.get("numOrdre")
            or course.get("numCourse")
            or course.get("numero")
        )

        if str(numero).strip() == numero_recherche:
            return course

        libelle = str(
            course.get(
                "libelle",
                ""
            )
        ).upper()

        if (
            numero_recherche
            and numero_recherche in libelle
        ):
            return course

    return None


# =====================================
# RECUPERATION PARTICIPANTS
# =====================================

def recuperer_participants(date, reunion, course_numero):
    reunion_numero = str(
        reunion or "R1"
    ).upper().replace("R", "").strip()

    course_numero = str(
        course_numero or "C1"
    ).upper().replace("C", "").strip()

    url = (
        f"{PMU_BASE_URL}/"
        f"{date}/"
        f"R{reunion_numero}/"
        f"C{course_numero}/"
        f"participants"
    )

    try:
        response = requests.get(
            url,
            params={"specialisation": "INTERNET"},
            timeout=TIMEOUT,
            headers={
                "Accept": "application/json",
                "User-Agent": "AZ-Turf-Pro/1.0",
            },
        )

        response.raise_for_status()
        donnees = response.json()

        if isinstance(donnees, dict):
            participants = donnees.get("participants", [])

            if isinstance(participants, list):
                return participants

        if isinstance(donnees, list):
            return donnees

    except Exception as erreur:
        print("Erreur participants PMU :", erreur)

    return []


# =====================================
# DETECTION FIABILISEE DU QUINTE+
# =====================================
#
# NOMBRE MINIMUM DE PARTANTS pour qu'une course puisse
# raisonnablement etre le Quinte+ (un vrai Quinte+ reunit toujours
# un grand champ, historiquement 14 a 20 partants). Ce seuil sert
# de garde-fou anti-faux-positif : une course a 6 partants ne peut
# jamais etre retenue, meme si le mot "quinte" apparait ailleurs
# dans son JSON.

PARTANTS_MINIMUM_QUINTE = 10


def _nombre_partants(course):
    for cle in (
        "nombreDeclaresPartants",
        "nombrePartants",
        "nbPartants"
    ):
        valeur = course.get(cle)

        try:
            if valeur not in (None, ""):
                return int(valeur)
        except (TypeError, ValueError):
            continue

    return 0


def _extraire_types_paris(course):
    """
    Retourne la liste des types de paris proposes sur la course, si
    le champ existe. Le nom exact de ce champ n'est pas garanti par
    une documentation officielle publique de l'API PMU : plusieurs
    noms plausibles sont donc tentes.
    """

    for cle in ("paris", "parisPMU", "typesParis", "listePari"):
        valeur = course.get(cle)

        if isinstance(valeur, list):
            return valeur

    return []


def _contient_quinte(course):
    """
    DÃ©tection du QuintÃ©+ en deux temps, du plus fiable au moins
    fiable - corrige le faux positif observe (course a 6 partants
    retenue a tort par une simple recherche de texte globale) :

    1. Recherche CIBLEE dans la liste des types de paris proposes
       sur la course (si ce champ existe dans la reponse API) : on
       cherche un code contenant "QUINTE" explicitement dans cette
       liste, pas n'importe ou dans le JSON.

    2. A DEFAUT SEULEMENT, repli sur une recherche textuelle du
       libelle de la course - mais UNIQUEMENT si le nombre de
       partants declares est >= PARTANTS_MINIMUM_QUINTE. Cette
       condition est ce qui empeche desormais une course ordinaire
       a peu de partants d'etre confondue avec le Quinte+.
    """

    if not isinstance(course, dict):
        return False

    # ---- 1. Detection ciblee via la
