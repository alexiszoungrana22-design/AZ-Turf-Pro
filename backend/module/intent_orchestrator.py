"""AZ Turf Pro - orchestration locale sans dépendance à un LLM externe.
Comprend les demandes par familles sémantiques, extrait les chevaux et construit
un plan d'action pour les modules existants. Ne remplace aucun moteur métier.
"""
from __future__ import annotations
import re
import unicodedata
from dataclasses import dataclass, asdict
from typing import Any


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text or ""))
    return "".join(c for c in text if not unicodedata.combining(c)).lower().strip()


INTENT_PATTERNS = {
    "comparaison_tickets": ["compare", "comparatif", "difference", "versus", "face a", "contre"],
    "comparaison_chevaux": ["entre", "lequel", "qui est meilleur", "compare", "opposer", "duel", "face a"],
    "ticket": ["ticket", "combinaison", "quinte", "quarte", "trio", "couple", "jeu"],
    "analyse_independante": ["independant", "independamment", "sans az", "propre analyse", "ton analyse", "ton pronostic", "avis personnel"],
    "valeur": ["valeur", "value", "sous evalue", "sous-evalue", "cote interessante", "cote value", "rapport", "rentable"],
    "scenarios": ["scenario", "scenarios", "rythme", "allure", "course tactique", "piste lourde", "piste souple", "si la piste"],
    "cotes": ["cote", "cotes", "marche", "argent", "soutenu", "derive", "baisse de cote", "hausse de cote"],
    "piste_meteo": ["piste", "terrain", "meteo", "pluie", "vent", "lourd", "souple", "sec", "glissant"],
    "forme": ["forme", "musique", "derniere course", "dernieres courses", "regularite", "regulier", "periode"],
    "tactique": ["tactique", "parcours", "train", "rythme", "attentiste", "leader", "allure"],
    "historique": ["historique", "hier", "course passee", "course precedente", "arrivee", "resultat passe", "ancienne course"],
    "actualites": ["actualite", "actualites", "nouvelle", "nouvelles", "news", "infos", "information du jour"],
    "badges": ["badge", "badges", "icone", "sigle", "signification"],
    "favori": ["favori", "favorite", "base", "coup sur", "meilleur cheval", "gagnant", "premiere chance"],
    "outsiders": ["outsider", "tocard", "surprise", "pepite", "grosse cote", "gros rapport"],
    "aide": ["aide", "comment ca marche", "que peux tu faire", "capacites", "fonctionnalites"],
}

@dataclass
class Plan:
    intentions: list[str]
    chevaux: list[str]
    modules: list[str]
    strategie: str | None
    comparaison_az: bool
    demande_detaillee: bool


def extraire_chevaux(question: str, contexte: dict | None = None) -> list[str]:
    q = _norm(question)
    nums = re.findall(r"(?<!\d)(?:n\s*[°o]?\s*)?(\d{1,2})(?!\d)", q)
    seen = []
    for n in nums:
        if n not in seen:
            seen.append(n)
    # Si la demande est pronominale, reprendre les chevaux du dernier contexte.
    if not seen and contexte:
        for n in (contexte.get("derniers_chevaux") or []):
            s = str(n)
            if s not in seen:
                seen.append(s)
    return seen[:10]


def analyser(question: str, contexte: dict | None = None) -> Plan:
    q = _norm(question)
    scores: dict[str, int] = {}
    for intent, terms in INTENT_PATTERNS.items():
        score = 0
        for term in terms:
            if term in q:
                score += 2 if " " in term else 1
        scores[intent] = score

    # Signaux de structure, utiles quand la formulation est inhabituelle.
    if re.search(r"\b(et|avec|plus|ainsi que|aussi)\b", q):
        scores["analyse_independante"] += 1
    # Deux numéros + formulation comparative implicite (« 4 ou 7 »,
    # « meilleur entre 4 et 7 », « lequel choisir »).
    nums_detectes = re.findall(r"(?<!\d)(?:n\s*[°o]?\s*)?(\d{1,2})(?!\d)", q)
    if len(dict.fromkeys(nums_detectes)) >= 2 and (
        any(x in q for x in [" ou ", "lequel", "laquelle", "meilleur", "mieux", "preferes", "choisir"])
        or "compar" in q
    ):
        scores["comparaison_chevaux"] += 5
    if re.search(r"\b(pourquoi|explique|raison|justifie|comment)\b", q):
        scores["analyse_independante"] += 1
    if re.search(r"\b(4|5)\s*(chevaux|numeros|n°)", q):
        scores["ticket"] += 2

    intentions = [k for k, v in sorted(scores.items(), key=lambda x: x[1], reverse=True) if v > 0][:5]
    chevaux = extraire_chevaux(question, contexte)

    modules: list[str] = []
    mapping = {
        "ticket": ["moteur_az", "moteur_autonome", "strategie"],
        "comparaison_tickets": ["moteur_az", "moteur_autonome", "arbitre"],
        "comparaison_chevaux": ["moteur_az", "moteur_autonome", "valeur"],
        "analyse_independante": ["moteur_autonome", "multi_facteurs"],
        "valeur": ["cotes", "moteur_autonome", "valeur"],
        "scenarios": ["moteur_autonome", "scenarios", "piste_meteo"],
        "cotes": ["cotes", "moteur_autonome"],
        "piste_meteo": ["piste_meteo", "multi_facteurs"],
        "forme": ["multi_facteurs", "moteur_autonome"],
        "tactique": ["tactique", "scenarios", "moteur_autonome"],
        "historique": ["historique", "evaluation"],
        "actualites": ["actualites"],
        "badges": ["badges"],
        "favori": ["moteur_az", "moteur_autonome"],
        "outsiders": ["moteur_autonome", "valeur"],
    }
    for intent in intentions:
        for module in mapping.get(intent, []):
            if module not in modules:
                modules.append(module)

    strategie = None
    if any(x in q for x in ["prudent", "securise", "sans trop de risque"]): strategie = "prudent"
    elif any(x in q for x in ["offensif", "audacieux", "speculatif", "risque"]): strategie = "offensif"
    elif any(x in q for x in ["equilibre", "mix", "polyvalent"]): strategie = "equilibre"

    comparaison_az = any(x in q for x in ["az turf", "az pro", "indice az", "ticket az", "contre az"])
    if comparaison_az and "arbitre" not in modules:
        modules += [m for m in ["moteur_az", "moteur_autonome", "arbitre"] if m not in modules]

    detaillee = len(q.split()) >= 12 or any(x in q for x in ["pourquoi", "explique", "detail", "compare", "analyse"])
    if not intentions:
        intentions = ["analyse_independante"]
        modules = ["moteur_autonome", "multi_facteurs"]

    return Plan(intentions, chevaux, modules, strategie, comparaison_az, detaillee)


def plan_dict(question: str, contexte: dict | None = None) -> dict[str, Any]:
    return asdict(analyser(question, contexte))
