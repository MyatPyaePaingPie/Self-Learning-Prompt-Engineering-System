import pytest
import requests
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

def test_api_availability():
    """Test that the API is available and responding."""
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        assert response.status_code == 200
        assert response.json() == {"message": "yay! API is working!"}
    except requests.exceptions.ConnectionError:
        pytest.skip("API server not running - start with: python -m uvicorn api:app --reload")

def test_end_to_end_flow():
    """Test the complete flow from input to output."""
    try:
        # Test the improve endpoint
        test_prompt = {"prompt": "Write a story about a cat"}
        response = requests.post(
            "http://127.0.0.1:8000/improve", 
            json=test_prompt,
            timeout=5
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "improved_prompt" in data
        assert data["improved_prompt"].startswith("Make it clearer: ")
        
    except requests.exceptions.ConnectionError:
        pytest.skip("API server not running - start with: python -m uvicorn api:app --reload")

def test_api_docs_available():
    """Test that the API documentation is accessible."""
    try:
        response = requests.get("http://127.0.0.1:8000/docs", timeout=5)
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    except requests.exceptions.ConnectionError:
        pytest.skip("API server not running - start with: python -m uvicorn api:app --reload")
