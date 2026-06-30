# Data Architecture for AI — TP MSc 2025-2026

Architecture de données containerisée pour un laboratoire médical fictif.

## Stack

| Service | Image | Port |
|---------|-------|------|
| PostgreSQL | postgres:15 | 5432 |
| pgAdmin | dpage/pgadmin4 | 5050 |
| MongoDB | mongo:7 | 27017 |
| Mongo Express | mongo-express | 8081 |
| Portainer | portainer/portainer-ce | 9000 |
| Ingestor Python | ./app | — |

## Démarrage rapide

```bash
# 1. Copier et adapter les variables d'environnement
cp .env.example .env

# 2. Lancer tous les services
docker compose up -d

# 3. Vérifier l'état
docker compose ps
docker stats
```

## Interfaces d'administration

- **pgAdmin** : http://localhost:5050
- **Mongo Express** : http://localhost:8081
- **Portainer** : http://localhost:9000

## Tests de volumétrie

Modifier `NB_ROWS` dans `.env` puis relancer l'ingestor :

```bash
# 60 000 lignes (défaut)
NB_ROWS=60000 docker compose run --rm ingestor

# 600 000 lignes
NB_ROWS=600000 docker compose run --rm ingestor

# 6 000 000 lignes
NB_ROWS=6000000 docker compose run --rm ingestor
```

## Structure du projet

```
.
├── docker-compose.yml
├── .env.example
├── .gitignore
├── sql/
│   └── init.sql          # DDL PostgreSQL (tables + index)
├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── generate_data.py  # Génération Faker
│   ├── ingest_postgres.py
│   ├── ingest_mongodb.py
│   └── main.py
└── docs/
    ├── cahier_des_charges.md
    └── schema_nosql.json
```
