import logging

logger = logging.getLogger("pmu_sync")

def rechercher_arrivee(course):
    logger.info("[RESULTAT PMU] Recherche resultat pour %s", course)
    return None

def obtenir_resultat_course_test(course):
    return rechercher_arrivee(course)
