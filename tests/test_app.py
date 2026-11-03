import pytest
from app.main import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test that index page loads successfully and contains title."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Ganesh DevOps" in response.data

def test_health_check(client):
    """Test the /health endpoint used by Docker and Jenkins smoke testing."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "UP"
    assert data["service"] == "ganesh_devops_project"
    assert "timestamp" in data
    assert data["checks"]["web_server"] == "healthy"

def test_metrics_api(client):
    """Test the /api/metrics endpoint returns system stats."""
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    metrics = data["metrics"]
    assert "hostname" in metrics
    assert "python_version" in metrics
    assert "uptime_seconds" in metrics

def test_get_tasks(client):
    """Test retrieving tasks list."""
    response = client.get("/api/tasks")
    assert response.status_code == 200
    data = response.get_json()
    assert "tasks" in data
    assert len(data["tasks"]) >= 3

def test_create_task_success(client):
    """Test creating a new task."""
    payload = {
        "title": "Configure SonarQube Scanner",
        "category": "Code Quality",
        "status": "Planned"
    }
    response = client.post("/api/tasks", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["task"]["title"] == "Configure SonarQube Scanner"
    assert data["task"]["category"] == "Code Quality"

def test_create_task_validation(client):
    """Test validation when title is missing."""
    response = client.post("/api/tasks", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_info_endpoint(client):
    """Test the /api/info metadata endpoint."""
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.get_json()
    assert "project_name" in data
    assert "stack" in data
