# tests/test_utilities_complete.py
"""
Complete utility functions and helpers for integration testing
"""

import asyncio
import json
import time
import sqlite3
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, AsyncMock
from contextlib import contextmanager
import tempfile
import os


class TestDataFactory:
    """Factory for creating test data objects"""
    
    @staticmethod
    def create_project_data(name_suffix: str = "") -> Dict[str, str]:
        """Create sample project data"""
        return {
            "name": f"Test Project{' ' + name_suffix if name_suffix else ''}",
            "requirements": f"""
            Build a web application with the following features:
            - User authentication and registration
            - Data management with CRUD operations  
            - Real-time updates and notifications
            - Responsive mobile design
            - Basic analytics and reporting
            
            Technical requirements:
            - Fast response times (< 2 seconds)
            - Support for 50+ concurrent users
            - Modern, clean user interface
            - Secure data handling
            {f'- Specific to: {name_suffix}' if name_suffix else ''}
            """
        }
    
    @staticmethod
    def create_test_content() -> Dict[str, Any]:
        """Create sample test generation content"""
        return {
            "test_files": [
                {
                    "path": "test_main.py",
                    "content": """# API Tests
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Test Application API"

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
"""
                },
                {
                    "path": "test_models.py",
                    "content": """# Model Tests
import pytest
from models import User, UserData

def test_user_model():
    user = User(email="test@example.com", password="secure123")
    assert user.email == "test@example.com"
    assert user.password == "secure123"

def test_user_data_model():
    data = UserData(title="Test", content="Test content")
    assert data.title == "Test"
    assert data.content == "Test content"
"""
                }
            ],
            "test_results": {
                "total_tests": 12,
                "passed": 11,
                "failed": 1,
                "skipped": 0,
                "coverage": 87.5,
                "failed_tests": [
                    {
                        "name": "test_user_authentication",
                        "error": "Authentication endpoint returns 500 instead of expected 401",
                        "file": "test_auth.py",
                        "line": 25
                    }
                ]
            },
            "quality_metrics": {
                "complexity": "Low",
                "maintainability": "High",
                "security_score": 8.2,
                "performance_score": 7.8,
                "code_style_score": 9.1
            },
            "recommendations": [
                "Add input validation for all API endpoints",
                "Implement rate limiting for authentication endpoints",
                "Add comprehensive error handling middleware",
                "Include API documentation with examples"
            ],
            "confidence": 0.88
        }


class MockAgentFactory:
    """Factory for creating mock agents"""
    
    @staticmethod
    def create_mock_analyst(responses: List[Dict[str, Any]] = None) -> Mock:
        """Create mock analyst agent"""
        mock_agent = Mock()
        mock_agent.agent_id = "analyst"
        mock_agent.status = "idle"
        mock_agent.current_task = None
        
        if responses:
            mock_agent.process_message = AsyncMock(side_effect=responses)
        else:
            mock_agent.process_message = AsyncMock(return_value={
                "status": "complete",
                "analysis": TestDataFactory.create_analysis_content(),
                "tokens_used": 150
            })
        
        return mock_agent
    
    @staticmethod
    def create_mock_architect(responses: List[Dict[str, Any]] = None) -> Mock:
        """Create mock architect agent"""
        mock_agent = Mock()
        mock_agent.agent_id = "architect"
        mock_agent.status = "idle"
        mock_agent.current_task = None
        
        if responses:
            mock_agent.process_message = AsyncMock(side_effect=responses)
        else:
            mock_agent.process_message = AsyncMock(return_value={
                "status": "complete",
                "architecture": TestDataFactory.create_architecture_content(),
                "tokens_used": 200
            })
        
        return mock_agent
    
    @staticmethod
    def create_failing_agent(error_message: str = "Agent processing failed") -> Mock:
        """Create mock agent that fails"""
        mock_agent = Mock()
        mock_agent.agent_id = "failing_agent"
        mock_agent.status = "error"
        mock_agent.current_task = "processing"
        mock_agent.process_message = AsyncMock(return_value={
            "status": "error",
            "message": error_message,
            "tokens_used": 0
        })
        
        return mock_agent


