"""
Ingestion des consultations dans MongoDB depuis le fichier consultations.json.
"""

import os
import json
import time
import logging
from pymongo import MongoClient, ASCENDING
from pymongo.errors import BulkWriteError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [MONGO] %(message)s")
log = logging.getLogger(__name__)

MONGO_URI = (
    f"mongodb://{os.environ['MONGO_USER']}:{os.environ['MONGO_PASSWORD']}"
    f"@mongo:27017/"
)
MONGO_DB  = os.environ["MONGO_DB"]
DATA_DIR  = os.path.join("/data", os.getenv("DATA_SIZE", "data_small"))
BATCH_SIZE = 5_000


def get_collection():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10_000)
    col    = client[MONGO_DB]["consultations"]
    col.create_index([("consultation_id", ASCENDING)], unique=True)
    col.create_index([("patient_id",      ASCENDING)])
    col.create_index([("date",            ASCENDING)])
    return col


def run() -> None:
    path = os.path.join(DATA_DIR, "consultations.json")
    log.info("Chargement de %s…", path)
    t_total = time.time()

    with open(path, encoding="latin-1") as f:
        consultations = json.load(f)

    log.info("%d consultations chargées.", len(consultations))
    col = get_collection()

    inserted = 0
    nb_batches = -(-len(consultations) // BATCH_SIZE)
    for i in range(0, len(consultations), BATCH_SIZE):
        batch = consultations[i : i + BATCH_SIZE]
        t0 = time.time()
        try:
            result = col.insert_many(batch, ordered=False)
            inserted += len(result.inserted_ids)
        except BulkWriteError as bwe:
            inserted += bwe.details.get("nInserted", 0)
            log.warning("Doublons ignorés : %d", len(bwe.details.get("writeErrors", [])))
        log.info("Batch %d/%d — %d docs en %.2fs",
                 i // BATCH_SIZE + 1, nb_batches, len(batch), time.time() - t0)

    log.info("Ingestion MongoDB terminée — %d docs insérés en %.2fs",
             inserted, time.time() - t_total)


if __name__ == "__main__":
    run()
