# tests/conftest.py
import pytest
import tempfile
import os
import asyncio
import json
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient

# Import app components
from main import app, db, agents, llm_client
from database import DatabaseManager
from llm_client import LLMClient


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_db():
    """Create temporary test database"""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    test_database = DatabaseManager(temp_db.name)
    yield test_database
    # Cleanup
    temp_db.close()
    os.unlink(temp_db.name)


@pytest.fixture
def mock_llm_client():
    """Create mocked LLM client with predictable responses"""
    mock_client = Mock(spec=LLMClient)
    
    # Mock successful analysis response
    mock_analysis_response = {
        "success": True,
        "content": json.dumps({
            "analysis": "Requirements are clear and feasible",
            "user_stories": [
                {
                    "title": "User Registration",
                    "description": "As a user, I want to register an account",
                    "acceptance_criteria": ["Email validation", "Password strength check"]
                }
            ],
            "risks": [
                {
                    "risk": "Scalability concerns",
                    "mitigation": "Use cloud-native architecture"
                }
            ],
            "success_metrics": ["User adoption rate", "System uptime"],
            "confidence": 0.85,
            "next_steps": "Proceed to architecture design"
        }),
        "tokens_used": 150
    }
    
    # Mock successful architecture response
    mock_architecture_response = {
        "success": True,
        "content": json.dumps({
            "architecture": "Three-tier web application",
            "components": [
                {
                    "name": "Frontend",
                    "technology": "React",
                    "responsibility": "User interface"
                },
                {
                    "name": "Backend",
                    "technology": "FastAPI",
                    "responsibility": "Business logic and API"
                },
                {
                    "name": "Database",
                    "technology": "SQLite",
                    "responsibility": "Data persistence"
                }
            ],
            "tech_stack": {
                "frontend": "React with Tailwind CSS",
                "backend": "FastAPI with SQLAlchemy",
                "database": "SQLite for development",
                "justification": "Simple, well-documented stack suitable for POC"
            },
            "api_design": {
                "endpoints": [
                    {"path": "/api/users", "method": "POST", "purpose": "Create user"},
                    {"path": "/api/users/{id}", "method": "GET", "purpose": "Get user"}
                ]
            },
            "deployment_plan": {
                "platform": "Replit",
                "strategy": "Single instance deployment",
                "monitoring": "Basic health checks"
            },
            "confidence": 0.9,
            "concerns": ["Limited scalability in current design"]
        }),
        "tokens_used": 200
    }
    
    # Mock code generation response
    mock_code_response = {
        "success": True,
        "content": json.dumps({
            "files": [
                {
                    "path": "main.py",
                    "content": "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\ndef read_root():\n    return {'Hello': 'World'}"
                },
                {
                    "path": "models.py", 
                    "content": "from pydantic import BaseModel\n\nclass User(BaseModel):\n    name: str\n    email: str"
                }
            ],
            "documentation": "Simple FastAPI application with user model",
            "confidence": 0.8
        }),
        "tokens_used": 300
    }
    
    # Mock test generation response
    mock_test_response = {
        "success": True,
        "content": json.dumps({
            "test_files": [
                {
                    "path": "test_main.py",
                    "content": "def test_read_root():\n    assert True"
                }
            ],
            "test_results": {
                "total_tests": 5,
                "passed": 5,
                "failed": 0,
                "coverage": 85
            },
            "quality_metrics": {
                "complexity": "Low",
                "maintainability": "High",
                "security_score": 8.5
            },
            "confidence": 0.9
        }),
        "tokens_used": 180
    }
    
    # Configure mock responses based on prompt content
    def mock_generate_response(prompt, system_prompt=None, **kwargs):
        if "analyze" in prompt.lower() or "requirements" in prompt.lower():
            return mock_analysis_response
        elif "architecture" in prompt.lower() or "design" in prompt.lower():
            return mock_architecture_response
        elif "code" in prompt.lower() or "implement" in prompt.lower():
            return mock_code_response
        elif "test" in prompt.lower() or "validation" in prompt.lower():
            return mock_test_response
        else:
            return {
                "success": True,
                "content": "Generic successful response",
                "tokens_used": 50
            }
    
    mock_client.generate_response = AsyncMock(side_effect=mock_generate_response)
    return mock_client


@pytest.fixture
def test_client(test_db, mock_llm_client):
    """Create test client with mocked dependencies"""
    # Replace global dependencies with test versions
    app.dependency_overrides = {}
    
    # Replace database
    original_db = db
    app.dependency_overrides[type(db)] = lambda: test_db
    
    # Replace LLM client in agents
    for agent in agents.values():
        agent.llm_client = mock_llm_client
        agent.db = test_db
    
    client = TestClient(app)
    yield client
    
    # Cleanup
    app.dependency_overrides = {}


@pytest.fixture
def sample_project_data():
    """Sample project data for testing"""
    return {
        "name": "Test E-commerce App",
        "requirements": """
        Build a simple e-commerce web application with the following features:
        - User registration and authentication
        - Product catalog with search functionality
        - Shopping cart and checkout process
        - Order history for users
        - Admin panel for product management
        
        Non-functional requirements:
        - Should handle 100 concurrent users
        - Response time under 2 seconds
        - Mobile-responsive design
        - Basic security measures
        """
    }


@pytest.fixture 
def sample_messages():
    """Sample message data for testing"""
    return [
        {
            "project_id": "test-project-1",
            "from_agent": "analyst",
            "to_agent": "architect", 
            "message_type": "handoff",
            "content": {
                "analysis": "Requirements analysis complete",
                "user_stories": [{"title": "User login", "description": "User authentication"}],
                "confidence": 0.85
            },
            "confidence": 0.85
        },
        {
            "project_id": "test-project-1",
            "from_agent": "architect",
            "to_agent": "developer",
            "message_type": "handoff", 
            "content": {
                "architecture": "Three-tier architecture",
                "tech_stack": {"frontend": "React", "backend": "FastAPI"},
                "confidence": 0.9
            },
            "confidence": 0.9
        }
    ]


@pytest.fixture
def sample_actions():
    """Sample human action data for testing"""
    return [
        {
            "project_id": "test-project-1",
            "title": "Architecture Decision Required",
            "description": "Choose between SQLite and PostgreSQL for database",
            "priority": "high",
            "options": [
                {"value": "sqlite", "label": "SQLite (simpler)"},
                {"value": "postgresql", "label": "PostgreSQL (more scalable)"}
            ]
        },
        {
            "project_id": "test-project-1", 
            "title": "UI Framework Selection",
            "description": "Select UI component library",
            "priority": "medium",
            "options": [
                {"value": "tailwind", "label": "Tailwind CSS"},
                {"value": "mui", "label": "Material-UI"},
                {"value": "bootstrap", "label": "Bootstrap"}
            ]
        }
    ]


class AsyncContextManager:
    """Helper for async context management in tests"""
    def __init__(self, async_obj):
        self._async_obj = async_obj

    async def __aenter__(self):
        return self._async_obj

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def async_context():
    """Helper for async context management"""
    return AsyncContextManager
