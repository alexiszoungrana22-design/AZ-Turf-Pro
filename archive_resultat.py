import logging

logger = logging.getLogger("archive_resultat")


def normaliser_arrivee(arrivee):
    """
    Transforme une arrivée en liste exploitable.
    Exemple:
    "12-8-5-13-6-2-9-4"
    devient:
    [12,8,5,13,6,2,9,4]
    """
    if not arrivee:
        return None

    if isinstance(arrivee, list):
        return arrivee

    return [
        int(x.strip())
        for x in str(arrivee).replace(",", "-").split("-")
        if x.strip().isdigit()
    ]


def mettre_a_jour_arrivee_archive(course, arrivee):
    """
    Prépare la mise à jour de az_course_archive.
    """
    arrivee = normaliser_arrivee(arrivee)

    if not arrivee:
        return {
            "status": "error",
            "message": "Arrivée vide"
        }

    logger.info(
        "[ARCHIVE] Mise à jour course %s avec arrivée %s",
        course.get("course_key"),
        arrivee
    )

    # Ici on branche l'UPDATE PostgreSQL az_course_archive
    # sans écraser les données existantes.

    return {
        "status": "success",
        "course_key": course.get("course_key"),
        "arrivee": arrivee,
        "archive": "mise_a_jour_prete"
    }
