import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from api import app

client = TestClient(app)

def test_home_endpoint():
    """Test that the home endpoint returns the expected message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "yay! API is working!"}

def test_improve_endpoint_success():
    """Test that the improve endpoint processes a prompt correctly."""
    test_prompt = {"prompt": "Write a story about a cat"}
    
    response = client.post("/improve", json=test_prompt)
    assert response.status_code == 200
    
    data = response.json()
    assert "improved_prompt" in data
    assert data["improved_prompt"] == "Make it clearer: Write a story about a cat"

def test_improve_endpoint_empty_prompt():
    """Test the improve endpoint with an empty prompt."""
    test_prompt = {"prompt": ""}
    
    response = client.post("/improve", json=test_prompt)
    assert response.status_code == 200
    
    data = response.json()
    assert data["improved_prompt"] == "Make it clearer: "

def test_improve_endpoint_missing_prompt_key():
    """Test the improve endpoint with missing prompt key."""
    test_data = {"text": "some text"}
    
    response = client.post("/improve", json=test_data)
    # This should return 422 (validation error) because the prompt key is missing
    assert response.status_code == 422

def test_improve_endpoint_invalid_json():
    """Test the improve endpoint with invalid JSON."""
    response = client.post("/improve", data="invalid json")
    assert response.status_code == 422

def test_improve_endpoint_long_prompt():
    """Test the improve endpoint with a very long prompt."""
    long_prompt = "Write a story about a cat " * 100
    test_prompt = {"prompt": long_prompt}
    
    response = client.post("/improve", json=test_prompt)
    assert response.status_code == 200
    
    data = response.json()
    assert data["improved_prompt"].startswith("Make it clearer: ")
    assert len(data["improved_prompt"]) > len(long_prompt)
