import pytest
from app.main import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """
    GIVEN a Flask application
    WHEN the '/health/' page is requested (GET)
    THEN check that the response is valid
    """
    response = client.get('/health/')
    assert response.status_code == 200
    assert b"Api Funcionando en Flask!!" in response.data
