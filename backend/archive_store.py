"""Archive persistante des courses AZ Turf Pro.

Stockage PostgreSQL via DATABASE_URL, indépendant de data/historique_az.json.
La table est créée automatiquement au démarrage du premier enregistrement.
"""
from __future__ import annotations
import hashlib
import json
import os
from datetime import datetime, timezone

try:
    import psycopg2
    from psycopg2.extras import Json
except Exception:
    psycopg2 = None
    Json = None


def _database_url() -> str:
    return (os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or "").strip()


def _cle_course(course: dict) -> str:
    c = course if isinstance(course, dict) else {}
    date = str(c.get("date") or c.get("date_course") or "").strip()
    reunion = str(c.get("reunion") or "").strip().upper()
    numero = str(c.get("course_numero") or c.get("numero_course") or "").strip().upper()
    pmu_id = str(c.get("pmu_id") or c.get("identifiant_pmu") or c.get("id_pmu") or "").strip()
    if pmu_id:
        return "pmu:" + pmu_id
    if date and reunion and numero:
        return f"course:{date}|{reunion}|{numero}"
    raw = json.dumps(c, ensure_ascii=False, sort_keys=True, default=str)
    return "hash:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _connexion():
    if psycopg2 is None:
        raise RuntimeError("psycopg2 indisponible")
    url = _database_url()
    if not url:
        raise RuntimeError("DATABASE_URL non configurée")
    return psycopg2.connect(url)


def _init(conn) -> None:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS az_course_archive (
                id BIGSERIAL PRIMARY KEY,
                course_key TEXT NOT NULL UNIQUE,
                pmu_id TEXT,
                date_course TEXT,
                reunion TEXT,
                course_numero TEXT,
                hippodrome TEXT,
                course_json JSONB NOT NULL,
                chevaux_json JSONB NOT NULL,
                classement_json JSONB NOT NULL,
                tickets_json JSONB NOT NULL,
                selection_az_json JSONB NOT NULL,
                selection_premium_json JSONB NOT NULL,
                favori_json JSONB NOT NULL,
                non_partants_json JSONB NOT NULL,
                arrivee_json JSONB,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
    conn.commit()


def archiver_course(data: dict) -> dict:
    course = data.get("course") if isinstance(data, dict) else {}
    course = course if isinstance(course, dict) else {}
    key = _cle_course(course)
    pmu_id = course.get("pmu_id") or course.get("identifiant_pmu") or course.get("id_pmu")
    date_course = course.get("date") or course.get("date_course")
    reunion = course.get("reunion")
    numero = course.get("course_numero") or course.get("numero_course")
    hippodrome = course.get("hippodrome")
    conn = _connexion()
    try:
        _init(conn)
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO az_course_archive
                (course_key, pmu_id, date_course, reunion, course_numero, hippodrome,
                 course_json, chevaux_json, classement_json, tickets_json,
                 selection_az_json, selection_premium_json, favori_json,
                 non_partants_json, arrivee_json)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (course_key) DO UPDATE SET
                  pmu_id=COALESCE(EXCLUDED.pmu_id, az_course_archive.pmu_id),
                  course_json=EXCLUDED.course_json,
                  chevaux_json=EXCLUDED.chevaux_json,
                  classement_json=EXCLUDED.classement_json,
                  tickets_json=EXCLUDED.tickets_json,
                  selection_az_json=EXCLUDED.selection_az_json,
                  selection_premium_json=EXCLUDED.selection_premium_json,
                  favori_json=EXCLUDED.favori_json,
                  non_partants_json=EXCLUDED.non_partants_json,
                  updated_at=NOW()
                RETURNING id
            """, (
                key, pmu_id, date_course, reunion, numero, hippodrome,
                Json(course), Json(data.get("chevaux") or []), Json(data.get("classement") or []),
                Json(data.get("tickets") or {}), Json(data.get("selection_az") or []),
                Json(data.get("selection_premium") or []), Json(data.get("favori") or {}),
                Json(data.get("non_partants") or []), Json(data.get("arrivee")) if data.get("arrivee") else None,
            ))
            row_id = cur.fetchone()[0]
        conn.commit()
        return {"status": "success", "id": row_id, "course_key": key}
    finally:
        conn.close()


def archiver_arrivee(course_key: str, arrivee: list) -> bool:
    conn = _connexion()
    try:
        _init(conn)
        with conn.cursor() as cur:
            cur.execute("UPDATE az_course_archive SET arrivee_json=%s, updated_at=NOW() WHERE course_key=%s", (Json(arrivee), course_key))
            ok = cur.rowcount > 0
        conn.commit()
        return ok
    finally:
        conn.close()


def lire_archive(limit: int = 100) -> list[dict]:
    conn = _connexion()
    try:
        _init(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT id, course_key, pmu_id, date_course, reunion, course_numero, hippodrome, course_json, chevaux_json, classement_json, tickets_json, selection_az_json, selection_premium_json, favori_json, non_partants_json, arrivee_json, created_at, updated_at FROM az_course_archive ORDER BY created_at DESC LIMIT %s", (max(1, min(int(limit), 1000)),))
            cols = [d.name for d in cur.description]
            rows = cur.fetchall()
        return [dict(zip(cols, row)) for row in rows]
    finally:
        conn.close()
