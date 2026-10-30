import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "UP"

def test_suppliers_endpoint():
    res = client.get("/suppliers?limit=5")
    assert res.status_code == 200
    assert isinstance(res.json(), list)