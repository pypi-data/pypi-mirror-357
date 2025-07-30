"""
Pytest configuration and shared fixtures for the Cognify SDK tests.
"""

import os
import pytest
from unittest.mock import Mock, patch

from cognify_sdk import CognifyClient, CognifyConfig


@pytest.fixture
def mock_api_key():
    """Mock API key for testing."""
    return "cog_test_key_12345"


@pytest.fixture
def test_config(mock_api_key):
    """Test configuration with mock values."""
    return CognifyConfig(
        api_key=mock_api_key,
        base_url="https://api.test.cognify.ai",
        timeout=10.0,
        max_retries=1,
        debug=True,
    )


@pytest.fixture
def mock_client(test_config):
    """Mock Cognify client for testing."""
    with patch("cognify_sdk.client.HTTPClient") as mock_http:
        client = CognifyClient(
            api_key=test_config.api_key,
            base_url=test_config.base_url,
            timeout=test_config.timeout,
            max_retries=test_config.max_retries,
            debug=test_config.debug,
        )
        client.http = mock_http.return_value
        yield client


@pytest.fixture
def mock_http_response():
    """Mock HTTP response for testing."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "data": {"test": "data"},
        "message": "Success",
    }
    mock_response.headers = {"x-request-id": "test-request-id"}
    return mock_response


@pytest.fixture
def mock_error_response():
    """Mock HTTP error response for testing."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {
        "success": False,
        "error": "Bad Request",
        "message": "Invalid parameters",
    }
    mock_response.headers = {"x-request-id": "test-request-id"}
    return mock_response


@pytest.fixture(autouse=True)
def clean_environment():
    """Clean environment variables before each test."""
    # Store original values
    original_env = {}
    cognify_vars = [key for key in os.environ.keys() if key.startswith("COGNIFY_")]
    
    for var in cognify_vars:
        original_env[var] = os.environ[var]
        del os.environ[var]
    
    yield
    
    # Restore original values
    for var, value in original_env.items():
        os.environ[var] = value


@pytest.fixture
def temp_env_vars():
    """Context manager for temporary environment variables."""
    class TempEnvVars:
        def __init__(self):
            self.original = {}
        
        def set(self, **kwargs):
            for key, value in kwargs.items():
                if key in os.environ:
                    self.original[key] = os.environ[key]
                os.environ[key] = str(value)
        
        def clear(self):
            for key in list(os.environ.keys()):
                if key.startswith("COGNIFY_"):
                    if key in self.original:
                        os.environ[key] = self.original[key]
                    else:
                        del os.environ[key]
    
    return TempEnvVars()


# Test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.performance = pytest.mark.performance
