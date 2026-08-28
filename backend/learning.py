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
    os.makedirs(HISTORIQUE_DATA_DIR, exist_ok=True)
    fd, fichier_temp = tempfile.mkstemp(
        prefix="historique_az_", suffix=".tmp", dir=HISTORIQUE_DATA_DIR, text=True
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
    entree["evaluation"] = evaluer_prediction(entree)
    entree["heure_arrivee"] = maintenant.isoformat(timespec="seconds")
    entree["publication_at"] = (
        maintenant + timedelta(hours=2)
    ).isoformat(timespec="seconds")
    entree["publication_statut"] = "PROGRAMMEE"

    _sauvegarder_historique(historique)
    return True


def synchroniser_arrivees_pmu():
    """Synchronise les arrivées PMU disponibles avec les pronostics enregistrés."""
    historique = _charger_historique()
    try:
        from pmu_source import recuperer_arrivee_pmu
    except Exception:
        return {"modifie": False, "courses_verifiees": 0, "arrivees_recuperees": 0}
    modifie = False; verifiees = 0; recuperees = 0
    for entree in historique:
        if not isinstance(entree, dict) or entree.get("arrivee"):
            continue
        course = entree.get("course") or {}
        date = course.get("date") or entree.get("date")
        reunion = course.get("reunion") or entree.get("reunion")
        numero = course.get("course_numero") or entree.get("course_numero")
        if not (date and reunion and numero):
            continue
        verifiees += 1
        try:
            arrivee = recuperer_arrivee_pmu(date, reunion, numero)
        except Exception:
            continue
        if not arrivee:
            continue
        entree["arrivee"] = [_numero_arrivee(x) for x in arrivee if _numero_arrivee(x)][:5]
        entree["evaluation"] = evaluer_prediction(entree)
        entree["heure_arrivee"] = datetime.now().isoformat(timespec="seconds")
        modifie = True; recuperees += 1
    if modifie:
        _sauvegarder_historique(historique)
    return {"modifie": modifie, "courses_verifiees": verifiees, "arrivees_recuperees": recuperees}


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


def _numero_arrivee(x):
    if isinstance(x, dict):
        return _numero(x.get("numero") or x.get("num") or x.get("cheval"))
    return _numero(x)


def evaluer_prediction(entree):
    """Évalue une prédiction dès qu'une arrivée officielle est disponible.

    Retourne des métriques simples et déterministes, sans modifier le scoring AZ.
    """
    if not isinstance(entree, dict):
        return {}
    arrivee = [_numero_arrivee(x) for x in (entree.get("arrivee") or []) if _numero_arrivee(x)]
    selection = entree.get("selection_az") or []
    selection = [_numero_arrivee(x) for x in selection if _numero_arrivee(x)]
    premium = entree.get("selection_premium") or []
    premium = [_numero_arrivee(x) for x in premium if _numero_arrivee(x)]
    classement = entree.get("classement") or []
    classement_nums = [_numero_arrivee(x) for x in classement if _numero_arrivee(x)]
    if not arrivee:
        return {}

    top3=set(arrivee[:3]); top5=set(arrivee[:5])
    return {
        "favori_numero": _numero_arrivee(entree.get("favori")),
        "favori_top3": _numero_arrivee(entree.get("favori")) in top3,
        "selection_az_top3": sum(n in top3 for n in selection),
        "selection_az_top5": sum(n in top5 for n in selection),
        "selection_premium_top3": sum(n in top3 for n in premium),
        "selection_premium_top5": sum(n in top5 for n in premium),
        "classement_top1_correct": bool(classement_nums and classement_nums[0] == arrivee[0]),
        "arrivee": arrivee[:5],
    }


def calculer_performance_historique(historique=None):
    """Calcule des indicateurs pondérés sur les courses déjà terminées.

    Les courses récentes reçoivent un poids supérieur (décroissance exponentielle),
    sans entraîner ni modifier encore le modèle de scoring.
    """
    historique = _charger_historique() if historique is None else historique
    terminees=[]
    for entree in historique:
        if not isinstance(entree, dict) or not entree.get("arrivee"):
            continue
        evaluation=entree.get("evaluation") or evaluer_prediction(entree)
        if evaluation:
            terminees.append((entree,evaluation))
    if not terminees:
        return {"courses_terminees":0,"poids_total":0.0,"precision_favori_top3":0.0,"precision_selection_az_top3":0.0,"precision_selection_az_top5":0.0}

    # Plus la course est récente dans l'historique, plus son poids est fort.
    total=0.0; fav=0.0; az3=0.0; az5=0.0
    for idx,(entree,ev) in enumerate(reversed(terminees)):
        poids=0.90 ** idx
        total += poids
        fav += poids * float(bool(ev.get("favori_top3")))
        az3 += poids * (float(ev.get("selection_az_top3",0)) / max(1,len(entree.get("selection_az") or [])))
        az5 += poids * (float(ev.get("selection_az_top5",0)) / max(1,len(entree.get("selection_az") or [])))
    return {
        "courses_terminees":len(terminees),
        "poids_total":round(total,6),
        "precision_favori_top3":round(fav/total,4),
        "precision_selection_az_top3":round(az3/total,4),
        "precision_selection_az_top5":round(az5/total,4),
    }

# =========================================================
# APPRENTISSAGE PROGRESSIF / CALIBRATION V1
# =========================================================

def _float_safe(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _historique_termine(historique=None):
    historique = _charger_historique() if historique is None else historique
    return [
        e for e in historique
        if isinstance(e, dict) and e.get("arrivee") and (e.get("classement") or e.get("selection_az"))
    ]


def _taux_lisse(succes, essais, prior=0.50, force=8.0):
    essais = max(0, int(essais or 0))
    succes = max(0.0, min(float(essais), _float_safe(succes)))
    return (succes + force * prior) / (essais + force) if essais else prior


def construire_calibration(historique=None):
    """Construit une calibration bornée à partir des résultats réellement observés.

    On apprend uniquement sur des arrivées officielles déjà présentes. Le moteur
    de base reste inchangé si le volume d'observations est insuffisant.
    """
    courses = _historique_termine(historique)
    observations = []
    for entree in courses:
        arrivee = [_numero_arrivee(x) for x in (entree.get("arrivee") or []) if _numero_arrivee(x)]
        top3, top5 = set(arrivee[:3]), set(arrivee[:5])
        classement = entree.get("classement") or []
        for rang, cheval in enumerate(classement, start=1):
            if not isinstance(cheval, dict):
                continue
            numero = _numero_arrivee(cheval)
            if not numero:
                continue
            observations.append({
                "score": _float_safe(cheval.get("score_az", cheval.get("indice_az", 0))),
                "rang": rang,
                "top3": numero in top3,
                "top5": numero in top5,
            })

    # Apprentissage par bandes de score : robuste aux changements de numéros.
    bandes = {"0_39": [], "40_59": [], "60_79": [], "80_100": [], "101_plus": []}
    for obs in observations:
        score = obs["score"]
        if score < 40: cle = "0_39"
        elif score < 60: cle = "40_59"
        elif score < 80: cle = "60_79"
        elif score <= 100: cle = "80_100"
        else: cle = "101_plus"
        bandes[cle].append(obs)

    calibration = {}
    for cle, vals in bandes.items():
        essais = len(vals)
        top3 = sum(bool(x["top3"]) for x in vals)
        top5 = sum(bool(x["top5"]) for x in vals)
        calibration[cle] = {
            "essais": essais,
            "taux_top3": round(_taux_lisse(top3, essais), 4),
            "taux_top5": round(_taux_lisse(top5, essais), 4),
        }
    return {
        "courses_terminees": len(courses),
        "observations": len(observations),
        "calibration": calibration,
    }


def ajuster_score_avec_apprentissage(score, historique=None):
    """Ajustement très borné du score, activé seulement après assez de données.

    L'objectif est une calibration progressive, pas un remplacement du modèle.
    Le facteur maximal est volontairement limité pour éviter la dérive.
    """
    base = _float_safe(score)
    calibration = construire_calibration(historique)
    if calibration["courses_terminees"] < 10 or calibration["observations"] < 80:
        return round(base, 2)

    if base < 40: cle = "0_39"
    elif base < 60: cle = "40_59"
    elif base < 80: cle = "60_79"
    elif base <= 100: cle = "80_100"
    else: cle = "101_plus"

    taux = calibration["calibration"][cle]["taux_top3"]
    # Centre de gravité à 50%; effet maximal +/- 0.60 point.
    ajustement = max(-0.60, min(0.60, (taux - 0.50) * 1.20))
    return round(base + ajustement, 2)


def analyser_erreurs_historique(historique=None):
    """Identifie les erreurs récurrentes du moteur sans inventer de cause."""
    courses = _historique_termine(historique)
    erreurs = {"favori_hors_top3": 0, "gagnant_hors_selection": 0, "top1_incorrect": 0}
    total = 0
    for entree in courses:
        ev = entree.get("evaluation") or evaluer_prediction(entree)
        if not ev:
            continue
        total += 1
        if not ev.get("favori_top3"):
            erreurs["favori_hors_top3"] += 1
        arrivee = [str(x) for x in (entree.get("arrivee") or [])]
        selection = [str(_numero_arrivee(x)) for x in (entree.get("selection_az") or [])]
        if arrivee and arrivee[0] not in selection:
            erreurs["gagnant_hors_selection"] += 1
        if not ev.get("classement_top1_correct"):
            erreurs["top1_incorrect"] += 1
    return {
        "courses_evaluees": total,
        "erreurs": erreurs,
        "taux_erreur_favori_top3": round(erreurs["favori_hors_top3"] / total, 4) if total else 0.0,
        "taux_gagnant_hors_selection": round(erreurs["gagnant_hors_selection"] / total, 4) if total else 0.0,
        "taux_top1_incorrect": round(erreurs["top1_incorrect"] / total, 4) if total else 0.0,
    }



def calculer_performance_30_courses(historique=None):
    """Analyse les 30 dernières courses terminées réellement disponibles.

    Cette fonction ne fabrique aucune course manquante : si moins de 30 courses
    sont disponibles, le rapport indique explicitement le volume réel.
    """
    historique = _charger_historique() if historique is None else historique
    terminees = [
        e for e in historique
        if isinstance(e, dict) and e.get("arrivee")
    ]
    terminees = terminees[-30:]
    if not terminees:
        en_attente = sum(1 for e in historique if isinstance(e, dict) and not e.get("arrivee"))
        return {
            "courses_demandees": 30, "courses_disponibles": 0,
            "courses_en_attente": en_attente,
            "rapport_complet": False, "performance": {},
            "message": (
                "Aucune course terminée disponible. "
                f"{en_attente} pronostic(s) en attente d'arrivée officielle."
                if en_attente else "Aucune course terminée disponible."
            )
        }

    performance = calculer_performance_historique(terminees)
    erreurs = analyser_erreurs_historique(terminees)

    # Mesure séparée des tickets AZ et Premium, avec moyenne par course.
    az3 = az5 = prem3 = prem5 = 0.0
    fav3 = 0.0
    n = 0
    for entree in terminees:
        ev = entree.get("evaluation") or evaluer_prediction(entree)
        if not ev:
            continue
        n += 1
        selaz = max(1, len(entree.get("selection_az") or []))
        selpr = max(1, len(entree.get("selection_premium") or []))
        az3 += float(ev.get("selection_az_top3", 0)) / selaz
        az5 += float(ev.get("selection_az_top5", 0)) / selaz
        prem3 += float(ev.get("selection_premium_top3", 0)) / selpr
        prem5 += float(ev.get("selection_premium_top5", 0)) / selpr
        fav3 += float(bool(ev.get("favori_top3")))

    moyennes = {
        "favori_top3": round(fav3 / n, 4) if n else 0.0,
        "selection_az_top3": round(az3 / n, 4) if n else 0.0,
        "selection_az_top5": round(az5 / n, 4) if n else 0.0,
        "selection_premium_top3": round(prem3 / n, 4) if n else 0.0,
        "selection_premium_top5": round(prem5 / n, 4) if n else 0.0,
    }
    return {
        "courses_demandees": 30,
        "courses_disponibles": len(terminees),
        "courses_evaluees": n,
        "rapport_complet": len(terminees) >= 30,
        "performance": performance,
        "erreurs": erreurs,
        "moyennes": moyennes,
        "message": "Rapport basé uniquement sur les courses réellement terminées."
    }

def diagnostic_apprentissage(historique=None):
    perf = calculer_performance_historique(historique)
    erreurs = analyser_erreurs_historique(historique)
    calibration = construire_calibration(historique)
    return {
        "performance": perf,
        "erreurs": erreurs,
        "calibration": calibration,
        "apprentissage_actif": bool(
            calibration["courses_terminees"] >= 10 and calibration["observations"] >= 80
        ),
        "regle_securite": "aucun ajustement avant 10 courses terminées et 80 observations cheval",
    }



def diagnostic_historique():
    """Etat du pipeline de mémoire sans inventer de résultats."""
    historique = _charger_historique()
    enregistrees = terminees = en_attente = synchronisables = sans_identifiant = 0
    for entree in historique:
        if not isinstance(entree, dict):
            continue
        enregistrees += 1
        if entree.get("arrivee"):
            terminees += 1
            continue
        en_attente += 1
        course = entree.get("course") or {}
        date = course.get("date") or entree.get("date")
        reunion = course.get("reunion") or entree.get("reunion")
        numero = course.get("course_numero") or entree.get("course_numero")
        if date and reunion and numero:
            synchronisables += 1
        else:
            sans_identifiant += 1
    return {
        "pronostics_enregistres": enregistrees,
        "courses_terminees": terminees,
        "courses_en_attente": en_attente,
        "entrees_synchronisables": synchronisables,
        "entrees_sans_identifiant_pmu": sans_identifiant,
    }
