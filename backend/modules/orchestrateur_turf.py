"""Orchestrateur local du chatbot : aucun LLM externe requis."""
def detecter_intention(question):
    q=(question or "").lower()
    if any(x in q for x in ("actualité","actualite","news")): return "actualite"
    if any(x in q for x in ("définition","definition","que veut dire","signifie")): return "connaissance"
    if any(x in q for x in ("cote","côte","smart money","argent")): return "cotes"
    if any(x in q for x in ("météo","meteo","terrain","piste")): return "meteo"
    if any(x in q for x in ("performance","backtest","historique")): return "apprentissage"
    if any(x in q for x in ("ticket","pronostic","prono","quinté","quinte","cheval")): return "analyse_course"
    return "general"

def traiter_question(question, contexte=None, historique=None):
    from .chatbot_turf import repondre_assistant_turf
    resultat = repondre_assistant_turf(question, contexte or {}, historique or [])
    resultat["intention"] = detecter_intention(question)
    return resultat
