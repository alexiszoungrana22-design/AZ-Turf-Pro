
"""
AZ TURF PRO EXPERT V5
Base de connaissance hippique autonome
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def charger_base(fichier):
    chemin = DATA_DIR / fichier
    if not chemin.exists():
        return []
    with open(chemin, "r", encoding="utf-8") as f:
        return json.load(f)


def chercher_cheval(nom):
    chevaux = charger_base("chevaux.json")
    for c in chevaux:
        if c.get("nom", "").lower() == nom.lower():
            return c
    return None


def chercher_jockey(nom):
    jockeys = charger_base("jockeys.json")
    for j in jockeys:
        if j.get("nom", "").lower() == nom.lower():
            return j
    return None


def chercher_entraineur(nom):
    entraineurs = charger_base("entraineurs.json")
    for e in entraineurs:
        if e.get("nom", "").lower() == nom.lower():
            return e
    return None


def expliquer_terme(terme):
    lexique = charger_base("lexique_turf.json")
    for item in lexique:
        if item.get("terme", "").lower() == terme.lower():
            return item
    return None
