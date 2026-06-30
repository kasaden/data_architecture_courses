"""
Ingestion des données structurées dans PostgreSQL depuis les fichiers CSV.
Ordre d'insertion : doctors → medications → patients → prescriptions
"""

import os
import csv
import time
import logging
import psycopg2
from psycopg2.extras import execute_batch

logging.basicConfig(level=logging.INFO, format="%(asctime)s [PG] %(message)s")
log = logging.getLogger(__name__)

DSN = (
    f"host=postgres "
    f"dbname={os.environ['POSTGRES_DB']} "
    f"user={os.environ['POSTGRES_USER']} "
    f"password={os.environ['POSTGRES_PASSWORD']}"
)

DATA_DIR = os.path.join("/data", os.getenv("DATA_SIZE", "data_small"))
ENCODING = "latin-1"
BATCH    = 2000


def wait_for_postgres(max_retries: int = 10):
    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(DSN)
            log.info("Connexion PostgreSQL établie.")
            return conn
        except psycopg2.OperationalError as exc:
            log.warning("Tentative %d/%d — %s", attempt, max_retries, exc)
            time.sleep(3)
    raise RuntimeError("Impossible de se connecter à PostgreSQL.")


def read_csv(filename: str) -> list[dict]:
    path = os.path.join(DATA_DIR, filename)
    with open(path, encoding=ENCODING) as f:
        return list(csv.DictReader(f))


def insert_doctors(cur, rows: list[dict]) -> None:
    t0 = time.time()
    execute_batch(
        cur,
        """
        INSERT INTO doctors (id, first_name, last_name, specialty, hospital, phone)
        VALUES (%(id)s, %(first_name)s, %(last_name)s, %(specialty)s, %(hospital)s, %(phone)s)
        ON CONFLICT (id) DO NOTHING
        """,
        rows, page_size=BATCH,
    )
    log.info("Doctors insérés : %d en %.2fs", len(rows), time.time() - t0)


def insert_medications(cur, rows: list[dict]) -> None:
    t0 = time.time()
    execute_batch(
        cur,
        """
        INSERT INTO medications (id, name, dosage, unit, category)
        VALUES (%(id)s, %(name)s, %(dosage)s, %(unit)s, %(category)s)
        ON CONFLICT (id) DO NOTHING
        """,
        rows, page_size=BATCH,
    )
    log.info("Medications insérées : %d en %.2fs", len(rows), time.time() - t0)


def insert_patients(cur, rows: list[dict]) -> None:
    t0 = time.time()
    # doctor_id peut référencer un médecin absent → None si vide
    for r in rows:
        if not r.get("doctor_id"):
            r["doctor_id"] = None
    execute_batch(
        cur,
        """
        INSERT INTO patients (id, first_name, last_name, dob, gender, blood_type, doctor_id)
        VALUES (%(id)s, %(first_name)s, %(last_name)s, %(dob)s, %(gender)s, %(blood_type)s, %(doctor_id)s)
        ON CONFLICT (id) DO NOTHING
        """,
        rows, page_size=BATCH,
    )
    log.info("Patients insérés : %d en %.2fs", len(rows), time.time() - t0)


def insert_prescriptions(cur, rows: list[dict]) -> None:
    t0 = time.time()
    execute_batch(
        cur,
        """
        INSERT INTO prescriptions (id, consultation_id, medication_id, date, duration_days)
        VALUES (%(id)s, %(consultation_id)s, %(medication_id)s, %(date)s, %(duration_days)s)
        ON CONFLICT (id) DO NOTHING
        """,
        rows, page_size=BATCH,
    )
    log.info("Prescriptions insérées : %d en %.2fs", len(rows), time.time() - t0)


def run() -> None:
    log.info("Démarrage ingestion PostgreSQL — dataset: %s", DATA_DIR)
    t_total = time.time()

    conn = wait_for_postgres()
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            insert_doctors(cur,      read_csv("doctors.csv"))
            insert_medications(cur,  read_csv("medications.csv"))
            insert_patients(cur,     read_csv("patients.csv"))
            insert_prescriptions(cur, read_csv("prescriptions.csv"))
        conn.commit()
        log.info("Ingestion PostgreSQL terminée en %.2fs", time.time() - t_total)
    except Exception:
        conn.rollback()
        log.exception("Erreur — rollback effectué.")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    run()
