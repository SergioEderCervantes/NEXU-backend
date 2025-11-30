import pytest
from unittest.mock import patch
from app.main import create_app
from app.domain.entities import User
from app.domain.exceptions import InvalidCredentialsException

# --- Test Fixtures ---

@pytest.fixture
def client():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config['TESTING'] = True
    
    # Establish an application context before running the tests.
    with app.app_context():
        yield app.test_client()

@pytest.fixture
def sample_users():
    """Return a list of sample User objects for mocking."""
    return [
        User(id=1, name="Admin User", email="admin@example.com", password="password123", is_active=True, gender="other"),
        User(id=2, name="Normal User", email="user@example.com", password="password456", is_active=True, gender="female"),
    ]

# --- Tests for GET /users ---

@patch('app.middleware.auth.UserRepository')
@patch('app.middleware.auth.jwt.decode')
@patch('app.api.users.user_service')
def test_get_all_users_success(mock_user_service, mock_jwt_decode, mock_user_repo, client, sample_users):
    """Test GET /users returns a list of users successfully."""
    # Arrange
    mock_jwt_decode.return_value = {'sub': '1'}
    mock_user_repo.return_value.find_by_id.return_value = sample_users[0]
    mock_user_service.get_all_users.return_value = sample_users
    
    # Act
    response = client.get('/users/', headers={'Authorization': 'Bearer fake_token'})
    
    # Assert
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data) == 2
    assert json_data[0]['email'] == "admin@example.com"
    assert 'password' not in json_data[0]
    assert json_data[1]['name'] == "Normal User"
    mock_user_service.get_all_users.assert_called_once()

@patch('app.middleware.auth.UserRepository')
@patch('app.middleware.auth.jwt.decode')
@patch('app.api.users.user_service')
def test_get_all_users_empty(mock_user_service, mock_jwt_decode, mock_user_repo, client, sample_users):
    """Test GET /users returns an empty list when no users exist."""
    # Arrange
    mock_jwt_decode.return_value = {'sub': '1'}
    mock_user_repo.return_value.find_by_id.return_value = sample_users[0]
    mock_user_service.get_all_users.return_value = []
    
    # Act
    response = client.get('/users/', headers={'Authorization': 'Bearer fake_token'})
    
    # Assert
    assert response.status_code == 200
    assert response.get_json() == []
    mock_user_service.get_all_users.assert_called_once()

@patch('app.middleware.auth.UserRepository')
@patch('app.middleware.auth.jwt.decode')
@patch('app.api.users.user_service')
def test_get_all_users_repository_error(mock_user_service, mock_jwt_decode, mock_user_repo, client, sample_users):
    """Test GET /users handles unexpected errors gracefully."""
    # Arrange
    mock_jwt_decode.return_value = {'sub': '1'}
    mock_user_repo.return_value.find_by_id.return_value = sample_users[0]
    mock_user_service.get_all_users.side_effect = Exception("Database error")
    
    # Act
    response = client.get('/users/', headers={'Authorization': 'Bearer fake_token'})
    
    # Assert
    assert response.status_code == 500
    assert response.get_json() == {"error": "Ocurrió un error inesperado al obtener usuarios."}
    mock_user_service.get_all_users.assert_called_once()


# --- Tests for POST /users/login ---

@patch('app.api.users.login_service')
def test_login_success(mock_login_service, client):
    """Test POST /users/login with correct credentials."""
    # Arrange
    mock_login_service.login.return_value = "fake_jwt_token"
    login_data = {"email": "test@example.com", "password": "correct_password"}
    
    # Act
    response = client.post('/users/login', json=login_data)
    
    # Assert
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['access_token'] == "fake_jwt_token"
    assert json_data['token_type'] == "bearer"
    mock_login_service.login.assert_called_once_with("test@example.com", "correct_password")

@patch('app.api.users.login_service')
def test_login_failure_invalid_credentials(mock_login_service, client):
    """Test POST /users/login with incorrect credentials."""
    # Arrange
    mock_login_service.login.side_effect = InvalidCredentialsException()
    login_data = {"email": "test@example.com", "password": "wrong_password"}
    
    # Act
    response = client.post('/users/login', json=login_data)
    
    # Assert
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['error'] == 'Invalid credentials provided.'
    mock_login_service.login.assert_called_once_with("test@example.com", "wrong_password")

def test_login_bad_request_no_data(client):
    """Test POST /users/login with an empty JSON body."""
    # Act
    response = client.post('/users/login', data='{}', content_type='application/json')
    
    # Assert
    assert response.status_code == 400
    assert response.get_json()['error'] == "Se requiere un cuerpo de solicitud JSON."

def test_login_bad_request_missing_fields(client):
    """Test POST /users/login with missing email or password."""
    # Act (missing password)
    response_no_pass = client.post('/users/login', json={"email": "test@example.com"})
    
    # Assert
    assert response_no_pass.status_code == 400
    assert response_no_pass.get_json()['error'] == "Email y contraseña son requeridos."
    
    # Act (missing email)
    response_no_email = client.post('/users/login', json={"password": "some_password"})
    
    # Assert
    assert response_no_email.status_code == 400
    assert response_no_email.get_json()['error'] == "Email y contraseña son requeridos."

@patch('app.api.users.login_service')
def test_login_unexpected_error(mock_login_service, client):
    """Test POST /users/login handles unexpected server errors."""
    # Arrange
    mock_login_service.login.side_effect = Exception("Something went very wrong")
    login_data = {"email": "test@example.com", "password": "password"}
    
    # Act
    response = client.post('/users/login', json=login_data)
    
    # Assert
    assert response.status_code == 500
    assert response.get_json()['error'] == "Ocurrió un error inesperado al iniciar sesión."
