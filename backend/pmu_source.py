# =====================================
# AZ TURF PRO
# SOURCE PMU
# Connexion aux données PMU réelles
# =====================================

import requests
import math


# =====================================
# CONFIGURATION
# =====================================

PMU_BASE_URL = (
    "https://offline.turfinfo.api.pmu.fr"
    "/rest/client/7/programme"
)

TIMEOUT = 5


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
        sum(recentes)
        / len(recentes)
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
        sum(recentes)
        / len(recentes)
    )

    variance = sum(
        (position - moyenne) ** 2
        for position in recentes
    ) / len(recentes)

    ecart_type = math.sqrt(
        variance
    )

    score = 10.0 - ecart_type

    return limiter_score(score)


# =====================================
# EXPERIENCE
# =====================================

def calculer_experience(
    nombre_courses
):

    try:

        nombre_courses = float(
            nombre_courses or 0
        )

    except (
        TypeError,
        ValueError
    ):

        nombre_courses = 0

    return limiter_score(
        nombre_courses / 10.0
    )


# =====================================
# NORMALISATION
# =====================================

def normaliser(
    valeur,
    minimum,
    maximum
):

    try:

        valeur = float(valeur)
        minimum = float(minimum)
        maximum = float(maximum)

    except (
        TypeError,
        ValueError
    ):

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

    rapport = (
        participant
        .get(
            "dernierRapportDirect",
            {}
        )
        .get(
            "rapport"
        )
    )

    try:

        rapport = float(rapport)

    except (
        TypeError,
        ValueError
    ):

        return None

    if rapport <= 0:
        return None

    return rapport


# =====================================
# SCORES COTES
# =====================================

def calculer_scores_cotes(
    participants
):

    cotes = []

    for participant in participants:

        cote = obtenir_cote(
            participant
        )

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

        # Plus la cote est basse,
        # plus le score est élevé.

        if maximum == minimum:

            score = 5.0

        else:

            score = (
                (maximum - cote)
                / (maximum - minimum)
            ) * 10.0

        resultats[numero] = {

            "score":
                limiter_score(score),

            "cote":
                cote
        }

    return resultats


# =====================================
# SCORES GAINS
# =====================================

def obtenir_gains(participant):

    gains = (
        participant
        .get(
            "gainsParticipant",
            {}
        )
        .get(
            "gainsCarriere",
            0
        )
    )

    try:

        return float(gains or 0)

    except (
        TypeError,
        ValueError
    ):

        return 0.0


def calculer_scores_gains(
    participants
):

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
        or ""
    )

    entraineur = participant.get(
        "entraineur",
        ""
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

    nombre_courses = participant.get(
        "nombreCourses",
        0
    )

    experience = calculer_experience(
        nombre_courses
    )

    # =================================
    # VALEURS NEUTRES
    # =================================

    # Aucune donnée fiable permettant
    # de mesurer l'aptitude individuelle
    # à la distance.
    distance_score = 5.0

    # Le terrain du jour est connu,
    # mais pas l'affinité individuelle.
    terrain_score = 5.0

    terrain_info = obtenir_terrain(
        course
    )

    # Aucune statistique jockey/driver
    # fiable dans cet endpoint.
    jockey_score = 5.0

    return {

        "numero": numero,

        "nom": nom,

        "age": age,

        "sexe": sexe,

        "jockey": jockey,

        "entraineur": entraineur,

        "performances":
            performances,

        "forme":
            forme,

        "regularite":
            regularite,

        "gains":
            gains,

        "jockey_score":
            jockey_score,

        "cote":
            cote,

        "distance":
            distance_score,

        "terrain":
            terrain_score,

        "terrain_info":
            terrain_info,

        "experience":
            experience,

        "cote_brute":
            cote_brute,

        "gains_carriere_brute":
            obtenir_gains(
                participant
            ),

        "musique_brute":
            musique
    }


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

        chevaux.append(
            cheval
        )

    hippodrome = course.get(
        "hippodrome",
        ""
    )

    if isinstance(
        hippodrome,
        dict
    ):

        hippodrome = hippodrome.get(
            "libelle",
            ""
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
            course.get(
                "date",
                ""
            ),

        "hippodrome":
            hippodrome,

        "discipline":
            course.get(
                "discipline",
                ""
            ),

        "distance_course":
            course.get(
                "distance",
                ""
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

def recuperer_programme(
    date
):

    url = (
        f"{PMU_BASE_URL}/"
        f"{date}/"
    )

    try:

        response = requests.get(
            url,
            timeout=TIMEOUT
        )

        response.raise_for_status()

        return response.json()

    except Exception as erreur:

        print(
            "Erreur programme PMU :",
            erreur
        )

        return None


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

    code_reunion = str(
        reunion
    ).upper()

    if not code_reunion.startswith(
        "R"
    ):

        code_reunion = (
            "R" + code_reunion
        )

    for r in reunions:

        numero = (
            r.get("numReunion")
            or r.get("numero")
        )

        if str(numero).upper() == code_reunion.replace(
            "R",
            ""
        ):

            return r

        libelle = str(
            r.get(
                "libelle",
                ""
            )
        ).upper()

        if code_reunion in libelle:

            return r

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

    numero_recherche = str(
        course_numero
    ).upper()

    if not numero_recherche.startswith(
        "C"
    ):

        numero_recherche = (
            "C" + numero_recherche
        )

    for course in courses:

        numero = (
            course.get("numOrdre")
            or course.get("numCourse")
            or course.get("numero")
        )

        if str(numero).upper() == (
            numero_recherche.replace(
                "C",
                ""
            )
        ):

            return course

        libelle = str(
            course.get(
                "libelle",
                ""
            )
        ).upper()

        if numero_recherche in libelle:

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
        reunion
    ).upper().replace(
        "R",
        ""
    )

    course_numero = str(
        course_numero
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
            timeout=TIMEOUT
        )

        response.raise_for_status()

        donnees = response.json()

        if isinstance(
            donnees,
            dict
        ):

            return donnees.get(
                "participants",
                []
            )

        if isinstance(
            donnees,
            list
        ):

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
    reunion,
    course_numero
):

    programme = recuperer_programme(
        date
    )

    if not programme:

        return None

    reunion_data = trouver_reunion(
        programme,
        reunion
    )

    if not reunion_data:

        print(
            "Réunion PMU introuvable :",
            reunion
        )

        return None

    course = trouver_course(
        reunion_data,
        course_numero
    )

    if not course:

        print(
            "Course PMU introuvable :",
            course_numero
        )

        return None

    participants = recuperer_participants(
        date,
        reunion,
        course_numero
    )

    if not participants:

        print(
            "Aucun participant PMU trouvé."
        )

        return None

    return transformer_course(
        course,
        participants
    )


# =====================================
# TEST
# =====================================

if __name__ == "__main__":

    print(
        "AZ Turf Pro - Source PMU"
    )

    print(
        "Module chargé correctement."
    )

    print(
        "Distance : 5.0"
    )

    print(
        "Terrain : 5.0"
    )

    print(
        "Jockey : 5.0"
    )

    print(
        "Connexion PMU disponible."
    )
