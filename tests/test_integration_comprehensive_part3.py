# tests/test_integration_comprehensive_part3.py
# Final part of comprehensive integration tests

import pytest
import asyncio
import json
import time
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, Mock
import sqlite3
import threading


class TestErrorHandlingContinued:
    """Test error handling and recovery scenarios - continued"""
    
    def test_concurrent_agent_processing(self, test_db, mock_llm_client):
        """Test multiple agents processing concurrently"""
        from agents import AnalystAgent, ArchitectAgent
        
        analyst = AnalystAgent(mock_llm_client, test_db)
        architect = ArchitectAgent(mock_llm_client, test_db)
        
        project1_id = test_db.create_project("Concurrent Test 1", "Build app 1")
        project2_id = test_db.create_project("Concurrent Test 2", "Build app 2")
        
        async def test_concurrent():
            # Create messages for both agents
            analyst_message = {
                "id": "msg1",
                "project_id": project1_id,
                "message_type": "start_analysis",
                "content": {"requirements": "Build web app"},
                "confidence": 1.0
            }
            
            architect_message = {
                "id": "msg2", 
                "project_id": project2_id,
                "message_type": "handoff",
                "content": {"analysis": "Complete", "user_stories": []},
                "confidence": 0.8
            }
            
            # Process concurrently
            results = await asyncio.gather(
                analyst.process_message(analyst_message),
                architect.process_message(architect_message),
                return_exceptions=True
            )
            
            # Both should succeed
            assert len(results) == 2
            assert all(isinstance(r, dict) and r.get("status") == "complete" for r in results)
            
            # Verify messages were sent to next agents
            architect_msgs = test_db.get_pending_messages("architect")
            developer_msgs = test_db.get_pending_messages("developer")
            
            assert len(architect_msgs) == 1  # From analyst
            assert len(developer_msgs) == 1   # From architect
        
        asyncio.run(test_concurrent())


