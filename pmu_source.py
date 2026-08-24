# =====================================
# AZ TURF PRO
# SOURCE PMU
# Connexion aux donnees PMU reelles
# =====================================
# VERSION COMPLETE ET FIABILISEE
# Compatible avec api.py : charger_course_pmu(date, reunion=None, course_numero=None)

import math
import os
import json
import requests
from datetime import datetime

from modules.cotes_history import analyser_tendances_cotes


# =====================================
# CONFIGURATION
# =====================================

PMU_BASE_URLS = [
    # Client 1 is the long-standing public JSON endpoint used by PMU integrations.
    ("https://online.turfinfo.api.pmu.fr/rest/client/1/programme", "INTERNET"),
    # Offline client 7 is kept as a secondary source when online is unavailable.
    ("https://offline.turfinfo.api.pmu.fr/rest/client/7/programme", "OFFLINE"),
    # Existing endpoint retained as a final compatibility fallback.
    ("https://turfinfo.api.prd.pmutech.fr/rest/client/61/programme", "INTERNET"),
]

TIMEOUT = 12
LAST_PMU_DIAGNOSTIC = {"ok": False, "erreurs": []}
PARTANTS_MINIMUM_QUINTE = 10

DOSSIER_DONNEES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
FICHIER_COTES_MATIN = os.path.join(DOSSIER_DONNEES, "cotes_matin.json")


def _charger_cache_cotes_matin():
    try:
        with open(FICHIER_COTES_MATIN, "r", encoding="utf-8") as fichier:
            return json.load(fichier)
    except (FileNotFoundError, ValueError):
        return {}


def _sauvegarder_cache_cotes_matin(cache):
    try:
        os.makedirs(DOSSIER_DONNEES, exist_ok=True)
        with open(FICHIER_COTES_MATIN, "w", encoding="utf-8") as fichier:
            json.dump(cache, fichier, ensure_ascii=False)
    except OSError:
        pass


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
        mois_candidat = texte[4:6]
        jour_candidat = texte[6:8]
        if (
            mois_candidat.isdigit()
            and jour_candidat.isdigit()
            and 1 <= int(mois_candidat) <= 12
            and 1 <= int(jour_candidat) <= 31
        ):
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
    cache_cotes_matin=None,
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

    cote_matin_brute = None
    if cache_cotes_matin is not None and numero is not None:
        cle_cheval = str(numero)
        if cle_cheval in cache_cotes_matin:
            cote_matin_brute = cache_cotes_matin[cle_cheval]
        elif cote_brute is not None:
            cache_cotes_matin[cle_cheval] = cote_brute
            cote_matin_brute = cote_brute

    nombre_courses = obtenir_nombre_courses(participant)
    experience = calculer_experience(nombre_courses)

    distance_score = 5.0
    terrain_score = 5.0
    jockey_score = 5.0

    terrain_info = obtenir_terrain(course)

    # Données additives destinées à l'analyse contextuelle Premium.
    deferre = (
        participant.get("deferre")
        or participant.get("deferrage")
        or participant.get("ferrure")
        or participant.get("ferrage")
        or participant.get("shoeing")
        or ""
    )
    corde = (
        participant.get("corde")
        or participant.get("numeroCorde")
        or participant.get("stall")
        or ""
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
        "cote_matin_brute": cote_matin_brute,
        "gains_carriere_brute": obtenir_gains(participant),
        "musique_brute": musique,
        "deferre": deferre,
        "corde": corde,
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

    cle_course = f"{course.get('date') or course.get('dateCourse') or ''}_R{course.get('numReunion') or course.get('reunion') or ''}C{course.get('numOrdre') or course.get('numCourse') or course.get('numero') or ''}"
    cache_complet = _charger_cache_cotes_matin()
    cache_du_jour = cache_complet.setdefault(cle_course, {})

    chevaux = []

    for participant in participants:
        cheval = transformer_participant(
            participant,
            course,
            scores_cotes,
            scores_gains,
            cache_du_jour,
        )

        if cheval.get("numero") is not None:
            chevaux.append(cheval)

    _sauvegarder_cache_cotes_matin(cache_complet)

    if not chevaux:
        return None

    tendances = analyser_tendances_cotes({"chevaux": chevaux})
    tendances_par_numero = {
        str(item.get("numero")): item
        for item in tendances.get("resultats", [])
    }
    for cheval in chevaux:
        info_tendance = tendances_par_numero.get(str(cheval.get("numero")), {})
        cheval["tendance_cote"] = info_tendance.get("tendance", "STABLE")
        cheval["signal_marche"] = info_tendance.get("signal", "NEUTRE")
        cheval["variation_cote_pct"] = info_tendance.get("variation_pct", 0.0)

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

    type_depart = (
        course.get("type_depart")
        or course.get("typeDepart")
        or course.get("mode_depart")
        or course.get("modeDepart")
        or course.get("typeDepartLibelle")
        or ""
    )

    conditions = (
        course.get("conditions")
        or course.get("conditionCourse")
        or course.get("conditionsCourse")
        or course.get("libelleConditions")
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
        "type_depart": type_depart,
        "conditions": conditions,
        "chevaux": chevaux,
        "non_partants": non_partants,
        "plus_joues": [],
        "source_plus_joues": "non disponible via API PMU",
        "source": "pmu_live",
    }


# =====================================
# RECUPERATION PROGRAMME
# =====================================

def recuperer_programme(date, reunion=None):
    """Récupère le programme PMU réel avec plusieurs clients compatibles.

    Le fallback entre clients ne change pas le format attendu par le reste du
    moteur. Aucun fichier local n'est utilisé ici : si PMU est indisponible,
    l'appelant conserve son comportement existant de fallback.
    """
    global LAST_PMU_DIAGNOSTIC
    date = normaliser_date(date)
    erreurs = []

    for base_url, specialisation in PMU_BASE_URLS:
        if reunion is None:
            url = f"{base_url}/{date}"
        else:
            reunion_numero = str(reunion).upper().replace("R", "").strip()
            if not reunion_numero.isdigit():
                continue
            url = f"{base_url}/{date}/R{reunion_numero}"

        try:
            response = requests.get(
                url,
                params={"meteo": "true", "specialisation": specialisation},
                timeout=TIMEOUT,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "AZ-Turf-Pro/1.0",
                },
            )
            if response.status_code != 200:
                erreurs.append({"url": response.url, "status": response.status_code})
                continue

            donnees = response.json()
            if isinstance(donnees, dict):
                LAST_PMU_DIAGNOSTIC = {
                    "ok": True,
                    "url": response.url,
                    "status": response.status_code,
                    "client": base_url.split("/client/")[-1].split("/")[0],
                    "date": date,
                }
                return donnees

            erreurs.append({"url": response.url, "status": response.status_code, "erreur": "Réponse JSON non objet"})
        except requests.RequestException as erreur:
            erreurs.append({"url": url, "erreur": str(erreur)})
        except (ValueError, TypeError) as erreur:
            erreurs.append({"url": url, "erreur": f"JSON invalide: {erreur}"})
        except Exception as erreur:
            erreurs.append({"url": url, "erreur": str(erreur)})

    LAST_PMU_DIAGNOSTIC = {"ok": False, "date": date, "erreurs": erreurs}
    return None


