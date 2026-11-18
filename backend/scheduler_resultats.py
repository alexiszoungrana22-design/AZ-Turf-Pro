"""Synchronisation périodique des arrivées et calibration prudente.

Le scheduler est additif : il ne modifie ni les routes existantes ni les
archives déjà enregistrées, et toute erreur reste non bloquante.
"""
import asyncio
import logging

logger = logging.getLogger("pmu_scheduler")
INTERVALLE = 1800


def synchroniser_arrivees_archivees(limit=100):
    from archive_store import lire_archive_performance, archiver_arrivee
    from pmu_source import recuperer_arrivee_pmu

    lignes = lire_archive_performance(limit)
    stats = {"courses_lues": len(lignes), "traitees": 0, "mises_a_jour": 0,
             "deja_a_jour": 0, "corrigees": 0, "ignorees": 0, "erreurs": []}
    nouvelle_arrivee = False
    for ligne in lignes:
        existante = ligne.get("arrivee_json")
        if existante:
            if isinstance(existante, list) and len(existante) > 5:
                try:
                    archiver_arrivee(ligne["course_key"], existante[:5])
                    stats["corrigees"] += 1
                except Exception as exc:
                    stats["erreurs"].append(f'{ligne.get("course_key")}: {exc}')
            else:
                stats["deja_a_jour"] += 1
            continue
        date = ligne.get("date_course")
        reunion = ligne.get("reunion")
        numero = ligne.get("course_numero")
        if not (date and reunion and numero):
            stats["ignorees"] += 1
            continue
        stats["traitees"] += 1
        try:
            arrivee = recuperer_arrivee_pmu(date, reunion, numero)
            if isinstance(arrivee, list) and arrivee:
                if archiver_arrivee(ligne["course_key"], arrivee[:5]):
                    stats["mises_a_jour"] += 1
                    nouvelle_arrivee = True
        except Exception as exc:
            stats["erreurs"].append(f'{ligne.get("course_key")}: {exc}')
    if nouvelle_arrivee:
        try:
            from auto_calibration import executer_calibration_automatique
            stats["calibration"] = executer_calibration_automatique()
        except Exception as exc:
            stats["calibration"] = {"status": "erreur", "message": str(exc)}
    return stats


async def synchroniser_course_test():
    try:
        resultat = await asyncio.to_thread(synchroniser_arrivees_archivees, 100)
        logger.info("[SCHEDULER PMU] Synchronisation terminée: %s", resultat)
        return resultat
    except Exception:
        logger.exception("[SCHEDULER PMU] Échec non bloquant de synchronisation")
        return {"status": "erreur"}


async def boucle_scheduler():
    logger.info("[SCHEDULER PMU] Démarrage; intervalle=%ss", INTERVALLE)
    while True:
        await synchroniser_course_test()
        await asyncio.sleep(INTERVALLE)


def lancer_scheduler():
    return asyncio.create_task(boucle_scheduler())
