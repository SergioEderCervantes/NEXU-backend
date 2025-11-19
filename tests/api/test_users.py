import pytest
from unittest.mock import patch
from app.main import create_app
from app.domain.entities import User

@pytest.fixture
def client():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_users():
    """Return a list of sample User objects."""
    return [
        User(id=1, nombre_usuario="test1", correo_electronico="test1@test.com", contrasena_hash="hash1", nombre_completo="Test One"),
        User(id=2, nombre_usuario="test2", correo_electronico="test2@test.com", contrasena_hash="hash2", nombre_completo="Test Two")
    ]

@patch('app.api.users.user_repository')
def test_get_all_users_success(mock_repo, client, sample_users):
    """Test the GET /users/ endpoint successfully returns a list of users."""
    # Arrange
    mock_repo.find_all.return_value = sample_users
    
    # Act
    response = client.get('/users/')
    
    # Assert
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    
    json_data = response.get_json()
    assert len(json_data) == 2
    assert json_data[0]['id'] == 1
    assert json_data[0]['nombre_usuario'] == 'test1'
    assert json_data[1]['id'] == 2
    assert json_data[1]['nombre_completo'] == 'Test Two'
    mock_repo.find_all.assert_called_once()

@patch('app.api.users.user_repository')
def test_get_all_users_empty(mock_repo, client):
    """Test the GET /users/ endpoint when no users are found."""
    # Arrange
    mock_repo.find_all.return_value = []
    
    # Act
    response = client.get('/users/')
    
    # Assert
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.get_json() == []
    mock_repo.find_all.assert_called_once()

@patch('app.api.users.user_repository')
def test_get_all_users_repository_error(mock_repo, client):
    """Test the GET /users/ endpoint when the repository raises an exception."""
    # Arrange
    mock_repo.find_all.side_effect = Exception("Database connection failed")
    
    # Act
    response = client.get('/users/')
    
    # Assert
    assert response.status_code == 500
    assert response.content_type == 'application/json'
    json_data = response.get_json()
    assert json_data == {"error": "An unexpected error occurred."}
    mock_repo.find_all.assert_called_once()
