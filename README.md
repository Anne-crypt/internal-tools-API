# Internal Tools API

## Technologies
- Langage: Python 3.11.2
- Framework: FastAPI / Starlette
- Gestionnaire de dépendances & Outils: uv (Ruff intégré pour le linting et formatage)
- Base de données: PostgreSQL
- Port API: 8002 (configurable via le fichier .env)

## Quick Start

1. `docker compose --profile postgres up -d` pour lancer la base de données avec Docker
2. `uv sync` pour installer les dépendances
3. `uv run alembic upgrade head` pour lancer les migrations de bdd
4. `uv run uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload` démarrer le serveur de dev
5. L'API est disponible sur : http://localhost:8002
6. Documentation interactive (Swagger UI) : http://localhost:8002/docs

## Configuration
- Variables d'environnement: .env (j'ai pas fait l'exemple)
- Configuration DB: Gérée via l'URL DATABASE_URL asynchrone (postgresql+asyncpg://...) dans le fichier .env

## Tests
uv run pytest - Tests unitaires + intégration

## Architecture
- [Justification_choix_tech]
FastAPI & Asynchronisme : Choisi pour ses performances de pointe (moteur Starlette / Uvicorn) et son typage natif fort via Pydantic permettant de documenter automatiquement l'API tout en garantissant la sécurité des données entrantes.

Écosystème uv & Ruff : Utilisation du nouvel outil de gestion de paquets uv pour garantir des installations de dépendances et un lancement des tests ultra-rapides. Le formatage et le linting sont automatisés via ruff (uv run ruff format .).

Sécurité et Gestion des Erreurs :

Note sur la sécurité : L'application implémente un gestionnaire d'exceptions centralisé et volontairement non verbeux dans ses réponses publiques. En cas d'erreur inattendue (500), aucun détail technique, trace de code (stack trace) ou information sur la structure de la base de données n'est exposé à l'utilisateur afin de bloquer toute tentative d'ingénierie inverse ou d'exploitation de failles. Les détails fins restent cantonnés aux logs internes du serveur.

Gestion stricte du Business Logic (Filtres et Validation) : Implémentation de verrous métiers robustes (ex: interdiction d'avoir un coût minimum supérieur au coût maximum) directement gérés en amont de la base de données pour renvoyer des erreurs HTTP 400 claires.

- [Structure_projet_expliquee]
Le projet suit une architecture modulaire et découplée :
app/
├── api/             # Couche transport (Routes HTTP et contrôleurs)
├── core/            # Configuration globale, sécurité et gestionnaires d'exceptions
├── crud/            # Logique d'accès aux données (Requêtes SQL/SQLAlchemy)
├── models/          # Définition des tables ORM (Modèles de base de données)
└── schemas/         # Schémas de validation de données (Pydantic)
    ├── api/         # Schémas d'E/S pour les endpoints (Request/Response)
    └── table/       # Schémas miroirs des types de tables / Enums

Choix d'Architecture - Schémas Futurproof :
L'architecture des schémas Pydantic a été rigoureusement séparée en deux sous-dossiers : schemas/api/ (qui gère la forme des requêtes et réponses HTTP) et schemas/table/ (qui représente les types de données stricts de la base de données comme les structures de tables ou les Enums).
Cette séparation étanche rend l'API hautement évolutive (futurproof) : la structure de la base de données peut évoluer de manière indépendante sans casser le contrat d'interface exposé aux clients de l'API, et inversement.