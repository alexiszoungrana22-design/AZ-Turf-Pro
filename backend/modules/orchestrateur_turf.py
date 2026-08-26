
"""
AZ TURF PRO EXPERT V7
Orchestrateur principal.
Relie les couches Expert sans remplacer le moteur AZ.
"""

try:
    from modules.pronostiqueur_engine import analyser_profils_chevaux
except Exception:
    analyser_profils_chevaux = None

try:
    from modules.knowledge_turf import expliquer_terme
except Exception:
    expliquer_terme = None

try:
    from modules.news_turf import resumer_actualite
except Exception:
    resumer_actualite = None

try:
    from modules.learning_turf import analyser_erreurs
except Exception:
    analyser_erreurs = None


def detecter_intention(question):
    q = (question or "").lower()

    if any(x in q for x in ["pronostic", "quinté", "ticket", "cheval"]):
        return "analyse_course"

    if any(x in q for x in ["définition", "que veut dire", "signifie"]):
        return "connaissance"

    if any(x in q for x in ["actualité", "nouvelle", "info"]):
        return "actualite"

    if any(x in q for x in ["réussite", "performance", "historique"]):
        return "apprentissage"

    return "general"


def traiter_question(question, contexte=None):
    intention = detecter_intention(question)

    if intention == "connaissance" and expliquer_terme:
        return expliquer_terme(question)

    if intention == "actualite" and resumer_actualite:
        return resumer_actualite()

    return {
        "intention": intention,
        "message": "Analyse experte disponible."
    }
