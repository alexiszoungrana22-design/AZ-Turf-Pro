
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
