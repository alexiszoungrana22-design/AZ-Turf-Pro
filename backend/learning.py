"""
AZ TURF PRO - HISTORIQUE / APPRENTISSAGE
Sauvegarde robuste des courses, selections et arrivees officielles.
Compatible avec engine.py / api.py existants.
"""

import json
import os
import tempfile
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
# Sur Render gratuit le système de fichiers est éphémère. On permet donc
# de déplacer le fichier vers un stockage monté plus tard sans modifier le code.
# Tant que HISTORIQUE_DATA_DIR n'est pas défini, comportement historique conservé.
HISTORIQUE_DATA_DIR = os.getenv("HISTORIQUE_DATA_DIR", DATA_DIR)
HISTORIQUE_FILE = os.path.join(HISTORIQUE_DATA_DIR, "historique_az.json")


def _charger_historique():
    if not os.path.exists(HISTORIQUE_FILE):
        return []
    try:
        with open(HISTORIQUE_FILE, "r", encoding="utf-8") as f:
            contenu = json.load(f)
        if isinstance(contenu, list):
            return contenu
        if isinstance(contenu, dict):
            for cle in ("historique", "courses", "data"):
                if isinstance(contenu.get(cle), list):
                    return contenu[cle]
    except (json.JSONDecodeError, OSError, TypeError):
        pass
    return []


