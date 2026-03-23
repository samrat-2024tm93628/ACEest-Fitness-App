import pytest
from app import app

@pytest.fixture
def client():
    """Setup a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# ──────────────────────────────────────────────
# GET /health
# ──────────────────────────────────────────────
def test_health_check(client):
    """Validates the health endpoint returns 200 with correct fields."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == "healthy"
    assert response.json['service'] == "ACEest Fitness"


# ──────────────────────────────────────────────
# GET /programs
# ──────────────────────────────────────────────
def test_get_all_programs_status(client):
    """Validates the programs endpoint returns 200."""
    response = client.get('/programs')
    assert response.status_code == 200

def test_get_all_programs_content(client):
    """Validates all 3 programs are returned."""
    response = client.get('/programs')
    data = response.json
    assert "Fat Loss (FL)" in data
    assert "Muscle Gain (MG)" in data
    assert "Beginner (BG)" in data

def test_programs_have_required_fields(client):
    """Validates each program contains workout, diet, and color keys."""
    response = client.get('/programs')
    for program in response.json.values():
        assert 'workout' in program
        assert 'diet' in program
        assert 'color' in program


# ──────────────────────────────────────────────
# POST /calculate (BMI)
# ──────────────────────────────────────────────
def test_bmi_calculation(client):
    """Validates correct BMI: 70kg / (1.7m)^2 = 24.22."""
    response = client.post('/calculate', json={"weight": 70, "height": 170})
    assert response.status_code == 200
    assert response.json['bmi'] == 24.22

def test_bmi_response_has_message(client):
    """Validates the BMI response includes a message field."""
    response = client.post('/calculate', json={"weight": 70, "height": 170})
    assert 'message' in response.json

def test_bmi_missing_payload_returns_400(client):
    """Validates that an empty payload returns 400."""
    response = client.post('/calculate', json={})
    assert response.status_code == 400
    assert 'error' in response.json

def test_bmi_missing_weight_returns_400(client):
    """Validates that a missing weight field returns 400."""
    response = client.post('/calculate', json={"height": 170})
    assert response.status_code == 400

def test_bmi_missing_height_returns_400(client):
    """Validates that a missing height field returns 400."""
    response = client.post('/calculate', json={"weight": 70})
    assert response.status_code == 400

def test_bmi_no_json_returns_error(client):
    """Validates that a request with no JSON body returns a 4xx error.
    Flask returns 415 Unsupported Media Type when no Content-Type is set."""
    response = client.post('/calculate')
    assert response.status_code in (400, 415)


# ──────────────────────────────────────────────
# GET /export/csv
# ──────────────────────────────────────────────
def test_export_csv_status(client):
    """Validates the CSV export endpoint returns 200."""
    response = client.get('/export/csv')
    assert response.status_code == 200

def test_export_csv_content_type(client):
    """Validates the response is served as text/csv."""
    response = client.get('/export/csv')
    assert 'text/csv' in response.content_type

def test_export_csv_has_header_row(client):
    """Validates the CSV contains the expected header row."""
    response = client.get('/export/csv')
    content = response.data.decode('utf-8')
    assert 'Program' in content
    assert 'Workout' in content
    assert 'Diet' in content

def test_export_csv_has_program_data(client):
    """Validates the CSV contains at least one program name."""
    response = client.get('/export/csv')
    content = response.data.decode('utf-8')
    assert 'Fat Loss (FL)' in content


# ──────────────────────────────────────────────
# POST /client
# ──────────────────────────────────────────────
def test_save_client_status(client):
    """Validates that saving a client returns 201."""
    response = client.post('/client', json={"name": "Sam", "bmi": 22.5})
    assert response.status_code == 201

def test_save_client_response_message(client):
    """Validates the save client response contains the confirmation message."""
    response = client.post('/client', json={"name": "Sam", "bmi": 22.5})
    assert 'message' in response.json
    assert response.json['message'] == "Client data persisted to SQLite"


# ──────────────────────────────────────────────
# GET /status
# ──────────────────────────────────────────────
def test_gym_status_returns_200(client):
    """Validates the gym status endpoint returns 200."""
    response = client.get('/status')
    assert response.status_code == 200

def test_gym_status_has_capacity(client):
    """Validates the capacity field is present and numeric."""
    response = client.get('/status')
    assert 'capacity' in response.json
    assert isinstance(response.json['capacity'], int)

def test_gym_status_has_required_fields(client):
    """Validates all expected metric fields are present."""
    response = client.get('/status')
    data = response.json
    assert 'current_utilization' in data
    assert 'status' in data
    assert 'recommendation' in data