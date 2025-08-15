# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestAPI:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_create_project(self):
        project_data = {
            "name": "Test Project",
            "requirements": "Build a simple web app"
        }

        response = client.post("/api/projects", json=project_data)
        assert response.status_code == 200

        data = response.json()
        assert "project_id" in data
        assert data["status"] == "created"

    def test_get_project(self):
        # First create a project
        project_data = {
            "name": "Test Project",
            "requirements": "Build a simple web app"
        }

        create_response = client.post("/api/projects", json=project_data)
        project_id = create_response.json()["project_id"]

        # Then retrieve it
        response = client.get(f"/api/projects/{project_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Test Project"
        assert data["requirements"] == "Build a simple web app"
