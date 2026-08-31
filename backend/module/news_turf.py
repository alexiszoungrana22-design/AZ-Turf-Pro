
"""
AZ TURF PRO EXPERT V6
Module actualité hippique autonome
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def charger_actualites():
    fichier = DATA_DIR / "actualite_hippique.json"

    if not fichier.exists():
        return []

    with open(fichier, "r", encoding="utf-8") as f:
        return json.load(f)


def chercher_actualite_cheval(nom):
    actualites = charger_actualites()

    return [
        a for a in actualites
        if a.get("nom", "").lower() == nom.lower()
    ]


def chercher_evenement(nom):
    actualites = charger_actualites()

    return [
        a for a in actualites
        if a.get("categorie") == "evenement"
        and a.get("sujet", "").lower() == nom.lower()
    ]


def resumer_actualite():
    actualites = charger_actualites()

    if not actualites:
        return "Aucune actualité enregistrée."

    return actualites[:10]
