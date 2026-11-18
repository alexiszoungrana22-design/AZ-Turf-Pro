"""Calibration automatique prudente, déclenchée après l'enregistrement d'une arrivée officielle.

Aucun changement aux scores/tickets/routes existants. Les facteurs ne sont activés
que si une validation chronologique hors-échantillon est suffisante et favorable.
"""
from __future__ import annotations

MIN_COURSES_TOTAL = 50
MIN_COURSES_TEST = 15
NOUVELLES_COURSES_AVANT_REEVALUATION = 5
# Clé PostgreSQL réservée à ce mécanisme (verrou consultatif, aucune table métier verrouillée).
LOCK_KEY = 741926031


def executer_calibration_automatique():
    """Vérifie périodiquement les nouvelles arrivées et active seulement un gain validé.

    Toute erreur est renvoyée sous forme de statut pour que l'appelant puisse
    l'ignorer sans perturber l'enregistrement d'une arrivée ou l'API historique.
    """
    conn_verrou = None
    verrou = False
    try:
        from archive_store import (
            _connexion,
            lire_archive_pour_validation,
            enregistrer_calibration,
        )
        from learning_validation import evaluer_calibration_hors_echantillon

        conn_verrou = _connexion()
        conn_verrou.autocommit = True
        with conn_verrou.cursor() as cur:
            cur.execute("SELECT pg_try_advisory_lock(%s)", (LOCK_KEY,))
            verrou = bool(cur.fetchone()[0])
        if not verrou:
            return {"status": "ignoree", "raison": "calibration_deja_en_cours"}

        # Table d'état additive : CREATE IF NOT EXISTS, aucune donnée existante modifiée.
        with conn_verrou.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS az_auto_calibration_state (
                    id SMALLINT PRIMARY KEY CHECK (id = 1),
                    dernier_nombre_evalue INT NOT NULL DEFAULT 0,
                    derniere_evaluation TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
            cur.execute("""INSERT INTO az_auto_calibration_state (id, dernier_nombre_evalue)
                         VALUES (1, 0) ON CONFLICT (id) DO NOTHING""")
            cur.execute("SELECT dernier_nombre_evalue FROM az_auto_calibration_state WHERE id=1")
            dernier_nombre = int(cur.fetchone()[0])

        lignes = lire_archive_pour_validation(5000)
        nombre = len(lignes)
        if nombre < MIN_COURSES_TOTAL:
            # Ne pas avancer le compteur : dès que le seuil de 50 est atteint,
            # la première validation doit pouvoir se lancer immédiatement.
            return {
                "status": "en_attente", "courses_terminees": nombre,
                "seuil_requis": MIN_COURSES_TOTAL,
                "raison": "historique_insuffisant_aucune_activation",
            }
        if nombre - dernier_nombre < NOUVELLES_COURSES_AVANT_REEVALUATION:
            return {
                "status": "ignoree", "courses_terminees": nombre,
                "prochain_controle_apres_nouvelles_courses": max(0, NOUVELLES_COURSES_AVANT_REEVALUATION - (nombre - dernier_nombre)),
            }

        evaluation = evaluer_calibration_hors_echantillon(lignes)
        test_count = int(evaluation.get("courses_test_evaluees", 0) or 0)
        if evaluation.get("status") != "success" or test_count < MIN_COURSES_TEST:
            _memoriser_evaluation(conn_verrou, nombre)
            return {
                "status": "refusee", "raison": "validation_insuffisante",
                "courses_terminees": nombre, "courses_test_evaluees": test_count,
                "evaluation": evaluation,
            }

        ecarts = evaluation.get("ecart_points") or {}
        # Exiger un gain de couverture AZ ET Premium, sans régression
        # significative sur le gagnant ni sur le top 5 complet.
        favorable = calibration_candidate_acceptee(ecarts)
        if not favorable:
            _memoriser_evaluation(conn_verrou, nombre)
            return {
                "status": "conservee", "raison": "candidate_non_superieure_ou_regression_detectee",
                "courses_terminees": nombre, "evaluation": evaluation,
            }

        facteurs = evaluation.get("facteurs_candidats") or {}
        if not facteurs:
            _memoriser_evaluation(conn_verrou, nombre)
            return {"status": "conservee", "raison": "aucun_facteur_candidat", "evaluation": evaluation}

        ok = enregistrer_calibration(
            facteurs,
            int(evaluation.get("courses_apprentissage", 0)),
            sum(len(row.get("chevaux_json") or []) for row in lignes[:int(len(lignes) * 0.70)]),
        )
        _memoriser_evaluation(conn_verrou, nombre)
        return {
            "status": "activee" if ok else "erreur_enregistrement",
            "courses_terminees": nombre,
            "courses_test_evaluees": test_count,
            "ecart_points": ecarts,
            "facteurs_actives": bool(ok),
            "message": "Calibration activée après validation hors-échantillon." if ok else "La calibration précédente est conservée.",
        }
    except Exception as exc:
        return {"status": "erreur", "message": str(exc)}
    finally:
        if conn_verrou is not None:
            try:
                if verrou:
                    with conn_verrou.cursor() as cur:
                        cur.execute("SELECT pg_advisory_unlock(%s)", (LOCK_KEY,))
            except Exception:
                pass
            try:
                conn_verrou.close()
            except Exception:
                pass


def _memoriser_evaluation(conn, nombre: int) -> None:
    with conn.cursor() as cur:
        cur.execute("""UPDATE az_auto_calibration_state
                       SET dernier_nombre_evalue=%s, derniere_evaluation=NOW()
                       WHERE id=1""", (int(nombre),))


def calibration_candidate_acceptee(ecarts: dict) -> bool:
    """Politique d'activation : progrès simultané AZ et Premium.

    Compatibilité avec l'ancien format plat conservée pour les tests/outils
    historiques, mais le nouveau format exige les deux validations.
    """
    ecarts = ecarts or {}
    try:
        if "az" not in ecarts or "premium" not in ecarts:
            return (
                float(ecarts.get("couverture_moyenne_top5", 0)) >= 1.0
                and float(ecarts.get("taux_gagnant_dans_top5", 0)) >= -1.0
                and float(ecarts.get("taux_top5_complet", 0)) >= -1.0
            )
        for bloc in (ecarts["az"], ecarts["premium"]):
            if float(bloc.get("couverture_arrivee_top5", 0)) < 1.0:
                return False
            if float(bloc.get("taux_gagnant_dans_selection", 0)) < -1.0:
                return False
            if float(bloc.get("taux_top5_complet", 0)) < -1.0:
                return False
        return True
    except (TypeError, ValueError, KeyError):
        return False
