# =====================================
# AZ TURF PRO
# SOURCE PMU
# Connexion aux donnees PMU reelles
# =====================================
# VERSION COMPLETE ET FIABILISEE
# Compatible avec api.py : charger_course_pmu(date, reunion=None, course_numero=None)

import math
import requests
from datetime import datetime


# =====================================
# CONFIGURATION
# =====================================

PMU_BASE_URLS = [
    "https://online.turfinfo.api.pmu.fr/rest/client/61/programme",
    "https://offline.turfinfo.api.pmu.fr/rest/client/61/programme",
    "https://turfinfo.api.prd.pmutech.fr/rest/client/61/programme",
]

# Compatibilite avec l'ancien nom utilise ailleurs dans le projet.
PMU_BASE_URL = PMU_BASE_URLS[0]
TIMEOUT = 15

_LAST_PMU_DIAGNOSTIC = {}
PARTANTS_MINIMUM_QUINTE = 10


# =====================================
# OUTILS ET NORMALISATION
# =====================================

def normaliser_date(date_val):
    """
    Normalise n'importe quel format de date (YYYY-MM-DD, DD/MM/YYYY, datetime, etc.)
    vers le format DDMMYYYY attendu par l'API PMU.
    """
    if not date_val:
        return datetime.now().strftime("%d%m%Y")

    if hasattr(date_val, "strftime"):
        return date_val.strftime("%d%m%Y")

    texte = str(date_val).replace("-", "").replace("/", "").replace(" ", "").strip()

    # Si format YYYYMMDD (ex: 20260813) -> Convertir en DDMMYYYY (13082026)
    if len(texte) == 8 and (texte.startswith("20") or texte.startswith("19")):
        return f"{texte[6:8]}{texte[4:6]}{texte[0:4]}"

    return texte


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
    moyenne = sum(recentes) / len(recentes)
    return limiter_score(10.0 - moyenne)


# =====================================
# REGULARITE
# =====================================

def calculer_regularite(positions):
    if len(positions) < 2:
        return 5.0

    recentes = positions[:8]
    moyenne = sum(recentes) / len(recentes)

    variance = sum(
        (position - moyenne) ** 2
        for position in recentes
    ) / len(recentes)

    ecart_type = math.sqrt(variance)
    return limiter_score(10.0 - ecart_type)


# =====================================
# EXPERIENCE
# =====================================

def calculer_experience(nombre_courses):
    try:
        nombre_courses = float(nombre_courses or 0)
    except (TypeError, ValueError):
        nombre_courses = 0

    return limiter_score(nombre_courses / 10.0)


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

    score = ((valeur - minimum) / (maximum - minimum)) * 10.0
    return limiter_score(score)


# =====================================
# EXTRACTION COTE
# =====================================

def _extraire_nom_personne(valeur):
    if isinstance(valeur, str):
        return valeur.strip()

    if isinstance(valeur, dict):
        for cle in (
            "nom",
            "nomComplet",
            "libelle",
            "identite",
            "nomPrenom",
        ):
            valeur_nom = valeur.get(cle)
            if valeur_nom:
                return str(valeur_nom).strip()

        prenom = valeur.get("prenom") or ""
        nom = valeur.get("nom") or ""
        resultat = f"{prenom} {nom}".strip()
        if resultat:
            return resultat

    return ""


def _extraire_valeur_numerique(valeur):
    if isinstance(valeur, (int, float)):
        return float(valeur)

    if isinstance(valeur, dict):
        for cle in (
            "rapport",
            "rapportDirect",
            "rapportProbable",
            "cote",
            "valeur",
        ):
            resultat = _extraire_valeur_numerique(valeur.get(cle))
            if resultat is not None:
                return resultat

    if isinstance(valeur, str):
        texte = valeur.replace(",", ".").strip()
        try:
            return float(texte)
        except (TypeError, ValueError):
            return None

    return None


def obtenir_cote(participant):
    for cle in (
        "dernierRapportDirect",
        "rapportDirect",
        "dernierRapport",
        "coteProbable",
        "cote",
        "rapport",
    ):
        valeur = _extraire_valeur_numerique(
            participant.get(cle)
        )
        if valeur is not None and valeur > 0:
            return valeur

    return None


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
        numero = participant.get("numPmu")
        cote = obtenir_cote(participant)

        if cote is None:
            resultats[numero] = {"score": 5.0, "cote": None}
            continue

        if maximum == minimum:
            score = 5.0
        else:
            score = ((maximum - cote) / (maximum - minimum)) * 10.0

        resultats[numero] = {
            "score": limiter_score(score),
            "cote": cote,
        }

    return resultats


