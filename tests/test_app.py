"""
Unit tests for the main application.
"""
import pytest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from config import TestingConfig


@pytest.fixture
def client():
    """Create test client."""
    app.config.from_object(TestingConfig)
    with app.test_client() as client:
        yield client


@pytest.fixture
def app_context():
    """Create application context."""
    with app.app_context():
        yield


def test_home_page(client):
    """Test home page renders correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Document Generator' in response.data
    assert b'WP' in response.data or b'Writ Petition' in response.data


def test_valid_form_page(client):
    """Test valid document type form page."""
    response = client.get('/form/WP')
    assert response.status_code == 200
    assert b'Create' in response.data
    assert b'Writ Petition' in response.data


def test_invalid_form_page(client):
    """Test invalid document type redirects."""
    response = client.get('/form/INVALID_TYPE')
    assert response.status_code == 302  # Redirect


def test_generate_without_data(client):
    """Test document generation without required data."""
    response = client.post('/generate', data={
        'doc_type': 'WP'
    }, follow_redirects=True)
    # Should redirect back to form or show error
    assert response.status_code == 200


def test_health_check():
    """Test application imports correctly."""
    assert app is not None
    assert app.config is not None


def test_config_loading():
    """Test configuration loading."""
    app.config.from_object(TestingConfig)
    assert app.config['TESTING'] is True
    assert app.config['WTF_CSRF_ENABLED'] is False

