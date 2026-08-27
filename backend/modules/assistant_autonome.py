"""Façade publique vers le chatbot autonome réellement branché."""
def repondre(question, contexte=None, historique=None, state=None):
    from .chatbot_turf import repondre_assistant_turf
    resultat = repondre_assistant_turf(question, contexte or {}, historique or [])
    if state is not None:
        try:
            state.last_intent = resultat.get("intention", "")
            state.last_analysis = contexte or {}
        except Exception:
            pass
    return resultat