# =====================================
# SCORES GAINS
# =====================================

def obtenir_gains(participant):
    gains_data = participant.get("gainsParticipant", {})

    if not isinstance(gains_data, dict):
        gains_data = {}

    gains = gains_data.get("gainsCarriere", 0)

    try:
        return float(gains or 0)
    except (TypeError, ValueError):
        return 0.0


def calculer_scores_gains(participants):
    valeurs = [obtenir_gains(p) for p in participants]

    if not valeurs:
        return {}

    minimum = min(valeurs)
    maximum = max(valeurs)
    resultats = {}

    for participant in participants:
        numero = participant.get("numPmu")
        gains = obtenir_gains(participant)

        resultats[numero] = normaliser(
            gains,
            minimum,
            maximum,
        )

    return resultats


# =====================================
# TERRAIN
# =====================================

def obtenir_terrain(course):
    penetrometre = course.get("penetrometre", {})

    if isinstance(penetrometre, dict):
        return penetrometre.get("intitule", "Non disponible")

    return "Non disponible"


# =====================================
# EXTRACTION NOMBRE DE COURSES
# =====================================

def obtenir_nombre_courses(participant):
    for cle in (
        "nombreCourses",
        "nombreCoursesCarriere",
        "nbCourses",
    ):
        valeur = participant.get(cle)
        if valeur not in (None, ""):
            return valeur

    return 0


# =====================================
# TRANSFORMATION PARTICIPANT
# =====================================

def transformer_participant(
    participant,
    course,
    scores_cotes,
    scores_gains,
):
    numero = participant.get("numPmu")
    nom = participant.get("nom", "")
    age = participant.get("age", 0)
    sexe = participant.get("sexe", "")

    if str(sexe).upper() == "HONGRES":
        sexe = "M"

    jockey = _extraire_nom_personne(
        participant.get("driver")
        or participant.get("jockey")
        or participant.get("pilote")
        or participant.get("conducteur")
    )

    entraineur = _extraire_nom_personne(
        participant.get("entraineur")
        or participant.get("trainer")
        or participant.get("entraineurNom")
    )

    musique = participant.get("musique", "")
    performances = extraire_positions(musique)

    forme = calculer_forme(performances)
    regularite = calculer_regularite(performances)

    gains = scores_gains.get(numero, 5.0)

    cote_data = scores_cotes.get(numero, {})
    cote = cote_data.get("score", 5.0)
    cote_brute = cote_data.get("cote")

    nombre_courses = obtenir_nombre_courses(participant)
    experience = calculer_experience(nombre_courses)

    distance_score = 5.0
    terrain_score = 5.0
    jockey_score = 5.0

    terrain_info = obtenir_terrain(course)

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
        "gains_carriere_brute": obtenir_gains(participant),
        "musique_brute": musique,
    }


# =====================================
# EXTRACTION INFOS COURSE
# =====================================

def obtenir_hippodrome(course):
    for cle in (
        "hippodrome",
        "hippodromeLibelle",
        "hippodromeNom",
        "lieu",
        "site",
    ):
        valeur = course.get(cle, "")

        if isinstance(valeur, dict):
            valeur = (
                valeur.get("libelleLong")
                or valeur.get("libelleCourt")
                or valeur.get("libelle")
                or valeur.get("nom")
                or valeur.get("label")
                or ""
            )

        if valeur:
            return str(valeur).strip()

    return "Non disponible"


def obtenir_discipline(course):
    discipline = course.get("discipline", "")

    if isinstance(discipline, dict):
        return (
            discipline.get("libelle")
            or discipline.get("nom")
            or ""
        )

    return discipline


# =====================================
# TRANSFORMATION COURSE
# =====================================

def extraire_non_partants(course, participants):
    non_partants = set()

    for participant in participants:
        if not isinstance(participant, dict):
            continue

        statut = str(
            participant.get("statut")
            or participant.get("statutParticipant")
            or participant.get("status")
            or participant.get("statutPmu")
            or ""
        ).upper().replace("-", "_").replace(" ", "_")

        indicateur_np = (
            participant.get("nonPartant") is True
            or participant.get("non_partant") is True
            or participant.get("nonPartant") == 1
            or participant.get("non_partant") == 1
        )

        if indicateur_np or "NON_PARTANT" in statut or statut in {"NP", "N_P", "NONPARTANT"}:
            numero = participant.get("numPmu") or participant.get("numero")
            if numero is not None:
                non_partants.add(numero)

    for incident in course.get("incidents", []) or []:
        if (
            isinstance(incident, dict)
            and str(incident.get("type", "")).upper().replace("-", "_") in {"NON_PARTANT", "NONPARTANT", "NP"}
        ):
            for numero in incident.get("numeroParticipants", []) or []:
                non_partants.add(numero)

    return sorted(non_partants)


