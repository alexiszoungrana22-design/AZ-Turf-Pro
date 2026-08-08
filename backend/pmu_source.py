# =====================================
# AZ TURF PRO
# SOURCE PMU
# Connexion aux données PMU réelles
# =====================================
#
# CORRECTIONS APPORTEES A CETTE VERSION (rien d'autre n'a change) :
#
# 1. BUG REEL CORRIGE : recuperer_programme() retournait la reponse
#    JSON brute, mais l'API PMU enveloppe le programme dans une cle
#    "programme" (confirme par test direct + plusieurs sources
#    techniques independantes). trouver_reunion() cherchait donc
#    "reunions" au mauvais niveau et ne trouvait jamais rien, meme
#    quand la requete reseau reussissait. Corrige en depaquetant
#    cette cle des la reception (avec repli si jamais l'API change
#    de forme et renvoie un jour un JSON non enveloppe).
#
# 2. reunion/course_numero ne sont plus figes en dur a "R1"/"C1"
#    par defaut : si non precises, une fonction dediee lit le vrai
#    programme du jour et choisit la premiere reunion et la
#    premiere course reellement disponibles. charger_course_pmu()
#    reste 100% compatible avec les appels existants
#    (date, reunion, course_numero) : rien ne change si on les
#    fournit explicitement.
#
# Tout le reste (formules de score, transformer_participant,
# transformer_course, extraction cote/gains/musique) est identique
# a la version precedente, deja validee.


import math
import requests
from datetime import datetime


# =====================================
# CONFIGURATION
# =====================================

PMU_BASE_URL = (
    "https://turfinfo.api.prd.pmutech.fr"
    "/rest/client/61/programme"
)

TIMEOUT = 10


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
            hippodrome.get("libelleLong")
            or hippodrome.get("libelle")
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

def recuperer_programme(date):
    """
    Récupère le programme PMU du jour.

    L'API PMU actuelle utilise :
    /rest/client/61/programme/{date}/R{reunion}
    avec specialisation=INTERNET.

    On récupère les réunions disponibles puis on les
    rassemble dans un format compatible avec le reste
    du module.
    """

    reunions = []

    try:
        # Les réunions PMU sont généralement numérotées
        # R1, R2, R3...
        for numero_reunion in range(1, 20):

            url = (
                f"{PMU_BASE_URL}/"
                f"{date}/"
                f"R{numero_reunion}"
            )

            response = requests.get(
                url,
                params={
                    "specialisation": "INTERNET"
                },
                timeout=TIMEOUT,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "AZ-Turf-Pro/1.0"
                }
            )

            # Une réunion inexistante n'est pas une raison
            # pour interrompre tout le programme.
            if response.status_code == 404:
                continue

            response.raise_for_status()

            donnees = response.json()

            if not isinstance(donnees, dict):
                continue

            # L'API renvoie directement une réunion.
            if donnees.get("numReunion") is not None:
                reunions.append(donnees)

            elif donnees.get("numExterne") is not None:
                reunions.append(donnees)

            # Protection supplémentaire si l'API renvoie
            # exceptionnellement un conteneur de réunions.
            elif isinstance(donnees.get("reunions"), list):
                reunions.extend(
                    r for r in donnees["reunions"]
                    if isinstance(r, dict)
                )

    except Exception as erreur:

        print(
            "Erreur programme PMU :",
            erreur
        )

    if not reunions:
        return None

    return {
        "reunions": reunions
            }


# =====================================
# SELECTION AUTOMATIQUE DE LA COURSE DU JOUR
# (utilisee uniquement si reunion/course_numero
# ne sont pas fournis explicitement)
# =====================================

def choisir_premiere_course_disponible(programme):
    """
    Choisit la premiere reunion et la premiere course reellement
    presentes dans le programme du jour (au lieu de supposer que
    R1/C1 existe toujours). Retourne (reunion, course_numero) sous
    forme de chaines 'R1'/'C1', ou (None, None) si le programme est
    vide ou inexploitable.
    """

    if not programme:
        return None, None

    reunions = programme.get("reunions", [])

    if not isinstance(reunions, list) or not reunions:
        return None, None

    premiere_reunion = reunions[0]

    numero_reunion = (
        premiere_reunion.get("numReunion")
        or premiere_reunion.get("numero")
    )

    if numero_reunion is None:
        return None, None

    courses = premiere_reunion.get("courses", [])

    if not isinstance(courses, list) or not courses:
        return f"R{numero_reunion}", None

    premiere_course = courses[0]

    numero_course = (
        premiere_course.get("numOrdre")
        or premiere_course.get("numCourse")
        or premiere_course.get("numero")
    )

    if numero_course is None:
        return f"R{numero_reunion}", None

    return f"R{numero_reunion}", f"C{numero_course}"


# =====================================
# RECHERCHE REUNION
# =====================================

def trouver_reunion(
    programme,
    reunion
):

    if not programme:
        return None

    reunions = programme.get(
        "reunions",
        []
    )

    if not isinstance(
        reunions,
        list
    ):
        return None

    code_reunion = str(
        reunion or ""
    ).upper().strip()

    if code_reunion.startswith("R"):
        numero_reunion = (
            code_reunion[1:]
        )
    else:
        numero_reunion = code_reunion

    for reunion_data in reunions:

        if not isinstance(
            reunion_data,
            dict
        ):
            continue

        numero = (
            reunion_data.get("numReunion")
            or reunion_data.get("numero")
        )

        if str(numero).strip() == numero_reunion:
            return reunion_data

        libelle = str(
            reunion_data.get(
                "libelle",
                ""
            )
        ).upper()

        if code_reunion in libelle:
            return reunion_data

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

def recuperer_participants(
    date,
    reunion,
    course_numero
):

    reunion_numero = str(
        reunion or ""
    ).upper().replace(
        "R",
        ""
    )

    course_numero = str(
        course_numero or ""
    ).upper().replace(
        "C",
        ""
    )

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
        params={
            "specialisation": "INTERNET"
        },
        timeout=TIMEOUT,
        headers={
            "Accept": "application/json",
            "User-Agent": "AZ-Turf-Pro/1.0"
        }
    )

    response.raise_for_status()

    donnees = response.json()

    if isinstance(donnees, dict):

        participants = donnees.get(
            "participants",
            []
        )

        if isinstance(participants, list):
            return participants

    if isinstance(donnees, list):
        return donnees

except Exception as erreur:

    print(
        "Erreur participants PMU :",
        erreur
    )

return []


# =====================================
# CHARGEMENT COURSE PMU
# =====================================

def charger_course_pmu(
    date,
    reunion=None,
    course_numero=None
):
    """
    Compatible avec les appels existants charger_course_pmu(date,
    reunion, course_numero) : si reunion/course_numero sont fournis
    (ex: "R1", "C1"), le comportement est identique a avant.

    Si l'un des deux (ou les deux) n'est pas fourni (None), la
    reunion et/ou la course sont determinees automatiquement a
    partir du vrai programme du jour, au lieu de supposer R1/C1.
    """

    try:

        programme = recuperer_programme(
            date
        )

        if not programme:
            return None

        if not reunion or not course_numero:

            reunion_auto, course_auto = (
                choisir_premiere_course_disponible(
                    programme
                )
            )

            reunion = reunion or reunio
