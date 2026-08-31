"""Scheduler PMU AZ Turf Pro.

Synchronise les arrivées et prépare automatiquement la course de demain
à partir de deux heures après la course principale du jour.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta

logger = logging.getLogger("pmu_scheduler")
INTERVALLE = 1800  # 30 minutes
DELAI_PREPARATION_DEMAIN = timedelta(hours=2)


def _heure_course(course: dict) -> datetime | None:
    """Retourne la date/heure de départ locale si elle est exploitable."""
    date_val = course.get("date") or course.get("date_course")
    heure = course.get("heure_depart") or course.get("heure") or course.get("heureDepart")
    if not date_val or not heure:
        return None
    try:
        if isinstance(date_val, datetime):
            base = date_val.date()
        else:
            texte = str(date_val).strip()
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d%m%Y", "%Y%m%d"):
                try:
                    base = datetime.strptime(texte, fmt).date()
                    break
                except ValueError:
                    continue
            else:
                return None
        # PMU peut exposer HH:MM/HHhMM, ou exceptionnellement un timestamp.
        if isinstance(heure, (int, float)) and not isinstance(heure, bool):
            valeur = float(heure)
            if valeur > 1_000_000_000:
                if valeur > 10_000_000_000:
                    valeur /= 1000.0
                try:
                    return datetime.fromtimestamp(valeur)
                except (OverflowError, OSError, ValueError):
                    return None
            heure = str(int(valeur))

        h = str(heure).strip().replace("h", ":").replace("H", ":")
        if ":" not in h and h.isdigit() and len(h) in (3, 4):
            h = h.zfill(4)
            h = h[:2] + ":" + h[2:]
        elif ":" not in h:
            h += ":00"
        parts = h.split(":")
        if len(parts) < 2:
            return None
        hh, mm = int(parts[0]), int(parts[1])
        if not (0 <= hh <= 23 and 0 <= mm <= 59):
            return None
        return datetime.combine(base, datetime.min.time()).replace(hour=hh, minute=mm)
    except (TypeError, ValueError):
        return None


def _cle_course(course: dict) -> str:
    return str(
        course.get("cle_pmu")
        or course.get("pmu_id")
        or f"{course.get('date')}|{course.get('reunion')}|{course.get('course_numero')}"
    )


def preparer_course_demain() -> dict:
    """Charge et archive la course principale de demain si PMU la publie."""
    from pmu_source import charger_course_pmu
    from engine import lancer_analyse

    demain = datetime.now() + timedelta(days=1)
    date_pmu = demain.strftime("%d%m%Y")
    course = charger_course_pmu(date_pmu)
    if not course or not course.get("chevaux"):
        return {"status": "pending", "message": "Programme PMU de demain pas encore disponible", "date": date_pmu}

    resultat = lancer_analyse(course.get("chevaux") or [], course)
    try:
        from archive_store import archiver_course
        donnees = {
            "chevaux": resultat.get("chevaux", []),
            "classement": resultat.get("classement", []),
            "tickets": resultat.get("tickets", {}),
            "selection_az": resultat.get("tickets", {}).get("gratuit", {}).get("quinte", []),
            "selection_premium": resultat.get("tickets", {}).get("premium", {}).get("selection_quinte", []),
            "favori": resultat.get("favori", {}),
            "non_partants": resultat.get("non_partants", []),
            "course": course,
        }
        archive = archiver_course(donnees)
    except Exception as exc:
        logger.warning("Course de demain chargée mais non archivée: %s", exc)
        archive = {"status": "archive_pending", "error": str(exc)}

    return {
        "status": "ready",
        "date": date_pmu,
        "reunion": course.get("reunion"),
        "course_numero": course.get("course_numero"),
        "heure_depart": course.get("heure_depart"),
        "hippodrome": course.get("hippodrome"),
        "archive": archive,
    }


def _doit_preparer_demain() -> bool:
    """Détermine si la fenêtre de préparation de demain est ouverte."""
    from pmu_source import charger_course_pmu

    course = charger_course_pmu(datetime.now().strftime("%d%m%Y"))
    if not course:
        return False
    depart = _heure_course(course)
    if depart is None:
        return False
    return datetime.now() >= depart + DELAI_PREPARATION_DEMAIN


async def synchroniser_course_test():
    """Synchronise les arrivées manquantes et prépare demain au bon moment."""
    try:
        from archive_store import lire_archive, archiver_arrivee
        from pmu_source import recuperer_arrivee_pmu
        courses = await asyncio.to_thread(lire_archive, 100)
        for course in courses:
            if not isinstance(course, dict) or course.get("arrivee_json"):
                continue
            date = course.get("date_course")
            reunion = course.get("reunion")
            numero = course.get("course_numero")
            key = course.get("course_key")
            if not (date and reunion and numero and key):
                continue
            try:
                arrivee = await asyncio.to_thread(recuperer_arrivee_pmu, date, reunion, numero)
                if arrivee:
                    await asyncio.to_thread(archiver_arrivee, key, arrivee)
                    logger.info("[SCHEDULER PMU] Arrivée synchronisée: %s", key)
            except Exception as exc:
                logger.debug("Arrivée non disponible pour %s: %s", key, exc)
    except Exception as exc:
        logger.debug("Synchronisation archive indisponible: %s", exc)

    try:
        if _doit_preparer_demain():
            result = await asyncio.to_thread(preparer_course_demain)
            logger.info("[SCHEDULER PMU] Préparation demain: %s", result)
    except Exception as exc:
        logger.warning("[SCHEDULER PMU] Préparation demain en échec: %s", exc)


async def boucle_scheduler():
    logger.info("[SCHEDULER PMU] Démarrage OK — préparation demain après +2h")
    while True:
        try:
            await synchroniser_course_test()
        except asyncio.CancelledError:
            logger.info("[SCHEDULER PMU] Arrêt")
            raise
        except Exception:
            logger.exception("[SCHEDULER PMU] Erreur de boucle")
        await asyncio.sleep(INTERVALLE)


def lancer_scheduler():
    return asyncio.create_task(boucle_scheduler())
