
hier 9:38

AZ-Turf-Pro-main (4).zip
Archive zip
Examine ce dossier tout entier et fais le point de ton analyse sans toucher au fonctionnement déjà mise en place 


AZ-Turf-Pro-main (4)(1).zip
Archive zip


response_1787142309297.json
Fichier


response_1787143153582.json
Fichier


pmu_source.py
Python


response_1787144740462.json
Fichier


response_1787145585467.json
Fichier


AZ-Turf-Pro-main (7).zip
Archive zip


AZ-Turf-Pro-main (6).zip
Archive zip


pmu_source (3).py
Python


AZ-Turf-Pro-main (2).zip
Archive zip
Je crois que les bons fichiers se trouve dans ce zip

aujourd’hui 7:46

accueil.js
JavaScript

index.html
Fichier
Examine ces fichiers voir pourquoi l'accueil n'affiche pas 


AZ-Turf-Pro-main (8).zip
Archive zip


api.py
Python

main.py
Python


api(1).py
Python


pmu_source(2).py
Python

Oui. Et là il faut distinguer deux problèmes :

La structure de l'accueil ne s'affiche pas.

La course PMU ne remonte pas.

Les logs que tu viens de donner montrent seulement que /api/analyse retourne 503. Ils ne prouvent pas à eux seuls que la structure HTML/CSS est cassée.

Puisque les logs précédents donnaient :

/style.css       200
/accueil.js      200
/tri-partants.js 200
/modules-az.css  200
le serveur sert maintenant correctement les fichiers frontend.

Pour la structure
Je ne veux surtout pas toucher encore à style.css ou réécrire l'accueil. Il faut vérifier ce que accueil.js fait quand /api/analyse retourne 503.

Si le JavaScript attend obligatoirement une réponse 200 contenant une course, il peut laisser les cartes/tableaux vides lorsque l'API renvoie :

{"detail":"Aucune donnée de course disponible actuellement."}
Donc le problème de structure peut être une conséquence du 503, et non un problème CSS.

Ne remplace aucun fichier pour l'instant.

Le prochain contrôle doit porter sur accueil.js, précisément sur le traitement de l'erreur /api/analyse. On doit faire en sorte que la structure de l'accueil reste visible même lorsque les données PMU sont indisponibles, sans remettre la course du 24 juillet.


On a changé config.py , la date est passée au 24 juillet et on a touché a api.py plus rien n'affiche et tu trouves que le problème est ailleurs, comment tu veux que le problème soit ailleurs 

Tu as raison sur le raisonnement. On ne doit pas déplacer le problème vers accueil.js sans preuve.

La chronologie que tu donnes est déterminante :

Avant nos modifications, l'application affichait au moins la structure.

Nous avons modifié config.py pour corriger EXPORT_DIR.

Ensuite, la course affichée est devenue celle du 24 juillet.

Nous avons modifié api.py pour supprimer le fallback courses.json.

Depuis cette modification, plus rien ne s'affiche.

Maintenant /api/analyse renvoie 503, avec :

Aucun Quinté+ PMU trouvé pour 26202008
Aucune course PMU disponible pour la date demandee.
Donc oui : la priorité est de revenir sur les modifications que nous avons faites à config.py et surtout api.py, et de comparer avec les versions originales du ZIP. Ce n'est pas le moment de modifier encore accueil.js.

Et je reconnais une erreur de méthode : j'ai supprimé le fallback dans api.py avant d'avoir réparé la source PMU. Cela a transformé un affichage incorrect du 24 juillet en absence totale de données. Ce n'était pas une bonne séquence de correction.

Ce que je propose maintenant
On arrête les modifications en chaîne.

Étape 1 : reprendre le api.py original du ZIP.

Étape 2 : reprendre le config.py original et ajouter seulement ce qui était nécessaire pour EXPORT_DIR.

Étape 3 : comparer ces fichiers avec ceux actuellement modifiés.

Étape 4 : déterminer exactement quelle modification a cassé l'affichage.

Étape 5 : seulement après, corriger la date PMU 26202008.

Je ne toucherai ni au CSS, ni à l'accueil, ni à engine.py, ni au chatbot/backtest pendant cette vérification.

Si les fichiers du ZIP que tu as fourni sont toujours accessibles dans cette conversation, je peux faire cette comparaison directement et te dire ligne par ligne ce qui a changé et quel fichier doit être restauré/corrigé.


