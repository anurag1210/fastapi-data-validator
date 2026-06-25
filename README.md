# FastAPI Data Validator

A production-style REST API for automated data validation, built with FastAPI and Pydantic v2.

Inspired by real-world regression testing at enterprise scale — validating business-critical 
tables post-release across 100+ production datasets at JPMorgan Chase.

## Tech Stack

- **FastAPI** — REST API framework
- **Pydantic v2** — structured data validation and serialisation
- **Uvicorn** — ASGI server
- **Docker** — containerisation

## Features

- POST /api/v1/validate — run a validation job against any dataset
- GET /api/v1/health — health check endpoint
- Auto-generated Swagger UI at /docs
- Per-column validation results with null, uniqueness and range checks
- Structured JSON responses with UUID job tracking and UTC timestamps

## Quick Start

### Local

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs

### Docker

```bash
docker build -t fastapi-data-validator .
docker run -p 8000:8000 fastapi-data-validator
```

## Example Request

```json
POST /api/v1/validate

{
  "table_name": "customer_accounts",
  "data": [
    {"customer_id": 1, "email": "a@test.com", "balance": 500},
    {"customer_id": 2, "email": null, "balance": -50}
  ],
  "rules": [
    {"column_name": "customer_id", "not_null": true, "unique": true},
    {"column_name": "email", "not_null": true},
    {"column_name": "balance", "not_null": true, "min_value": 0}
  ]
}
```

## Example Response

```json
{
  "job_id": "6702815c-97e6-4289-9739-9a2488e2edbd",
  "table_name": "customer_accounts",
  "status": "failed",
  "total_records": 2,
  "validated_at": "2026-06-24T17:59:15.891882Z",
  "column_results": [...],
  "summary": "Validation FAILED for table 'customer_accounts'"
}
```

### Example of Failed Requests
```json
{
  "table_name": "customer_accounts",
  "data": [
    {"customer_id": 1, "email": "a@test.com", "balance": 500},
    {"customer_id": 2, "email": null, "balance": 1500},
    {"customer_id": 2, "email": "c@test.com", "balance": -50}
  ],
  "rules": [
    {"column_name": "customer_id", "not_null": true, "unique": true},
    {"column_name": "email", "not_null": true, "unique": false},
    {"column_name": "balance", "not_null": true, "min_value": 0}
  ]
}
```
## Project Structure

fastapi-data-validator/

├── app/

│   ├── main.py          # Application factory and router registration

│   ├── models.py        # Pydantic request and response models

│   ├── validator.py     # Core validation business logic

│   └── routes/

│       ├── health.py    # Health check endpoint

│       └── validate.py  # Validation endpoints

├── tests/               # Pytest test suite

├── Dockerfile           # Container definition

└── requirements.txt     # Dependencies

## Author

Anurag Gupta — Senior Software Engineer | AI Engineering

## Docker Commands

#docker build -t fastapi-data-validator .
#docker run -p 8000:8000 fastapi-data-validator


##Architecture Diagram

## Architecture

```
┌─────────────────┐     ┌──────────────────────────────────────────────┐
│     Clients     │     │              FastAPI App (app/)               │
│                 │     │                                               │
│  • Swagger UI   │────▶│  main.py                                      │
│  • REST client  │────▶│  App factory · router registration            │
│  • Mobile/curl  │────▶│                                               │
│                 │     │       ┌─────────────┐  ┌──────────────────┐  │
└─────────────────┘     │       │  health.py  │  │   validate.py    │  │
                        │       │  GET /health│  │  POST /validate  │  │
        JSON            │       └─────────────┘  └────────┬─────────┘  │
      response          │                                  │            │
         ◀──────────────│                        ┌─────────▼─────────┐  │
                        │                        │   validator.py    │  │
                        │                        │  Null · unique    │  │
                        │                        │  Range · status   │  │
                        │                        └─────────┬─────────┘  │
                        │                                  │            │
                        │                        ┌─────────▼─────────┐  │
                        │                        │    models.py      │  │
                        │                        │  Pydantic v2      │  │
                        │                        │  Request/Response │  │
                        │                        └───────────────────┘  │
                        │                                               │
                        │  ┌─────────────────────────────────────────┐  │
                        │  │  Dockerfile — python:3.11-slim · :8000  │  │
                        │  └─────────────────────────────────────────┘  │
                        └──────────────────────────────────────────────┘

┌─────────────────────────────────────┐
│  tests/test_api.py — pytest suite   │
│  6 tests · health · pass · fail     │
└─────────────────────────────────────┘
```

### Component responsibilities

| Component | Responsibility |
|-----------|---------------|
| `main.py` | App factory, router registration, root endpoint |
| `routes/health.py` | GET /api/v1/health — liveness check |
| `routes/validate.py` | POST /api/v1/validate — validation endpoint |
| `validator.py` | Core business logic — null, uniqueness, range checks |
| `models.py` | Pydantic v2 request and response models |
| `Dockerfile` | Containerisation — python:3.11-slim, port 8000 |
| `tests/test_api.py` | pytest suite — 6 tests covering all scenarios |