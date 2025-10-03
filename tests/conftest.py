import pytest
import sys
import os

# Add project directories to Python path
project_root = os.path.dirname(os.path.dirname(__file__))
backend_path = os.path.join(project_root, 'backend')
apps_path = os.path.join(project_root, 'apps', 'web')

sys.path.insert(0, backend_path)
sys.path.insert(0, apps_path)

@pytest.fixture
def sample_prompt():
    """Sample prompt for testing."""
    return "Write a story about a cat"

@pytest.fixture
def sample_prompt_data():
    """Sample prompt data for API testing."""
    return {"prompt": "Write a story about a cat"}

@pytest.fixture
def empty_prompt_data():
    """Empty prompt data for testing."""
    return {"prompt": ""}