class DatabaseTestHelper:
    """Helper class for database testing operations"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def create_test_project(self, name: str = "Test Project") -> str:
        """Create a test project and return ID"""
        return self.db.create_project(name, "Test requirements for integration testing")
    
    def create_message_chain(self, project_id: str, length: int = 3) -> List[str]:
        """Create a chain of messages for testing workflow"""
        agents = ["analyst", "architect", "developer", "tester"]
        message_ids = []
        
        for i in range(length):
            from_agent = agents[i] if i < len(agents) else f"agent_{i}"
            to_agent = agents[i + 1] if i + 1 < len(agents) else f"agent_{i + 1}"
            
            message_id = self.db.add_message(
                project_id=project_id,
                from_agent=from_agent,
                to_agent=to_agent,
                message_type="handoff",
                content={"step": i + 1, "data": f"Step {i + 1} data"},
                confidence=0.8 + (i * 0.05)
            )
            message_ids.append(message_id)
        
        return message_ids
    
    def add_test_actions(self, project_id: str, count: int = 2) -> List[str]:
        """Add test actions for human intervention testing"""
        action_ids = []
        priorities = ["high", "medium", "low"]
        
        conn = sqlite3.connect(self.db.db_path)
        
        for i in range(count):
            action_id = f"test_action_{i + 1}"
            priority = priorities[i % len(priorities)]
            
            conn.execute("""
                INSERT INTO actions (id, project_id, title, description, priority, options)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                action_id,
                project_id,
                f"Test Decision {i + 1}",
                f"This is test action {i + 1} requiring human intervention",
                priority,
                json.dumps([
                    {"value": f"option_{i}_1", "label": f"Option {i}.1"},
                    {"value": f"option_{i}_2", "label": f"Option {i}.2"}
                ])
            ))
            
            action_ids.append(action_id)
        
        conn.commit()
        conn.close()
        
        return action_ids
    
    def get_project_statistics(self, project_id: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a project"""
        conn = sqlite3.connect(self.db.db_path)
        
        # Message statistics
        cursor = conn.execute("""
            SELECT 
                COUNT(*) as total_messages,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_messages,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_messages,
                COUNT(CASE WHEN status = 'error' THEN 1 END) as error_messages,
                AVG(confidence) as avg_confidence
            FROM messages WHERE project_id = ?
        """, (project_id,))
        
        message_stats = cursor.fetchone()
        
        # Action statistics
        cursor = conn.execute("""
            SELECT 
                COUNT(*) as total_actions,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_actions,
                COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_actions
            FROM actions WHERE project_id = ?
        """, (project_id,))
        
        action_stats = cursor.fetchone()
        
        # Agent activity
        cursor = conn.execute("""
            SELECT from_agent, COUNT(*) as message_count
            FROM messages 
            WHERE project_id = ?
            GROUP BY from_agent
        """, (project_id,))
        
        agent_activity = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "messages": {
                "total": message_stats[0],
                "pending": message_stats[1],
                "completed": message_stats[2],
                "errors": message_stats[3],
                "avg_confidence": round(message_stats[4] or 0, 3)
            },
            "actions": {
                "total": action_stats[0],
                "pending": action_stats[1],
                "resolved": action_stats[2]
            },
            "agent_activity": agent_activity
        }


class PerformanceTimer:
    """Context manager for measuring performance"""
    
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        print(f"⏱️  {self.name}: {self.duration:.3f} seconds")
    
    def assert_faster_than(self, max_seconds: float):
        """Assert that operation completed within time limit"""
        if self.duration and self.duration > max_seconds:
            raise AssertionError(f"{self.name} took {self.duration:.3f}s, expected < {max_seconds}s")


class TestEnvironmentManager:
    """Manager for test environment setup and cleanup"""
    
    def __init__(self):
        self.temp_files = []
        self.temp_dirs = []
        self.cleanup_functions = []
    
    def create_temp_database(self) -> str:
        """Create temporary database for testing"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_files.append(temp_file.name)
        temp_file.close()
        return temp_file.name
    
    def create_temp_directory(self) -> str:
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        return temp_dir
    
    def register_cleanup(self, cleanup_func):
        """Register cleanup function to run on exit"""
        self.cleanup_functions.append(cleanup_func)
    
    def cleanup(self):
        """Clean up all temporary resources"""
        # Run custom cleanup functions
        for cleanup_func in self.cleanup_functions:
            try:
                cleanup_func()
            except Exception as e:
                print(f"Warning: Cleanup function failed: {e}")
        
        # Remove temporary files
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                print(f"Warning: Could not remove temp file {temp_file}: {e}")
        
        # Remove temporary directories
        for temp_dir in self.temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    import shutil
                    shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Warning: Could not remove temp directory {temp_dir}: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


class AsyncTestHelper:
    """Helper for async testing operations"""
    
    @staticmethod
    async def wait_for_condition(condition_func, timeout: float = 5.0, interval: float = 0.1) -> bool:
        """Wait for a condition to become true"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            await asyncio.sleep(interval)
        
        return False
    
    @staticmethod
    async def run_with_timeout(coro, timeout: float = 10.0):
        """Run coroutine with timeout"""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            raise AssertionError(f"Operation timed out after {timeout} seconds")
    
    @staticmethod
    def create_mock_future(return_value=None, exception=None):
        """Create mock future for testing"""
        future = asyncio.Future()
        
        if exception:
            future.set_exception(exception)
        else:
            future.set_result(return_value)
        
        return future


class IntegrationTestAssertions:
    """Custom assertions for integration testing"""
    
    @staticmethod
    def assert_message_chain_valid(messages: List[Dict[str, Any]]):
        """Assert that message chain follows expected pattern"""
        if not messages:
            raise AssertionError("Message chain is empty")
        
        # Check chronological order
        timestamps = [msg.get("timestamp") for msg in messages]
        sorted_timestamps = sorted(timestamps)
        
        if timestamps != sorted_timestamps:
            raise AssertionError("Messages are not in chronological order")
        
        # Check agent handoff pattern
        for i in range(len(messages) - 1):
            current_msg = messages[i]
            next_msg = messages[i + 1]
            
            if current_msg.get("to_agent") != next_msg.get("from_agent"):
                raise AssertionError(
                    f"Message handoff broken: {current_msg.get('to_agent')} -> {next_msg.get('from_agent')}"
                )
    
    @staticmethod
    def assert_api_response_valid(response, expected_status: int = 200, required_fields: List[str] = None):
        """Assert API response is valid"""
        if response.status_code != expected_status:
            raise AssertionError(
                f"Expected status {expected_status}, got {response.status_code}: {response.text}"
            )
        
        if required_fields:
            try:
                data = response.json()
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    raise AssertionError(f"Missing required fields: {missing_fields}")
                    
            except json.JSONDecodeError:
                raise AssertionError("Response is not valid JSON")
    
    @staticmethod
    def assert_performance_acceptable(duration: float, max_duration: float, operation_name: str = "Operation"):
        """Assert performance meets requirements"""
        if duration > max_duration:
            raise AssertionError(
                f"{operation_name} took {duration:.3f}s, expected < {max_duration:.3f}s"
            )
    
    @staticmethod
    def assert_agent_workflow_complete(db_helper: DatabaseTestHelper, project_id: str):
        """Assert agent workflow completed successfully"""
        stats = db_helper.get_project_statistics(project_id)
        
        if stats["messages"]["errors"] > 0:
            raise AssertionError(f"Workflow has {stats['messages']['errors']} error messages")
        
        if stats["messages"]["pending"] > stats["messages"]["completed"]:
            raise AssertionError("More pending messages than completed - workflow may be stuck")
        
        expected_agents = ["analyst", "architect", "developer", "tester"]
        active_agents = list(stats["agent_activity"].keys())
        
        if not any(agent in active_agents for agent in expected_agents):
            raise AssertionError(f"No expected agents found in workflow. Active: {active_agents}")


# Export main classes and functions
__all__ = [
    'TestDataFactory',
    'MockAgentFactory', 
    'DatabaseTestHelper',
    'PerformanceTimer',
    'TestEnvironmentManager',
    'AsyncTestHelper',
    'IntegrationTestAssertions'
]