class TestEndToEnd:
    """End-to-end integration tests"""
    
    def test_complete_project_workflow(self, test_client, test_db, mock_llm_client, sample_project_data):
        """Test complete project workflow from creation to completion"""
        # Step 1: Create project
        response = test_client.post("/api/projects", json=sample_project_data)
        assert response.status_code == 200
        
        project_id = response.json()["project_id"]
        
        # Step 2: Verify project was created
        project_response = test_client.get(f"/api/projects/{project_id}")
        assert project_response.status_code == 200
        
        project = project_response.json()
        assert project["name"] == sample_project_data["name"]
        assert project["status"] == "active"
        
        # Step 3: Simulate workflow progress by adding messages manually
        # (In real system, background task would do this)
        
        # Analyst completes analysis
        analyst_msg_id = test_db.add_message(
            project_id=project_id,
            from_agent="analyst",
            to_agent="architect",
            message_type="handoff",
            content={
                "analysis": "E-commerce requirements analyzed successfully",
                "user_stories": [
                    {"title": "User Registration", "description": "Users can create accounts"},
                    {"title": "Product Browse", "description": "Users can view products"},
                    {"title": "Shopping Cart", "description": "Users can add items to cart"}
                ],
                "risks": [
                    {"risk": "Payment security", "mitigation": "Use trusted payment gateway"}
                ],
                "success_metrics": ["User conversion rate", "Transaction volume"],
                "confidence": 0.85
            },
            confidence=0.85
        )
        
        # Architect completes design
        architect_msg_id = test_db.add_message(
            project_id=project_id,
            from_agent="architect", 
            to_agent="developer",
            message_type="handoff",
            content={
                "architecture": "Three-tier web application with React frontend",
                "components": [
                    {"name": "Frontend", "tech": "React", "purpose": "User interface"},
                    {"name": "API", "tech": "FastAPI", "purpose": "Business logic"},
                    {"name": "Database", "tech": "SQLite", "purpose": "Data storage"}
                ],
                "tech_stack": {
                    "frontend": "React with Tailwind CSS",
                    "backend": "FastAPI with Pydantic",
                    "database": "SQLite with migrations"
                },
                "confidence": 0.9
            },
            confidence=0.9
        )
        
        # Developer generates code
        developer_msg_id = test_db.add_message(
            project_id=project_id,
            from_agent="developer",
            to_agent="tester", 
            message_type="handoff",
            content={
                "files": [
                    {"path": "main.py", "content": "# FastAPI application\nfrom fastapi import FastAPI\napp = FastAPI()"},
                    {"path": "models.py", "content": "# Data models\nfrom pydantic import BaseModel"},
                    {"path": "frontend/App.jsx", "content": "// React application\nimport React from 'react'"}
                ],
                "documentation": "E-commerce application with user auth and product management",
                "confidence": 0.8
            },
            confidence=0.8
        )
        
        # Tester validates code
        tester_msg_id = test_db.add_message(
            project_id=project_id,
            from_agent="tester",
            to_agent="system",
            message_type="completion",
            content={
                "test_results": {
                    "total_tests": 15,
                    "passed": 14, 
                    "failed": 1,
                    "coverage": 87
                },
                "quality_metrics": {
                    "maintainability": "High",
                    "complexity": "Medium",
                    "security_score": 8.2
                },
                "recommendations": [
                    "Add input validation for user registration",
                    "Implement rate limiting for API endpoints"
                ],
                "confidence": 0.88
            },
            confidence=0.88
        )
        
        # Step 4: Verify messages were created
        messages_response = test_client.get(f"/api/projects/{project_id}/messages")
        assert messages_response.status_code == 200
        
        messages = messages_response.json()["messages"]
        assert len(messages) == 4
        
        # Verify message progression
        agent_sequence = [msg["from_agent"] for msg in reversed(messages)]  # Reverse for chronological order
        assert agent_sequence == ["analyst", "architect", "developer", "tester"]
        
        # Step 5: Verify final message contains completion data
        final_message = next(msg for msg in messages if msg["from_agent"] == "tester")
        assert final_message["message_type"] == "completion"
        assert "test_results" in final_message["content"]
        assert final_message["content"]["test_results"]["total_tests"] == 15
    
    def test_human_intervention_workflow(self, test_client, test_db, sample_project_data):
        """Test workflow with human intervention"""
        # Create project
        response = test_client.post("/api/projects", json=sample_project_data)
        project_id = response.json()["project_id"]
        
        # Simulate agent needing human decision
        conn = sqlite3.connect(test_db.db_path)
        action_id = "action_123"
        conn.execute("""
            INSERT INTO actions (id, project_id, title, description, priority, status, options)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            action_id,
            project_id,
            "Database Selection Required",
            "Choose between SQLite for simplicity or PostgreSQL for scalability",
            "high",
            "pending",
            json.dumps([
                {"value": "sqlite", "label": "SQLite (Simple, file-based)"},
                {"value": "postgresql", "label": "PostgreSQL (Scalable, robust)"}
            ])
        ))
        conn.commit()
        conn.close()
        
        # Get pending actions
        actions_response = test_client.get(f"/api/projects/{project_id}/actions")
        assert actions_response.status_code == 200
        
        actions = actions_response.json()["actions"]
        assert len(actions) == 1
        
        action = actions[0]
        assert action["title"] == "Database Selection Required"
        assert action["priority"] == "high"
        assert len(action["options"]) == 2
        
        # Human responds to action
        response = test_client.post("/api/actions/respond", json={
            "action_id": action_id,
            "response": "postgresql"
        })
        assert response.status_code == 200
        assert response.json()["status"] == "resolved"
        
        # Verify action was resolved
        conn = sqlite3.connect(test_db.db_path)
        cursor = conn.execute("SELECT status, response FROM actions WHERE id = ?", (action_id,))
        row = cursor.fetchone()
        conn.close()
        
        assert row[0] == "resolved"
        assert row[1] == "postgresql"
        
        # Verify no pending actions remain
        actions_response = test_client.get(f"/api/projects/{project_id}/actions")
        pending_actions = actions_response.json()["actions"]
        assert len(pending_actions) == 0
    
    def test_error_recovery_workflow(self, test_client, test_db, sample_project_data):
        """Test workflow recovery from errors"""
        # Create project
        response = test_client.post("/api/projects", json=sample_project_data)
        project_id = response.json()["project_id"]
        
        # Add message that would cause processing error
        error_msg_id = test_db.add_message(
            project_id=project_id,
            from_agent="system",
            to_agent="nonexistent_agent",  # This agent doesn't exist
            message_type="test_error",
            content={"test": "error scenario"},
            confidence=1.0
        )
        
        # Simulate message processing error
        test_db.update_message_status(error_msg_id, "error")
        
        # Add recovery message
        recovery_msg_id = test_db.add_message(
            project_id=project_id,
            from_agent="system",
            to_agent="analyst",  # Valid agent
            message_type="start_analysis",
            content={"requirements": sample_project_data["requirements"]},
            confidence=1.0
        )
        
        # Verify both messages exist with correct statuses
        messages_response = test_client.get(f"/api/projects/{project_id}/messages")
        messages = messages_response.json()["messages"]
        assert len(messages) == 2
        
        # Find error and recovery messages
        error_msg = next(msg for msg in messages if msg["id"] == error_msg_id)
        recovery_msg = next(msg for msg in messages if msg["id"] == recovery_msg_id)
        
        assert error_msg["status"] == "error"
        assert error_msg["to_agent"] == "nonexistent_agent"
        
        assert recovery_msg["status"] == "pending"
        assert recovery_msg["to_agent"] == "analyst"
    
    def test_performance_under_load(self, test_client, test_db):
        """Test system performance under load"""
        import time
        import threading
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        def create_project(i):
            """Create a project and measure response time"""
            start_time = time.time()
            
            project_data = {
                "name": f"Load Test Project {i}",
                "requirements": f"Build application {i} with specific requirements"
            }
            
            response = test_client.post("/api/projects", json=project_data)
            end_time = time.time()
            
            return {
                "project_id": response.json().get("project_id") if response.status_code == 200 else None,
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "index": i
            }
        
        # Create multiple projects concurrently
        num_projects = 20
        max_workers = 5
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(create_project, i) for i in range(num_projects)]
            results = [future.result() for future in as_completed(futures)]
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful_results = [r for r in results if r["status_code"] == 200]
        failed_results = [r for r in results if r["status_code"] != 200]
        
        success_rate = len(successful_results) / len(results)
        avg_response_time = sum(r["response_time"] for r in successful_results) / len(successful_results)
        max_response_time = max(r["response_time"] for r in successful_results)
        
        # Performance assertions
        assert success_rate >= 0.95, f"Success rate {success_rate} below 95%"
        assert avg_response_time < 2.0, f"Average response time {avg_response_time} above 2 seconds"
        assert max_response_time < 5.0, f"Max response time {max_response_time} above 5 seconds"
        assert total_time < 15.0, f"Total execution time {total_time} above 15 seconds"
        
        # Verify all projects were created in database
        conn = sqlite3.connect(test_db.db_path)
        cursor = conn.execute("SELECT COUNT(*) FROM projects")
        project_count = cursor.fetchone()[0]
        conn.close()
        
        assert project_count == len(successful_results)
        
        print(f"Performance test results:")
        print(f"  - Total projects: {num_projects}")
        print(f"  - Success rate: {success_rate:.2%}")
        print(f"  - Average response time: {avg_response_time:.3f}s")
        print(f"  - Max response time: {max_response_time:.3f}s")
        print(f"  - Total time: {total_time:.3f}s")


class TestDataConsistency:
    """Test data consistency across the system"""
    
    def test_message_thread_consistency(self, test_db):
        """Test message threading and conversation consistency"""
        project_id = test_db.create_project("Thread Test", "Test message threading")
        
        # Create conversation thread
        msg1_id = test_db.add_message(
            project_id=project_id,
            from_agent="analyst",
            to_agent="architect",
            message_type="handoff",
            content={"analysis": "Initial analysis"},
            confidence=0.8
        )
        
        msg2_id = test_db.add_message(
            project_id=project_id,
            from_agent="architect", 
            to_agent="developer",
            message_type="handoff",
            content={"architecture": "System design", "previous_msg": msg1_id},
            confidence=0.9
        )
        
        msg3_id = test_db.add_message(
            project_id=project_id,
            from_agent="developer",
            to_agent="tester",
            message_type="handoff", 
            content={"code": "Implementation", "previous_msg": msg2_id},
            confidence=0.85
        )
        
        # Verify message chain consistency
        all_messages = test_db.get_pending_messages()
        project_messages = [msg for msg in all_messages if msg["project_id"] == project_id]
        
        assert len(project_messages) == 3
        
        # Verify chronological order
        timestamps = [msg["timestamp"] for msg in project_messages]
        assert timestamps == sorted(timestamps)
        
        # Verify agent handoff chain
        agents = [(msg["from_agent"], msg["to_agent"]) for msg in sorted(project_messages, key=lambda x: x["timestamp"])]
        expected_chain = [("analyst", "architect"), ("architect", "developer"), ("developer", "tester")]
        assert agents == expected_chain
    
    def test_project_state_consistency(self, test_db):
        """Test project state consistency across operations"""
        # Create project
        project_id = test_db.create_project("State Test", "Test state consistency")
        
        # Get initial project state
        initial_project = test_db.get_project(project_id)
        assert initial_project["status"] == "active"
        assert initial_project["version"] == 1
        
        # Add messages and actions
        test_db.add_message(
            project_id=project_id,
            from_agent="analyst",
            to_agent="architect",
            message_type="handoff",
            content={"data": "test"},
            confidence=0.8
        )
        
        conn = sqlite3.connect(test_db.db_path)
        conn.execute("""
            INSERT INTO actions (id, project_id, title, description, priority)
            VALUES ('action1', ?, 'Test Action', 'Test Description', 'medium')
        """, (project_id,))
        conn.commit()
        
        # Update project
        conn.execute("UPDATE projects SET status = 'in_progress' WHERE id = ?", (project_id,))
        conn.commit()
        conn.close()
        
        # Verify state consistency
        updated_project = test_db.get_project(project_id)
        assert updated_project["id"] == project_id
        assert updated_project["status"] == "in_progress"
        assert updated_project["name"] == initial_project["name"]
        assert updated_project["requirements"] == initial_project["requirements"]
        
        # Verify related data still exists
        messages = test_db.get_pending_messages()
        project_messages = [msg for msg in messages if msg["project_id"] == project_id]
        assert len(project_messages) == 1
        
        conn = sqlite3.connect(test_db.db_path)
        cursor = conn.execute("SELECT COUNT(*) FROM actions WHERE project_id = ?", (project_id,))
        action_count = cursor.fetchone()[0]
        conn.close()
        assert action_count == 1


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