def transformer_course(course, participants):
    if not participants:
        return None

    scores_cotes = calculer_scores_cotes(participants)
    scores_gains = calculer_scores_gains(participants)

    non_partants = extraire_non_partants(course, participants)

    chevaux = []

    for participant in participants:
        cheval = transformer_participant(
            participant,
            course,
            scores_cotes,
            scores_gains,
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

    heure_depart = (
        course.get("heureDepart")
        or course.get("heureDepartCourse")
        or course.get("heure")
        or course.get("heureDepartPrevue")
        or ""
    )

    return {
        "course": course.get(
            "libelle",
            course.get("nom", "Course"),
        ),
        "date": date_course,
        "reunion": reunion,
        "course_numero": course_numero,
        "heure_depart": heure_depart,
        "horaires": {"depart": heure_depart, "arret_des_jeux": ""},
        "hippodrome": obtenir_hippodrome(course),
        "discipline": obtenir_discipline(course),
        "distance_course": (
            course.get("distance")
            or course.get("distanceCourse")
            or course.get("distanceMetres")
            or ""
        ),
        "allocation": course.get(
            "montantPrix",
            course.get("allocation", ""),
        ),
        "chevaux": chevaux,
        "non_partants": non_partants,
        "plus_joues": [],
        "source_plus_joues": "non disponible via API PMU",
        "source": "pmu_live",
    }


# =====================================
# RECUPERATION PROGRAMME
# =====================================

def _extraire_reunions(programme):
    if not isinstance(programme, dict):
        return []
    candidats = [
        programme.get("reunions"),
        (programme.get("programme") or {}).get("reunions") if isinstance(programme.get("programme"), dict) else None,
        (programme.get("programmeJour") or {}).get("reunions") if isinstance(programme.get("programmeJour"), dict) else None,
    ]
    for value in candidats:
        if isinstance(value, list):
            return value
    return []


def _requete_pmu(path, params=None):
    global _LAST_PMU_DIAGNOSTIC
    params = params or {"specialisation": "INTERNET"}
    headers = {
        "Accept": "application/json",
        "User-Agent": "AZ-Turf-Pro/1.0",
        "Connection": "close",
    }
    erreurs = []
    for base in PMU_BASE_URLS:
        url = f"{base}/{path.lstrip('/')}"
        try:
            response = requests.get(url, params=params, timeout=TIMEOUT, headers=headers)
            status = response.status_code
            if status != 200:
                erreurs.append({"url": url, "status": status})
                continue
            donnees = response.json()
            if not isinstance(donnees, (dict, list)):
                erreurs.append({"url": url, "status": status, "erreur": "JSON inattendu"})
                continue
            _LAST_PMU_DIAGNOSTIC = {"ok": True, "url": url, "status": status, "erreurs": erreurs}
            return donnees
        except Exception as erreur:
            erreurs.append({"url": url, "erreur": f"{type(erreur).__name__}: {erreur}"})
    _LAST_PMU_DIAGNOSTIC = {"ok": False, "erreurs": erreurs}
    return None


def recuperer_programme(date, reunion=None):
    date = normaliser_date(date)
    path = date
    if reunion is not None:
        reunion_numero = str(reunion).upper().replace("R", "").strip()
        if not reunion_numero.isdigit():
            return None
        path = f"{date}/R{reunion_numero}"
    donnees = _requete_pmu(path)
    return donnees if isinstance(donnees, dict) else None


# =====================================
# RECHERCHE REUNION ET COURSE
# =====================================

def trouver_reunion(programme, reunion):
    if not isinstance(programme, dict):
        return None
    code = str(reunion or "").upper().strip()
    if not code:
        return None
    numero_recherche = code[1:] if code.startswith("R") else code
    numero = str(programme.get("numOfficiel") or programme.get("numReunion") or programme.get("numero") or "").strip()
    if numero == numero_recherche and isinstance(programme.get("courses"), list):
        return programme
    for item in _extraire_reunions(programme):
        if not isinstance(item, dict):
            continue
        num = str(item.get("numOfficiel") or item.get("numReunion") or item.get("numero") or "").strip()
        if num == numero_recherche:
            return item
    if isinstance(programme.get("courses"), list):
        return programme
    return None


def trouver_course(reunion_data, course_numero):
    if not reunion_data:
        return None

    courses = reunion_data.get("courses", [])

    if not isinstance(courses, list):
        return None

    numero_recherche = str(course_numero or "").upper().strip()

    if numero_recherche.startswith("C"):
        numero_recherche = numero_recherche[1:]

    for course in courses:
        if not isinstance(course, dict):
            continue

        numero = (
            course.get("numOrdre")
            or course.get("numCourse")
            or course.get("numero")
        )

        if str(numero).strip() == numero_recherche:
            return course

    return None


# =====================================
# RECUPERATION PARTICIPANTS
# =====================================

def recuperer_participants(date, reunion, course_numero):
    if reunion is None or course_numero is None:
        return []
    date = normaliser_date(date)
    r = str(reunion).upper().replace("R", "").strip()
    c = str(course_numero).upper().replace("C", "").strip()
    if not r.isdigit() or not c.isdigit():
        return []
    donnees = _requete_pmu(f"{date}/R{r}/C{c}/participants")
    if isinstance(donnees, list):
        return donnees
    if isinstance(donnees, dict):
        for cle in ("participants", "listeParticipants", "partants"):
            if isinstance(donnees.get(cle), list):
                return donnees[cle]
    return []


# =====================================
# DETECTION QUINTE+ FIABILISEE
# =====================================

def _nombre_partants(course):
    if not isinstance(course, dict):
        return 0

    for cle in (
        "nombreDeclaresPartants",
        "nombrePartants",
        "nbPartants",
    ):
        valeur = course.get(cle)
        try:
            if valeur not in (None, ""):
                return int(valeur)
        except (TypeError, ValueError):
            pass

    participants = course.get("participants")
    if isinstance(participants, list):
        return len(participants)

    return 0


def _texte_contient_quinte(valeur):
    if valeur is None:
        return False

    if isinstance(valeur, dict):
        for cle, contenu in valeur.items():
            cle_texte = str(cle).upper()
            if "QUINTE" in cle_texte or "Q5" in cle_texte or "5PLUS" in cle_texte:
                return True
            if isinstance(contenu, (str, list, dict)):
                if _texte_contient_quinte(contenu):
                    return True
        return False

    if isinstance(valeur, list):
        return any(_texte_contient_quinte(item) for item in valeur)

    texte = str(valeur).upper()
    return "QUINTE" in texte or "Q5" in texte or "5PLUS" in texte or "E_QUINTE" in texte


def _extraire_types_paris(course):
    if not isinstance(course, dict):
        return []

    for cle in (
        "paris",
        "parisPMU",
        "typesParis",
        "listePari",
    ):
        valeur = course.get(cle)
        if isinstance(valeur, list):
            return valeur

    return []


def _contient_quinte(course):
    """
    Detection securisee du QuintÃ©+ :
    1. Booleens et drapeaux explicites (quintePlus, evenement, grandPrix)
    2. Types de paris
    3. Nom et libelle de la course
    Ne renvoie PAS False prematurely.
    """
    if not isinstance(course, dict):
        return False

    # 1. Champs booleens directs
    for flag in ("quintePlus", "quinte", "evenement", "grandPrix", "isQuinte"):
        if course.get(flag) is True:
            return True

    # 2. Recherche dans les types de paris
    types_paris = _extraire_types_paris(course)
    if types_paris:
        for pari in types_paris:
            if _texte_contient_quinte(pari):
                return True

    # 3. Nombre de partants minimum
    nombre_partants = _nombre_partants(course)
    if nombre_partants > 0 and nombre_partants < PARTANTS_MINIMUM_QUINTE:
        return False

    # 4. Libelles de la course
    champs_identification = (
        "libelle",
        "nom",
        "libelleCourt",
        "libelleLong",
        "typeCourse",
        "conditionModifiee",
        "statutEvenement",
    )

    for cle in champs_identification:
        valeur = course.get(cle)
        if isinstance(valeur, str) and _texte_contient_quinte(valeur):
            return True

    return False


# =====================================
# RECHERCHE QUINTE+ DU JOUR
# =====================================

def trouver_quinte_du_jour(date):
    date = normaliser_date(date)
    prog_global = recuperer_programme(date)
    if not prog_global:
        return None, None, None

    # API PMU client/61 renvoie normalement programme.reunions.
    reunions = _extraire_reunions(prog_global)
    for reunion_obj in reunions:
        if not isinstance(reunion_obj, dict):
            continue
        num_r = reunion_obj.get("numOfficiel") or reunion_obj.get("numReunion") or reunion_obj.get("numero")
        code_r = f"R{num_r}" if num_r is not None else None
        courses = reunion_obj.get("courses", [])
        if not isinstance(courses, list):
            continue
        for course in courses:
            if isinstance(course, dict) and _contient_quinte(course):
                return prog_global, code_r, course

    # Si le drapeau Quinté+ n'est pas fourni, on choisit explicitement
    # la première course avec au moins le minimum de partants, mais
    # uniquement dans le programme LIVE du jour.
    for reunion_obj in reunions:
        if not isinstance(reunion_obj, dict):
            continue
        num_r = reunion_obj.get("numOfficiel") or reunion_obj.get("numReunion") or reunion_obj.get("numero")
        code_r = f"R{num_r}" if num_r is not None else None
        for course in reunion_obj.get("courses", []) or []:
            if isinstance(course, dict) and _nombre_partants(course) >= PARTANTS_MINIMUM_QUINTE:
                return prog_global, code_r, course

    return None, None, None


# =====================================
# CHARGEMENT COURSE PMU
# =====================================

def charger_course_pmu(
    date=None,
    reunion=None,
    course_numero=None,
):
    try:
        date = normaliser_date(date)

        # MODE AUTOMATIQUE QUINTE+
        if reunion is None and course_numero is None:
            programme, reunion_trouvee, course = trouver_quinte_du_jour(date)

            if not course:
                print("Aucun QuintÃ©+ PMU trouve pour", date)
                return None

            reunion = reunion_trouvee
            course_numero = (
                course.get("numOrdre")
                or course.get("numCourse")
                or course.get("numero")
            )

        # MODE COURSE PRECISE
        else:
            if reunion is None or course_numero is None:
                return None

            programme = recuperer_programme(date, reunion)
            if not programme:
                return None

            reunion_data = trouver_reunion(programme, reunion)
            if not reunion_data:
                print("Reunion PMU introuvable :", reunion)
                return None

            course = trouver_course(reunion_data, course_numero)
            if not course:
                print("Course PMU introuvable :", course_numero)
                return None

        # RECUPERATION PARTICIPANTS
        participants = recuperer_participants(date, reunion, course_numero)

        if not participants:
            print("Aucun participant PMU trouve pour", reunion, course_numero)
            return None

        # TRANSFORMATION
        resultat = transformer_course(course, participants)

        if not resultat:
            return None

        resultat["reunion"] = reunion
        resultat["course_numero"] = course_numero

        if not resultat.get("date"):
            resultat["date"] = date

        return resultat

    except Exception as erreur:
        print("Erreur chargement course PMU :", erreur)
        return None


# =====================================
# ARRIVEE REELLE D'UNE COURSE PASSEE
# =====================================

def recuperer_arrivee_pmu(date, reunion, course_numero):
    date = normaliser_date(date)
    programme = recuperer_programme(date, reunion)

    if not programme:
        return None

    reunion_data = trouver_reunion(programme, reunion)
    if not reunion_data:
        return None

    course = trouver_course(reunion_data, course_numero)
    if not course:
        return None

    ordre_brut = course.get("ordreArrivee")
    if not ordre_brut:
        return None

    arrivee = []
    for groupe in ordre_brut:
        if isinstance(groupe, list):
            arrivee.extend(groupe)
        else:
            arrivee.append(groupe)

    return arrivee


def diagnostic_pmu():
    return dict(_LAST_PMU_DIAGNOSTIC)


# =====================================
# TEST
# =====================================

if __name__ == "__main__":
    print("AZ Turf Pro - Source PMU (CorrigÃ©)")
    print("Module chargÃ© correctement.")

    date_test = datetime.now().strftime("%d%m%Y")
    resultat = charger_course_pmu(date_test)

    if resultat:
        print("âœ… Connexion PMU disponible !")
        print("Course trouvÃ©e :", resultat.get("course"))
        print("RÃ©union/Course :", resultat.get("reunion"), "C" + str(resultat.get("course_numero")))
        print("Partants :", len(resultat.get("chevaux", [])))
    else:
        print("âŒ PMU indisponible ou aucune course trouvÃ©e.")
