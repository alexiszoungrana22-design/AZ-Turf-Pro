
"""
AZ TURF PRO EXPERT V4
Mémoire et apprentissage du pronostiqueur
"""

from datetime import datetime


def enregistrer_pronostic(selection, contexte=None):
    return {
        "date": datetime.now().isoformat(),
        "selection": selection,
        "contexte": contexte or {},
        "statut": "en_attente"
    }


def comparer_prediction_resultat(pronostic, arrivee):
    selection = [str(x) for x in pronostic.get("selection", [])]
    arrivee = [str(x) for x in arrivee]

    communs = list(set(selection).intersection(set(arrivee)))

    return {
        "selection": selection,
        "arrivee": arrivee,
        "chevaux_trouves": communs,
        "nombre_trouves": len(communs)
    }


def analyser_erreurs(pronostic, arrivee):
    comparaison = comparer_prediction_resultat(pronostic, arrivee)

    erreurs = []

    if comparaison["nombre_trouves"] < 3:
        erreurs.append("Analyse à renforcer")

    return {
        "erreurs": erreurs,
        "comparaison": comparaison
    }


def calculer_indice_confiance(resultats):
    if not resultats:
        return 0

    reussite = sum(resultats) / len(resultats)
    return round(reussite * 100, 1)


# =====================================
# CALIBRATION DES COEFFICIENTS DE SCORING
# =====================================
# Calcule, à partir des courses réellement archivées (chevaux_json +
# arrivee_json), si chaque critère utilisé par scoring.py (forme,
# régularité, jockey, cote, expérience) est effectivement associé aux
# chevaux qui finissent bien placés ou non. Produit des multiplicateurs
# BORNÉS (jamais plus de ±20% du coefficient de base) pour éviter qu'un
# échantillon encore limité ne déforme le moteur. En dessous du seuil
# minimum, aucun ajustement n'est proposé : le moteur garde ses
# coefficients de base, inchangés.

SEUIL_MIN_COURSES = 30
CRITERES_CALIBRABLES = ("forme", "regularite", "jockey_score", "cote", "experience")
BORNE_AJUSTEMENT = 0.20  # ±20% maximum autour de 1.0


def _numero_str(v):
    return str(v) if v is not None else None


def calculer_calibration(lignes_archive, seuil_min=SEUIL_MIN_COURSES):
    """lignes_archive : liste de {"chevaux_json": [...], "arrivee_json": [...]}
    telle que retournée par archive_store.lire_archive_pour_calibration().

    Retourne un dict avec le statut, la taille de l'échantillon, et les
    facteurs calculés — jamais un facteur inventé sans donnée suffisante."""
    observations = {c: {"place": [], "non_place": []} for c in CRITERES_CALIBRABLES}
    courses_utilisables = 0

    for ligne in lignes_archive or []:
        chevaux = ligne.get("chevaux_json")
        arrivee = ligne.get("arrivee_json")
        if not isinstance(chevaux, list) or not chevaux or not isinstance(arrivee, list) or not arrivee:
            continue
        top5 = {_numero_str(n) for n in arrivee[:5]}
        if not top5:
            continue

        courses_utilisables += 1
        for cheval in chevaux:
            if not isinstance(cheval, dict):
                continue
            numero = _numero_str(cheval.get("numero"))
            place = numero is not None and numero in top5
            for critere in CRITERES_CALIBRABLES:
                valeur = cheval.get(critere)
                if valeur is None:
                    continue
                try:
                    valeur = float(valeur)
                except (TypeError, ValueError):
                    continue
                cible = observations[critere]["place" if place else "non_place"]
                cible.append(valeur)

    echantillon_chevaux = sum(
        len(o["place"]) + len(o["non_place"]) for o in observations.values()
    ) // max(1, len(CRITERES_CALIBRABLES))

    if courses_utilisables < seuil_min:
        return {
            "status": "donnees_insuffisantes",
            "echantillon_courses": courses_utilisables,
            "echantillon_chevaux": echantillon_chevaux,
            "seuil_requis": seuil_min,
            "facteurs": {},
            "message": (
                f"{courses_utilisables} course(s) avec résultat disponible(s), "
                f"{seuil_min} requises avant tout ajustement. Le moteur garde "
                f"ses coefficients de base, inchangés."
            ),
        }

    facteurs = {}
    details = {}
    for critere, obs in observations.items():
        places, non_places = obs["place"], obs["non_place"]
        if len(places) < 10 or len(non_places) < 10:
            # Pas assez d'observations pour CE critère précis, même si le
            # nombre de courses global suffit (ex: champ souvent absent).
            facteurs[critere] = 1.0
            details[critere] = {"statut": "donnees_insuffisantes_pour_ce_critere"}
            continue

        moyenne_place = sum(places) / len(places)
        moyenne_non_place = sum(non_places) / len(non_places)
        reference = moyenne_place + moyenne_non_place
        if reference == 0:
            facteurs[critere] = 1.0
            details[critere] = {"statut": "signal_nul"}
            continue

        # Écart relatif normalisé entre chevaux placés et non placés,
        # borné à ±BORNE_AJUSTEMENT pour rester un ajustement prudent.
        ecart_relatif = (moyenne_place - moyenne_non_place) / reference
        multiplicateur = 1.0 + max(-BORNE_AJUSTEMENT, min(BORNE_AJUSTEMENT, ecart_relatif))
        facteurs[critere] = round(multiplicateur, 4)
        details[critere] = {
            "statut": "calibre",
            "moyenne_chevaux_places": round(moyenne_place, 2),
            "moyenne_chevaux_non_places": round(moyenne_non_place, 2),
            "observations_places": len(places),
            "observations_non_places": len(non_places),
        }

    return {
        "status": "success",
        "echantillon_courses": courses_utilisables,
        "echantillon_chevaux": echantillon_chevaux,
        "seuil_requis": seuil_min,
        "facteurs": facteurs,
        "details": details,
    }
