import pytest
from app import app

@pytest.fixture
def client():
    # Setup a test client for the Flask app
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Requirement: Validate code integrity via health endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == "healthy"

def test_bmi_calculation(client):
    """Requirement: Confirm components perform according to specification."""
    # Testing 70kg and 170cm (1.7m) -> 70 / (1.7^2) = ~24.22
    payload = {"weight": 70, "height": 170}
    response = client.post('/calculate', json=payload)
    assert response.status_code == 200
    assert response.json['bmi'] == 24.22