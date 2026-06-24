from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Health Tests
# ---------------------------------------------------------------------------

def test_health_check():
    """API health endpoint returns healthy status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root():
    """Root endpoint confirms API is running."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "FastAPI Data Validator is running"


# ---------------------------------------------------------------------------
# Validation Tests
# ---------------------------------------------------------------------------

def test_validation_passes():
    """Clean dataset passes all validation rules."""
    response = client.post("/api/v1/validate", json={
        "table_name": "customer_accounts",
        "data": [
            {"customer_id": 1, "email": "a@test.com", "balance": 500},
            {"customer_id": 2, "email": "b@test.com", "balance": 1500},
        ],
        "rules": [
            {"column_name": "customer_id", "not_null": True, "unique": True},
            {"column_name": "email", "not_null": True},
            {"column_name": "balance", "not_null": True, "min_value": 0}
        ]
    })
    assert response.status_code == 200
    assert response.json()["status"] == "passed"


def test_validation_fails_on_nulls():
    """Dataset with null values fails validation."""
    response = client.post("/api/v1/validate", json={
        "table_name": "customer_accounts",
        "data": [
            {"customer_id": 1, "email": None, "balance": 500},
        ],
        "rules": [
            {"column_name": "email", "not_null": True},
        ]
    })
    assert response.status_code == 200
    assert response.json()["status"] == "failed"


def test_validation_fails_on_duplicates():
    """Dataset with duplicate values fails uniqueness rule."""
    response = client.post("/api/v1/validate", json={
        "table_name": "customer_accounts",
        "data": [
            {"customer_id": 1, "balance": 500},
            {"customer_id": 1, "balance": 200},
        ],
        "rules": [
            {"column_name": "customer_id", "not_null": True, "unique": True},
        ]
    })
    assert response.status_code == 200
    assert response.json()["status"] == "failed"


def test_validation_fails_on_range():
    """Dataset with out of range values fails range rule."""
    response = client.post("/api/v1/validate", json={
        "table_name": "customer_accounts",
        "data": [
            {"balance": -100},
        ],
        "rules": [
            {"column_name": "balance", "not_null": True, "min_value": 0},
        ]
    })
    assert response.status_code == 200
    assert response.json()["status"] == "failed"