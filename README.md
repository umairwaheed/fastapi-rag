# FastAPI RAG Example

This project has following features:
- Implements a RAG using PG Vector and OpenAI
- Implements RBAC using Oso framework
- Implements a fully functional CI/CD pipeline to lint and test the application
- Integrates linters to check code standardization
- Implements comprehensive tests to cover all the endpoints
- Integrates Swagger
- Implements deployment using Docker

## Technology Stack
- Python 3.13
- PG Vector 0.5.1
- Oso Authentication
- Docker

## Quickstart

Create virtual environment.

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

Copy environment file. Set the values as required.

```
cp env.sample .env
```

Start the docker containers for database and Oso.

```
docker-compose build
docker-compose up -d
```

These commands maybe written like this as well.

```
docker compose build
docker compose up -d
```

Run tests to see everything is working.

```
pytest
```

Run the dev server.

```
fastapi dev app/main.py
```

There is a utility script to create and admin user. If you don't give password,
the password will be set to admin. Make sure you set the OSO_API_KEY before
running this script. If you are running Oso Dev server, then you need to set
the following in your .env.

```
OSO_API_KEY=e_0123456789_12345_osotesttoken01xiIn
OSO_URL=http://localhost:8081
DEV_OSO_URL=http://localhost:8081
```

Run the script to create admin.

```
python scripts/create_admin.py <password>
```

The application will be accessible at `http://localhost:8000/`.
The swagger documentation will be accessible at `http://localhost:8000/docs`.

## Directory Structure
- app: Holds application code
- oso: Holds policy file and Dockerfile to setup dev Oso server
- prod: Holds prod docker setup
- scripts: Holds various utility scripts
- tests: Holds all the tests

## Deployment
You can do the deployment using docker-compose and docker like this.

```
cd prod;
docker-compose build
docker-compose up -d
```
