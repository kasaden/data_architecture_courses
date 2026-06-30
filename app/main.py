import logging
import ingest_postgres
import ingest_mongodb

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

if __name__ == "__main__":
    ingest_postgres.run()
    ingest_mongodb.run()
