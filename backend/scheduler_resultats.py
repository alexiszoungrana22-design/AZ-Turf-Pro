import asyncio
import logging

logger = logging.getLogger("pmu_scheduler")
INTERVALLE = 1800

async def synchroniser_course_test():
    logger.info("[SCHEDULER PMU] Verification course archivee")

async def boucle_scheduler():
    logger.info("[SCHEDULER PMU] Demarrage OK")
    while True:
        await synchroniser_course_test()
        await asyncio.sleep(INTERVALLE)

def lancer_scheduler():
    return asyncio.create_task(boucle_scheduler())
