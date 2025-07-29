import pytest
from drf_standardized_responses import responses

def test_package_imports():
    """Test that the package can be imported successfully."""
    assert hasattr(responses, 'StandardResponse')
    assert hasattr(responses.StandardResponse, 'success')
    assert hasattr(responses.StandardResponse, 'error')
    assert hasattr(responses.StandardResponse, 'from_response')

def test_version():
    """Test that the package has a version number."""
    import drf_standardized_responses
    assert drf_standardized_responses.__version__
