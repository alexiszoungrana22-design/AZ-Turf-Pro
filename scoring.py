"""AZ Turf Pro - scoring spécialisé par discipline.

L'API historique calculer_score_az() est conservée pour éviter toute régression.
"""
from discipline_engine import calculer_score_specialise, construire_contexte


def calculer_score_az(cheval, discipline="TROT", contexte_course=None):
    """Calcule l'indice AZ avec le moteur adapté à la discipline."""
    # Accepte aussi un contexte pré-calculé ou une liste de chevaux pour les
    # critères comparatifs (poids, valeur handicap, etc.).
    contexte = contexte_course if isinstance(contexte_course, dict) else {}
    resultat = calculer_score_specialise(cheval, discipline, contexte)
    return resultat["score"]


def analyser_score_az(cheval, discipline="TROT", contexte_course=None):
    """Version détaillée utilisée par le moteur et le diagnostic."""
    contexte = contexte_course if isinstance(contexte_course, dict) else {}
    return calculer_score_specialise(cheval, discipline, contexte)
