# tests/test_integration.py
import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from main import app


class TestIntegration:

    def setup_method(self):
        self.client = TestClient(app)

    def test_complete_workflow(self):
        """Test the complete agent workflow"""
        # 1. Create project
        project_data = {
            "name":
            "Test E-commerce App",
            "requirements":
            "Build a simple e-commerce web application with user authentication, product catalog, and shopping cart functionality."
        }

        response = self.client.post("/api/projects", json=project_data)
        assert response.status_code == 200

        project_id = response.json()["project_id"]

        # 2. Wait a bit for agents to start processing
        import time
        time.sleep(5)

        # 3. Check for messages
        response = self.client.get(f"/api/projects/{project_id}/messages")
        assert response.status_code == 200

        messages = response.json()["messages"]
        assert len(messages) > 0

        # 4. Check if analyst has produced analysis
        analyst_messages = [
            m for m in messages if m["from_agent"] == "analyst"
        ]
        assert len(analyst_messages) > 0

        # 5. Verify message content structure
        for message in analyst_messages:
            assert "content" in message
            assert message["confidence"] is not None

    def test_human_escalation(self):
        """Test human escalation workflow"""
        # This would test scenarios where agents need human input
        # Implementation depends on specific escalation triggers
        pass

    def test_error_handling(self):
        """Test error handling scenarios"""
        # Test invalid project creation
        response = self.client.post("/api/projects",
                                    json={
                                        "name": "",
                                        "requirements": ""
                                    })
        assert response.status_code == 422  # Validation error

        # Test non-existent project
        response = self.client.get("/api/projects/nonexistent")
        assert response.status_code == 404
