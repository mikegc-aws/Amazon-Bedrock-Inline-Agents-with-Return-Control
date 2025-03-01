import pytest
from unittest.mock import patch, MagicMock

# Sample functions for testing
def sample_function() -> dict:
    """A sample function that returns a dictionary"""
    return {"status": "success"}

def sample_function_with_params(param1: str, param2: int = 123) -> dict:
    """A sample function that takes parameters and returns a dictionary
    
    :param param1: A string parameter
    :param param2: An integer parameter
    """
    return {"param1": param1, "param2": param2}

@pytest.fixture
def mock_boto3_session():
    """Mock boto3 session for testing"""
    with patch("boto3.Session") as mock_session:
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        yield mock_session, mock_client 