"""
FastAPI Generator
Generates the main FastAPI application with comprehensive endpoints and functionality.
"""

import json
from typing import Dict, Any
from ..base import BaseGenerator


class FastAPIGenerator(BaseGenerator):
    """
    Generator for the main FastAPI application.
    Creates comprehensive FastAPI app with all necessary endpoints and middleware.
    """

    async def generate(self, specifications: Dict) -> str:
        """Generate main FastAPI application code."""
        
        try:
            # Attempt LLM generation with specifications
            prompt = self._create_fastapi_prompt(specifications)
            content = await self._try_llm_generation(prompt, max_tokens=3000, temperature=0.1)
            
            self._update_generation_stats()
            return content
            
        except Exception as e:
            self.logger.warning(f"FastAPI LLM generation failed: {str(e)}, using fallback")
            content = self._use_fallback()
            self._update_generation_stats()
            return content

    def _create_fastapi_prompt(self, specifications: Dict) -> str:
        """Create prompt for FastAPI generation."""
        
        api_endpoints = specifications.get("api_endpoints", [])
        architecture = specifications.get("architecture", {})
        
        return f"""Generate a comprehensive FastAPI application for a BotArmy system with the following requirements:

API Endpoints needed:
{json.dumps(api_endpoints, indent=2)}

Architecture details:
{json.dumps(architecture, indent=2)}

Requirements:
1. Create a complete FastAPI application with proper imports
2. Include CORS middleware configuration
3. Add comprehensive error handling
4. Include health check endpoints
5. Add proper lifespan management for startup/shutdown
6. Include all CRUD endpoints for projects, agents, messages
7. Add real-time streaming endpoints for updates
8. Include proper dependency injection
9. Add comprehensive logging
10. Include rate limiting and security considerations

Generate clean, production-ready Python code with proper error handling and documentation.
"""

    def _generate_fallback(self) -> str:
        """Generate fallback FastAPI application."""
        
        return '''"""
BotArmy FastAPI Application
Main application entry point with comprehensive API endpoints.
"""

import asyncio
import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn

from config import get_settings
from database import Database
from llm_client import LLMClient
from utils.logger import setup_logging
from utils.error_handler import handle_api_error
from agents.agent_manager import AgentManager
from workflow.pipeline import WorkflowPipeline
from workflow.state_manager import StateManager

# Initialize logging
logger = setup_logging()

# Request/Response Models
class ProjectRequest(BaseModel):
    requirements: str
    user_id: Optional[str] = None

class ProjectResponse(BaseModel):
    project_id: str
    status: str
    message: str

class AgentStatusResponse(BaseModel):
    agent_type: str
    status: str
    progress: int
    messages: List[Dict]

class ConflictResolution(BaseModel):
    action_id: str
    resolution: str
    notes: Optional[str] = None

# Global instances
settings = get_settings()
database = Database(settings.database_url)
llm_client = LLMClient()
agent_manager = AgentManager(database, logger)
workflow_pipeline = WorkflowPipeline(database, logger)
state_manager = StateManager(database, logger)

@asynccontextmanager
async def lifespan(app: FastAPI):
    \"\"\"Application startup and shutdown handler\"\"\"
    
    # Startup
    logger.info("Starting BotArmy application...")
    
    # Initialize database
    await database.initialize()
    
    # Load and register agents
    from agents.analyst_agent import AnalystAgent
    from agents.architect_agent import ArchitectAgent
    from agents.developer_agent import DeveloperAgent
    from agents.tester_agent import TesterAgent
    
    # Register agents with manager
    agent_manager.register_agent("analyst", AnalystAgent(llm_client, database, logger))
    agent_manager.register_agent("architect", ArchitectAgent(llm_client, database, logger))
    agent_manager.register_agent("developer", DeveloperAgent(llm_client, database, logger))
    agent_manager.register_agent("tester", TesterAgent(llm_client, database, logger))
    
    logger.info("Application startup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down BotArmy application...")
    await database.close()

# Create FastAPI application
app = FastAPI(
    title="BotArmy POC",
    description="AI-powered software development automation platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Root endpoint
@app.get("/")
async def read_root():
    \"\"\"Root endpoint - serve the React application\"\"\"
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"message": "BotArmy API is running", "version": "1.0.0"}

# Health check endpoint
@app.get("/health")
async def health_check():
    \"\"\"Health check endpoint\"\"\"
    return {
        "status": "healthy",
        "database": "connected" if database.is_connected() else "disconnected",
        "llm_client": "ready",
        "agents_registered": len(agent_manager.get_all_agents())
    }

# Project Management Endpoints

@app.post("/api/projects", response_model=ProjectResponse)
async def create_project(request: ProjectRequest, background_tasks: BackgroundTasks):
    \"\"\"Create a new project and start the agent workflow\"\"\"
    
    try:
        # Create project in database
        project_id = await database.create_project(
            requirements=request.requirements,
            user_id=request.user_id
        )
        
        # Start workflow pipeline in background
        background_tasks.add_task(
            workflow_pipeline.execute_pipeline,
            project_id,
            request.requirements
        )
        
        logger.info(f"Created project {project_id}")
        
        return ProjectResponse(
            project_id=project_id,
            status="processing",
            message="Project created and workflow started"
        )
        
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    \"\"\"Get project details and current status\"\"\"
    
    try:
        project_data = await database.get_project(project_id)
        if not project_data:
            raise HTTPException(status_code=404, detail="Project not found")
            
        # Get current workflow status
        workflow_status = await workflow_pipeline.get_pipeline_status(project_id)
        
        return {
            **project_data,
            "workflow": workflow_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects")
async def list_projects(skip: int = 0, limit: int = 20):
    \"\"\"List all projects with pagination\"\"\"
    
    try:
        projects = await database.get_projects(skip=skip, limit=limit)
        return {"projects": projects, "total": len(projects)}
        
    except Exception as e:
        logger.error(f"Error listing projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# System Information Endpoints

@app.get("/api/system/stats")
async def get_system_stats():
    \"\"\"Get system statistics and performance metrics\"\"\"
    
    try:
        stats = {
            "llm_usage": llm_client.get_usage_stats(),
            "database_stats": await database.get_stats(),
            "agent_stats": agent_manager.get_system_stats()
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting system stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    \"\"\"Global exception handler\"\"\"
    return await handle_api_error(request, exc, logger)

# Development server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
'''