# =====================================
# RECHERCHE REUNION ET COURSE
# =====================================

def trouver_reunion(programme, reunion):
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

    reunions = programme.get("reunions") or programme.get("programme", {}).get("reunions", [])
    if isinstance(reunions, list):
        for r_item in reunions:
            if isinstance(r_item, dict):
                r_num = str(r_item.get("numOfficiel") or r_item.get("numReunion") or r_item.get("numero") or "").strip()
                if r_num == numero_recherche:
                    return r_item

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
    reunion_numero = str(reunion).upper().replace("R", "").strip()
    course_numero = str(course_numero).upper().replace("C", "").strip()
    if not reunion_numero.isdigit() or not course_numero.isdigit():
        return []

    for base_url, specialisation in PMU_BASE_URLS:
        url = f"{base_url}/{date}/R{reunion_numero}/C{course_numero}/participants"
        try:
            response = requests.get(
                url,
                params={"specialisation": specialisation},
                timeout=TIMEOUT,
                headers={"Accept": "application/json", "User-Agent": "AZ-Turf-Pro/1.0"},
            )
            if response.status_code != 200:
                continue
            donnees = response.json()
            if isinstance(donnees, dict) and isinstance(donnees.get("participants"), list):
                return donnees["participants"]
            if isinstance(donnees, list):
                return donnees
        except Exception:
            continue
    return []


# =====================================
# DETECTION QUINTE+
# =====================================

def _contient_quinte(course):
    """Indique si une course PMU est un Quinté+, d'après les paris proposés."""
    if not isinstance(course, dict):
        return False

    paris = course.get("paris") or course.get("parisEnLigne") or []
    if isinstance(paris, list):
        for pari in paris:
            if isinstance(pari, dict):
                type_pari = str(pari.get("typePari") or pari.get("type") or "").upper()
            else:
                type_pari = str(pari).upper()
            if "QUINTE" in type_pari:
                return True

    texte = str(
        course.get("specialite")
        or course.get("libelleCourt")
        or course.get("libelle")
        or ""
    ).upper()

    return "QUINTE" in texte


# =====================================
# RECHERCHE QUINTE+ DU JOUR
# =====================================

def trouver_quinte_du_jour(date):
    """
    Parcourt les reunions et retourne (programme, reunion, course).
    Inclus un systeme de secours (fallback R1C1) si aucun QuintÃ©+ n'est Ã©tiquetÃ©.
    """
    date = normaliser_date(date)

    # 1. Essai via le programme global du jour
    prog_global = recuperer_programme(date)
    if prog_global:
        reunions = prog_global.get("reunions") or prog_global.get("programme", {}).get("reunions", [])
        if isinstance(reunions, list):
            for reunion_obj in reunions:
                if not isinstance(reunion_obj, dict):
                    continue
                num_r = reunion_obj.get("numOfficiel") or reunion_obj.get("numReunion") or reunion_obj.get("numero")
                code_r = f"R{num_r}" if num_r else None
                courses = reunion_obj.get("courses", [])
                if isinstance(courses, list):
                    for course in courses:
                        if isinstance(course, dict) and _contient_quinte(course):
                            return prog_global, code_r or "R1", course

    # 2. Parcours individuel R1 Ã  R12
    premiere_course_fallback = None

    for numero_reunion in range(1, 13):
        reunion = f"R{numero_reunion}"
        programme = recuperer_programme(date, reunion)

        if not programme:
            continue

        reunion_data = trouver_reunion(programme, reunion)
        if not reunion_data:
            continue

        courses = reunion_data.get("courses", [])
        if not isinstance(courses, list):
            continue

        for course in courses:
            if not isinstance(course, dict):
                continue

            # On garde une reference sur la premiere course valide pour le secours
            if premiere_course_fallback is None:
                premiere_course_fallback = (programme, reunion, course)

            if _contient_quinte(course):
                return programme, reunion, course

    # 3. Aucun Quinté explicite : ne pas inventer une course cible.
    # Le fallback local de api.py reste disponible et inchangé.
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
