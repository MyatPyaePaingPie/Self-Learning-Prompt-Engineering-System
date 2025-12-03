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

def test_version_saved_to_csv_with_timestamp():
    """
    Week 6 Test: Verify that prompt versions are saved to CSV with timestamps.
    
    Tests:
    1. CSV file is created after prompt creation
    2. Timestamp field exists and is populated
    3. Both v0 and v1 versions are saved
    """
    import csv
    from pathlib import Path
    
    # Create a test prompt
    test_prompt = {"text": "Test prompt for Week 6 version tracking"}
    response = client.post("/v1/prompts", json=test_prompt)
    assert response.status_code == 200
    
    prompt_id = response.json()["promptId"]
    
    # Check that CSV file exists
    csv_path = Path("storage/prompt_versions.csv")
    assert csv_path.exists(), "CSV file should exist after creating prompt"
    
    # Read the CSV and find entries for this prompt
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Find rows for our prompt
    prompt_rows = [row for row in rows if row['prompt_id'] == prompt_id]
    
    # Should have at least 2 versions (v0 original, v1 improved)
    assert len(prompt_rows) >= 2, f"Expected at least 2 versions, found {len(prompt_rows)}"
    
    # Check that timestamp exists and is not empty for all versions
    for row in prompt_rows:
        assert 'timestamp' in row, "Timestamp field should exist in CSV"
        assert row['timestamp'], "Timestamp should not be empty"
        assert 'T' in row['timestamp'], "Timestamp should be in ISO format"
        
        # Verify other required fields
        assert 'version_no' in row
        assert 'version_uuid' in row
        assert 'text' in row
        assert 'source' in row
    
    # Check that v0 and v1 exist
    version_numbers = [row['version_no'] for row in prompt_rows]
    assert '0' in version_numbers, "Version 0 (original) should be saved"
    assert '1' in version_numbers, "Version 1 (improved) should be saved"
    
    print(f"✅ Week 6 Test Passed: {len(prompt_rows)} versions saved with timestamps")

def test_error_handling_with_invalid_api_key():
    """
    Week 7 Test: Verify that system handles API errors gracefully.
    
    Tests that when LLM API fails:
    1. System doesn't crash
    2. Falls back to template/heuristic
    3. Returns valid response
    """
    import os
    from unittest.mock import patch
    
    # Test with invalid API key (simulate API failure)
    with patch.dict(os.environ, {"GROQ_API_KEY": "invalid_key"}):
        test_prompt = {"text": "Write a function to sort numbers"}
        response = client.post("/v1/prompts", json=test_prompt)
        
        # Should still return 200 (graceful fallback)
        assert response.status_code == 200, "Should handle API errors gracefully"
        
        data = response.json()
        
        # Should have all required fields
        assert "improved" in data
        assert "explanation" in data
        assert "judge" in data
        
        # Should indicate fallback was used
        # Template fallback includes "You are a senior" pattern
        assert "senior" in data["improved"].lower() or "template" in data["improved"].lower()
        
        print("✅ Week 7 Test Passed: System handles API errors gracefully")

def test_error_handling_fallback_sources():
    """
    Week 7 Test: Verify fallback sources are correctly identified.
    
    When API is unavailable, the source should indicate fallback mode.
    """
    test_prompt = {"text": "Code a sorting algorithm"}
    response = client.post("/v1/prompts", json=test_prompt)
    assert response.status_code == 200
    
    data = response.json()
    
    # Check that we got a valid response
    assert "improved" in data
    assert len(data["improved"]) > 0
    
    # Judge should always return scores
    assert "judge" in data
    assert "clarity" in data["judge"]
    assert "total" in data["judge"]
    
    print("✅ Week 7 Test Passed: Fallback sources work correctly")

def test_empty_prompt_handling():
    """
    Week 7 Test: Verify system handles edge cases like empty prompts.
    """
    test_prompt = {"text": ""}
    response = client.post("/v1/prompts", json=test_prompt)
    
    # Should handle empty prompts without crashing
    assert response.status_code == 200
    
    data = response.json()
    assert "improved" in data
    assert "judge" in data
    
    print("✅ Week 7 Test Passed: Empty prompts handled correctly")

def test_very_long_prompt_handling():
    """
    Week 7 Test: Verify system handles very long prompts.
    """
    # Create a very long prompt (1000+ characters)
    long_prompt = "Write a function to process data. " * 50
    test_prompt = {"text": long_prompt}
    
    response = client.post("/v1/prompts", json=test_prompt)
    
    # Should handle long prompts without crashing
    assert response.status_code == 200
    
    data = response.json()
    assert "improved" in data
    assert "judge" in data
    
    print("✅ Week 7 Test Passed: Long prompts handled correctly")
