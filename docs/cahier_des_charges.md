# Cahier des charges — Architecture de données médicales containerisée

## 1. Contexte

Un laboratoire de santé souhaite centraliser ses données médicales dans une
infrastructure moderne, reproductible et monitorée. Les données proviennent de
plusieurs sources (dossiers patients, ordonnances, comptes-rendus de consultations)
et présentent des structures hétérogènes.

## 2. Besoins fonctionnels

| # | Besoin | Priorité |
|---|--------|----------|
| BF-1 | Stocker les informations des médecins, patients, médicaments et prescriptions | Haute |
| BF-2 | Stocker les comptes-rendus de consultations (symptômes et diagnostics) | Haute |
| BF-3 | Permettre des requêtes croisées entre entités (JOIN SQL) | Haute |
| BF-4 | Autoriser une structure de document variable pour les consultations | Haute |
| BF-5 | Ingérer automatiquement des jeux de données de grande volumétrie | Moyenne |
| BF-6 | Administrer les bases via des interfaces web | Moyenne |
| BF-7 | Monitorer l'état des services en temps réel | Basse |

## 3. Besoins techniques

| # | Besoin | Solution retenue |
|---|--------|-----------------|
| BT-1 | Base relationnelle avec contraintes d'intégrité | PostgreSQL 15 |
| BT-2 | Base documentaire pour données semi-structurées | MongoDB 7 |
| BT-3 | Administration PostgreSQL | pgAdmin 4 |
| BT-4 | Administration MongoDB | Mongo Express |
| BT-5 | Monitoring des conteneurs | Portainer CE |
| BT-6 | Orchestration des services | Docker Compose v3.9 |
| BT-7 | Pipeline d'ingestion | Python 3.12 (psycopg2, pymongo, Faker) |
| BT-8 | Persistance des données | Volumes Docker nommés |
| BT-9 | Isolation réseau | Bridge network Docker |
| BT-10 | Gestion des secrets | Fichier .env (non commité) |

## 4. Choix SQL vs NoSQL

### SQL (PostgreSQL) — données structurées

Les entités **médecins**, **patients**, **médicaments** et **prescriptions** ont
un schéma fixe avec des relations fortes (clés étrangères). PostgreSQL garantit
l'intégrité référentielle et permet des requêtes analytiques complexes
(agrégations, jointures multi-tables).

### NoSQL (MongoDB) — données semi-structurées

Les **consultations** contiennent des champs de longueur variable (`symptoms`,
`notes`) et peuvent évoluer sans migration de schéma. MongoDB stocke ces
documents JSON nativement. Le lien avec les entités PostgreSQL est maintenu
via `patient_id` et `medecin_id` (jointure applicative).

## 5. Architecture cible

```
[Ingestor Python]
       │
       ├──► [PostgreSQL:5432] ◄── [pgAdmin:5050]
       │         │ (volume postgres_data)
       │
       └──► [MongoDB:27017]  ◄── [Mongo Express:8081]
                 │ (volume mongo_data)

[Portainer:9000] ◄── /var/run/docker.sock (monitoring global)

Tous les services partagent le réseau isolé : medical_net
```

## 6. Volumétrie cible

| Palier | NB_ROWS | Usage |
|--------|---------|-------|
| Développement | 60 000 | Tests locaux rapides |
| Charge moyenne | 600 000 | Validation des performances |
| Charge haute | 6 000 000 | Test de robustesse |

## 7. Livrables

- `docker-compose.yml` commenté
- `sql/init.sql` — DDL PostgreSQL
- `app/` — Dockerfile, scripts Python, requirements.txt
- `docs/schema_nosql.json` — schéma JSON de la collection consultations
- `.env.example` — template de configuration
- `.gitignore` — exclusion du `.env` réel
