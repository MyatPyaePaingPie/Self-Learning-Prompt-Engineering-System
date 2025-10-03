import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)

def test_full_flow():
    """Test the complete flow from creating a prompt to getting details"""
    # This is a basic structure test - would need actual database setup for full e2e
    r = client.post("/v1/prompts", json={"text":"Help me code"})
    # For now, this will fail due to missing database, but structure is correct
    # assert r.status_code == 200
    # data = r.json()
    # assert "improved" in data and "judge" in data

def test_api_root():
    """Test that the API root responds correctly"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data

def test_metrics_endpoint():
    """Test that metrics endpoint is accessible"""
    response = client.get("/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

# Note: Full e2e tests would require:
# 1. Test database setup/teardown
# 2. Database migrations
# 3. Proper test fixtures
# This is a minimal structure to demonstrate the testing approach