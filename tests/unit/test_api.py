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
    assert response.json() == {"message": "Self-Learning Prompt Engineering System API", "version": "1.0.0"}

def test_create_prompt_endpoint():
    """Test that the create prompt endpoint works correctly."""
    test_prompt = {"text": "Write a story about a cat"}
    
    response = client.post("/v1/prompts", json=test_prompt)
    assert response.status_code == 200
    
    data = response.json()
    assert "promptId" in data
    assert "versionId" in data
    assert "versionNo" in data
    assert "improved" in data
    assert "explanation" in data
    assert "judge" in data
    
    # Check that the improved prompt is different from original
    assert data["improved"] != test_prompt["text"]
    
    # Check that explanation has expected structure
    assert "bullets" in data["explanation"]
    assert isinstance(data["explanation"]["bullets"], list)
    
    # Check that judge has expected structure
    judge_data = data["judge"]
    assert "clarity" in judge_data
    assert "specificity" in judge_data
    assert "actionability" in judge_data
    assert "structure" in judge_data
    assert "context_use" in judge_data
    assert "total" in judge_data
    assert "feedback" in judge_data

def test_create_prompt_empty_text():
    """Test the create prompt endpoint with empty text."""
    test_prompt = {"text": ""}
    
    response = client.post("/v1/prompts", json=test_prompt)
    assert response.status_code == 200
    
    data = response.json()
    assert "improved" in data
    assert "judge" in data

def test_create_prompt_invalid_json():
    """Test the create prompt endpoint with invalid JSON."""
    response = client.post("/v1/prompts", data="invalid json")
    assert response.status_code == 422

def test_create_prompt_long_text():
    """Test the create prompt endpoint with a very long prompt."""
    long_prompt = "Write a story about a cat " * 100
    test_prompt = {"text": long_prompt}
    
    response = client.post("/v1/prompts", json=test_prompt)
    assert response.status_code == 200
    
    data = response.json()
    assert "improved" in data
    assert len(data["improved"]) > 0

def test_get_prompt_details():
    """Test getting prompt details."""
    # First create a prompt
    test_prompt = {"text": "Write a Python function"}
    response = client.post("/v1/prompts", json=test_prompt)
    assert response.status_code == 200
    
    prompt_id = response.json()["promptId"]
    
    # Then get its details
    response = client.get(f"/v1/prompts/{prompt_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert "original" in data
    assert "best" in data
    assert "history" in data
    
    # Check original structure
    assert "text" in data["original"]
    assert "created_at" in data["original"]
    
    # Check history structure
    assert isinstance(data["history"], list)
    assert len(data["history"]) > 0
    
    # Check first history item
    first_version = data["history"][0]
    assert "versionId" in first_version
    assert "versionNo" in first_version
    assert "text" in first_version
    assert "explanation" in first_version
    assert "source" in first_version
    assert "created_at" in first_version
    assert "scores" in first_version

def test_get_nonexistent_prompt():
    """Test getting details for a nonexistent prompt."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/v1/prompts/{fake_id}")
    assert response.status_code == 404

def test_improve_existing_prompt():
    """Test improving an existing prompt."""
    # First create a prompt
    test_prompt = {"text": "Help me code"}
    response = client.post("/v1/prompts", json=test_prompt)
    assert response.status_code == 200
    
    prompt_id = response.json()["promptId"]
    
    # Then improve it
    response = client.post(f"/v1/prompts/{prompt_id}/improve", json={"strategy": "v1"})
    assert response.status_code == 200
    
    data = response.json()
    assert "versionId" in data
    assert "versionNo" in data
    assert "text" in data
    assert "explanation" in data
    assert "judge" in data

def test_metrics_endpoint():
    """Test the metrics endpoint."""
    response = client.get("/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data or "status" in data