def _sauvegarder_historique(historique):
    os.makedirs(DATA_DIR, exist_ok=True)
    fd, fichier_temp = tempfile.mkstemp(
        prefix="historique_az_", suffix=".tmp", dir=DATA_DIR, text=True
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(historique, f, indent=4, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(fichier_temp, HISTORIQUE_FILE)
    except Exception:
        try:
            os.unlink(fichier_temp)
        except OSError:
            pass
        raise


def _numero(valeur):
    return "" if valeur is None else str(valeur).strip()


def _cle_course(data):
    course = data.get("course") or {}
    date = course.get("date") or data.get("date") or ""
    reunion = course.get("reunion") or course.get("reunion_numero") or ""
    numero = course.get("course_numero") or course.get("numero_course") or ""
    nom = course.get("nom") or course.get("course") or course.get("libelle") or ""
    return (
        str(date).strip(),
        str(reunion).strip(),
        str(numero).strip(),
        str(nom).strip().upper(),
    )


def enregistrer_course(data):
    if not isinstance(data, dict):
        raise TypeError("data doit etre un dictionnaire")

    historique = _charger_historique()
    course = data.get("course") or {}
    tickets = data.get("tickets") or {}
    premium = tickets.get("premium") or {}

    selection_az = data.get("selection_az")
    if selection_az is None:
        selection_az = (tickets.get("gratuit") or {}).get("quinte") or []

    selection_premium = data.get("selection_premium")
    if selection_premium is None:
        selection_premium = (
            premium.get("selection_quinte")
            or premium.get("quinte")
            or []
        )

    non_partants = data.get("non_partants")
    if non_partants is None:
        non_partants = course.get("non_partants") or []

    classement = data.get("classement") or []

    nouvelle_course = {
        "date_analyse": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date": course.get("date") or data.get("date"),
        "course": course,
        "reunion": course.get("reunion"),
        "course_numero": course.get("course_numero"),
        "hippodrome": course.get("hippodrome"),
        "classement": classement,
        "favori": data.get("favori") or (classement[0] if classement else {}),
        "selection_az": selection_az,
        "selection_premium": selection_premium,
        "tickets": tickets,
        "non_partants": non_partants,
        "arrivee": data.get("arrivee"),
        "heure_arrivee": data.get("heure_arrivee"),
        "publication_at": data.get("publication_at"),
        "publication_statut": data.get("publication_statut", "EN ATTENTE"),
    }

    cle = _cle_course(nouvelle_course)
    index_existant = None

    if cle != ("", "", "", ""):
        for index, ancienne in enumerate(historique):
            if isinstance(ancienne, dict) and _cle_course(ancienne) == cle:
                index_existant = index
                break

    if index_existant is None:
        historique.append(nouvelle_course)
    else:
        ancienne = historique[index_existant]
        arrivee = ancienne.get("arrivee")
        heure_arrivee = ancienne.get("heure_arrivee")
        publication_at = ancienne.get("publication_at")
        statut = ancienne.get("publication_statut")

        ancienne.update(nouvelle_course)

        if arrivee:
            ancienne["arrivee"] = arrivee
        if heure_arrivee:
            ancienne["heure_arrivee"] = heure_arrivee
        if publication_at:
            ancienne["publication_at"] = publication_at
        if statut in ("PROGRAMMEE", "PUBLIE"):
            ancienne["publication_statut"] = statut

        historique[index_existant] = ancienne

    _sauvegarder_historique(historique)
    return nouvelle_course


def fusionner_historique(entrees):
    """Fusionne des sauvegardes clientes dans l'historique serveur.

    Utile sur un hébergement éphémère : le navigateur peut conserver une copie
    locale des analyses et la resynchroniser après un redémarrage du serveur.
    La clé de course empêche les doublons et les données déjà publiées sont
    conservées en priorité.
    """
    if not isinstance(entrees, list):
        return False
    historique = _charger_historique()
    index_par_cle = {}
    for i, ancienne in enumerate(historique):
        if isinstance(ancienne, dict):
            index_par_cle[_cle_course(ancienne)] = i

    modifie = False
    for entree in entrees:
        if not isinstance(entree, dict):
            continue
        cle = _cle_course(entree)
        if cle == ("", "", "", ""):
            continue
        if cle not in index_par_cle:
            historique.append(entree)
            index_par_cle[cle] = len(historique) - 1
            modifie = True
        else:
            actuel = historique[index_par_cle[cle]]
            # La copie cliente sert à récupérer une course perdue après reboot,
            # mais ne doit pas effacer une arrivée déjà connue côté serveur.
            arrivee = actuel.get("arrivee")
            actuel.update(entree)
            if arrivee:
                actuel["arrivee"] = arrivee
            historique[index_par_cle[cle]] = actuel
            modifie = True

    if modifie:
        _sauvegarder_historique(historique)
    return modifie


def lire_historique():
    return _charger_historique()


def mettre_a_jour_arrivee(index_entree, arrivee):
    historique = _charger_historique()

    try:
        index = int(index_entree)
    except (TypeError, ValueError):
        return False

    if index < 0 or index >= len(historique):
        return False

    if not isinstance(arrivee, list):
        arrivee = list(arrivee) if arrivee else []

    arrivee = [_numero(x) for x in arrivee if _numero(x)][:5]

    maintenant = datetime.now()
    entree = historique[index]
    entree["arrivee"] = arrivee
    entree["heure_arrivee"] = maintenant.isoformat(timespec="seconds")
    entree["publication_at"] = (
        maintenant + timedelta(hours=2)
    ).isoformat(timespec="seconds")
    entree["publication_statut"] = "PROGRAMMEE"

    _sauvegarder_historique(historique)
    return True


def mettre_a_jour_publications():
    historique = _charger_historique()
    maintenant = datetime.now()
    modifie = False

    for entree in historique:
        if not isinstance(entree, dict) or not entree.get("arrivee"):
            continue

        publication_at = entree.get("publication_at")

        if not publication_at:
            heure_arrivee = entree.get("heure_arrivee")
            if not heure_arrivee:
                continue
            try:
                dt = datetime.fromisoformat(str(heure_arrivee))
                publication_at = (
                    dt + timedelta(hours=2)
                ).isoformat(timespec="seconds")
                entree["publication_at"] = publication_at
                modifie = True
            except (ValueError, TypeError):
                continue

        try:
            date_publication = datetime.fromisoformat(str(publication_at))
        except (ValueError, TypeError):
            continue

        if (
            maintenant >= date_publication
            and entree.get("publication_statut") != "PUBLIE"
        ):
            entree["publication_statut"] = "PUBLIE"
            entree["date_publication"] = maintenant.isoformat(timespec="seconds")
            modifie = True

    if modifie:
        _sauvegarder_historique(historique)

    return modifie
