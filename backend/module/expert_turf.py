
"""
AZ TURF PRO - Couche Expert Hippique
Extension indépendante du moteur existant.
Ne remplace pas chatbot_turf.py.
"""

from typing import Optional


def analyser_question_expert(question: str, contexte: dict) -> Optional[str]:
    q = (question or "").lower()

    if any(x in q for x in ["cote", "joué", "argent", "smart money", "délaissé"]):
        return analyser_marche(contexte)

    if any(x in q for x in ["statistique", "réussite", "fiable", "backtest"]):
        return analyser_performance(contexte)

    if any(x in q for x in ["terrain", "piste", "météo", "pluie"]):
        return analyser_conditions(contexte)

    if any(x in q for x in ["outsider", "surprise", "valeur"]):
        return analyser_valeur(contexte)

    return None


def analyser_marche(contexte):
    return "💰 Analyse marché : tendances de cotes à intégrer avec le module cotes_history."


def analyser_performance(contexte):
    return "📊 Analyse historique : statistiques backtest disponibles via stats_backtest."


def analyser_conditions(contexte):
    return "🌦️ Conditions : impact piste et météo à analyser via le module meteo_piste."


def analyser_valeur(contexte):
    return "🎯 Recherche valeur : combinaison indice AZ, cote et forme recommandée."