Envoie les fichiers originaux 

Oui. Voici les fichiers originaux extraits directement du ZIP AZ-Turf-Pro-main (8).zip, sans correction ni modification :

config_original.py

api_original.py

main_original.py

pmu_source_original.py

Ce sont les versions avant nos modifications.

Ne remplace pas encore les quatre fichiers en même temps. On peut maintenant restaurer proprement, fichier par fichier, en commençant par celui qui a réellement provoqué la régression. 


config_original.py
Code


api_original.py
Code


main_original.py
Code


pmu_source_original.py
Code

Afficher moins

Aucun fichier choisi
Bibliothèque
/
pmu_source_original.py


# =====================================
# AZ TURF PRO
# SOURCE PMU
# Connexion aux donnees PMU reelles
# =====================================
# VERSION COMPLETE - detection QuintÃ©+ fiabilisee
# Compatible avec api.py : charger_course_pmu(date, reunion=None, course_numero=None)

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
PARTANTS_MINIMUM_QUINTE = 10


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
    """
    Normalise les champs jockey/entraineur PMU.
    L'API peut retourner une chaÃ®ne ou un objet.
    """
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
    """
    Extrait la cote/rapport brut quel que soit le format courant
    rencontrÃ© dans la rÃ©ponse PMU.
    """
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
    """
    Identifie les chevaux declares non-partants, a partir des deux
    sources possibles de l'API PMU (observees dans les vraies
    reponses) :
    1. Le statut individuel de chaque participant
       (participant["statut"] == "NON_PARTANT")
    2. La liste d'incidents au niveau course
       (course["incidents"] avec type == "NON_PARTANT")
    Combine les deux sans doublon. Retourne une liste triee de
    numeros.
    """

    non_partants = set()

    for participant in participants:
        if not isinstance(participant, dict):
            continue

        statut = str(participant.get("statut", "")).upper()

        if "NON_PARTANT" in statut or statut == "NP":
            numero = participant.get("numPmu")

            if numero is not None:
                non_partants.add(numero)

    for incident in course.get("incidents", []) or []:
        if (
            isinstance(incident, dict)
            and incident.get("type") == "NON_PARTANT"
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

    return {
        "course": course.get(
            "libelle",
            course.get("nom", "Course"),
        ),
        "date": date_course,
        "reunion": reunion,
        "course_numero": course_numero,
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

def recuperer_programme(date, reunion=None):
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
            erreur,
        )
        return None


# =====================================
# RECHERCHE REUNION
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

    if isinstance(programme.get("courses"), list):
        return programme

    return None


# =====================================
# RECHERCHE COURSE
# =====================================

def trouver_course(reunion_data, course_numero):
    if not reunion_data:
        return None

    courses = reunion_data.get("courses", [])

    if not isinstance(courses, list):
        return None

    numero_recherche = str(
        course_numero or ""
    ).upper().strip()

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

    reunion_numero = (
        str(reunion)
        .upper()
        .replace("R", "")
        .strip()
    )

    course_numero = (
        str(course_numero)
        .upper()
        .replace("C", "")
        .strip()
    )

    if not reunion_numero.isdigit() or not course_numero.isdigit():
        return []

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
# DETECTION QUINTE+
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
            if "QUINTE" in cle_texte:
                return True
            if isinstance(contenu, (str, list, dict)):
                if _texte_contient_quinte(contenu):
                    return True
        return False

    if isinstance(valeur, list):
        return any(_texte_contient_quinte(item) for item in valeur)

    return "QUINTE" in str(valeur).upper()


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
    Detection securisee :
    1. Si l'API expose explicitement les types de paris, recherche
       ciblee du QuintÃ©+ dans ces champs.
    2. Sinon, recherche dans les champs d'identification de la course
       avec un minimum de 10 partants.
    Une course a 6 partants ne peut donc pas etre retenue.
    """
    if not isinstance(course, dict):
        return False

    types_paris = _extraire_types_paris(course)

    if types_paris:
        for pari in types_paris:
            if _texte_contient_quinte(pari):
                return True

        return False

    nombre_partants = _nombre_partants(course)

    if nombre_partants < PARTANTS_MINIMUM_QUINTE:
        return False

    champs_identification = (
        "libelle",
        "nom",
        "libelleCourt",
        "libelleLong",
        "typeCourse",
    )

    for cle in champs_identification:
        valeur = course.get(cle)

        if isinstance(valeur, str):
            if "QUINTE" in valeur.upper():
                return True

    return False



# =====================================
# RECHERCHE QUINTE+ DU JOUR
# =====================================

def trouver_quinte_du_jour(date):
    """
    Parcourt les reunions disponibles et retourne :
        (programme, reunion, course)
    pour le vrai QuintÃ©+ detecte.

    Aucun R1/C1 n'est impose pour la recherche automatique.
    """
    for numero_reunion in range(1, 13):
        reunion = f"R{numero_reunion}"

        programme = recuperer_programme(
            date,
            reunion,
        )

        if not programme:
            continue

        reunion_data = trouver_reunion(
            programme,
            reunion,
        )

        if not reunion_data:
            continue

        courses = reunion_data.get("courses", [])

        if not isinstance(courses, list):
            continue

        for course in courses:
            if not isinstance(course, dict):
                continue

            if _contient_quinte(course):
                return (
                    programme,
                    reunion,
                    course,
                )

    return None, None, None


# =====================================
# CHARGEMENT COURSE PMU
# =====================================

def charger_course_pmu(
    date,
    reunion=None,
    course_numero=None,
):
    """
    Charge une course PMU.

    - Sans reunion/course : recherche automatique du vrai QuintÃ©+.
    - Avec reunion/course : charge explicitement la course demandee.
    """
    try:
        # =================================
        # MODE AUTOMATIQUE QUINTE+
        # =================================
        if reunion is None and course_numero is None:
            programme, reunion_trouvee, course = (
                trouver_quinte_du_jour(date)
            )

            if not course:
                print(
                    "Aucun QuintÃ©+ PMU trouve pour",
                    date,
                )
                return None

            reunion = reunion_trouvee
            course_numero = (
                course.get("numOrdre")
                or course.get("numCourse")
                or course.get("numero")
            )

        # =================================
        # MODE COURSE PRECISE
        # =================================
        else:
            if reunion is None or course_numero is None:
                return None

            programme = recuperer_programme(
                date,
                reunion,
            )

            if not programme:
                return None

            reunion_data = trouver_reunion(
                programme,
                reunion,
            )

            if not reunion_data:
                print(
                    "Reunion PMU introuvable :",
                    reunion,
                )
                return None

            course = trouver_course(
                reunion_data,
                course_numero,
            )

            if not course:
                print(
                    "Course PMU introuvable :",
                    course_numero,
                )
                return None

        # =================================
        # RECUPERATION PARTICIPANTS
        # =================================
        participants = recuperer_participants(
            date,
            reunion,
            course_numero,
        )

        if not participants:
            print(
                "Aucun participant PMU trouve pour",
                reunion,
                course_numero,
            )
            return None

        # =================================
        # TRANSFORMATION DANS LE FORMAT
        # ATTENDU PAR engine.py
        # =================================
        resultat = transformer_course(
            course,
            participants,
        )

        if not resultat:
            return None

        resultat["reunion"] = reunion
        resultat["course_numero"] = course_numero

        if not resultat.get("date"):
            resultat["date"] = date

        return resultat

    except Exception as erreur:
        print(
            "Erreur chargement course PMU :",
            erreur,
        )
        return None


# =====================================
# TEST
# =====================================

if __name__ == "__main__":
    from datetime import datetime

    print("AZ Turf Pro - Source PMU")
    print("Module charge correctement.")

    date_test = datetime.now().strftime("%d%m%Y")
    resultat = charger_course_pmu(date_test)

    if resultat:
        print("Connexion PMU disponible.")
        print("Course trouvee :", resultat.get("course"))
        print(
            "Reunion/Course :",
            resultat.get("reunion"),
            resultat.get("course_numero"),
        )
        print("Partants :", len(resultat.get("chevaux", [])))
    else:
        print(
            "PMU indisponible ou aucun Quinte+ trouve "
            "aujourd'hui (voir messages ci-dessus)."
        )


# =====================================
# ARRIVEE REELLE D'UNE COURSE PASSEE
# (additif - utilise pour l'historique)
# =====================================

def recuperer_arrivee_pmu(date, reunion, course_numero):
    """
    Recupere l'ordre d'arrivee reel d'une course PMU deja courue
    (champ "ordreArrivee" de l'API, present une fois la course
    terminee). Retourne une liste de numeros dans l'ordre
    d'arrivee, ou None si la course n'est pas encore courue ou
    introuvable.
    """

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
    
