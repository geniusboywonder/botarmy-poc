        return f"<{self.__class__.__name__}(type={self.agent_type}, status={self.status.value})>"
'''

    def _generate_agent_manager(self) -> str:
        """Generate comprehensive agent manager"""
        
        return '''"""
Agent manager for coordinating multiple agents and managing their interactions.
Handles agent lifecycle, communication, conflict detection, and performance monitoring.
"""

import asyncio
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import logging

from .base_agent import BaseAgent, AgentStatus

logger = logging.getLogger(__name__)

class AgentManager:
    """
    Comprehensive agent coordination and management system.
    Manages agent lifecycle, communication, conflicts, and performance.
    """

    def __init__(self, database, logger_instance):
        self.database = database
        self.logger = logger_instance or logger
        self.agents: Dict[str, BaseAgent] = {}
        self.active_projects: Dict[str, Dict] = {}
        self.agent_dependencies = {
            "architect": ["analyst"],
            "developer": ["analyst", "architect"], 
            "tester": ["analyst", "architect", "developer"]
        }

    def register_agent(self, agent_type: str, agent_instance: BaseAgent):
        """Register an agent with the manager"""
        
        if not isinstance(agent_instance, BaseAgent):
            raise ValueError(f"Agent must inherit from BaseAgent")
            
        self.agents[agent_type] = agent_instance
        self.logger.info(f"Registered agent: {agent_type}")

    def get_registered_agents(self) -> List[str]:
        """Get list of registered agent types"""
        return list(self.agents.keys())

    async def process_project(self, project_id: str, requirements: str) -> Dict[str, Any]:
        """Process a complete project through all agents"""
        
        self.active_projects[project_id] = {
            "status": "processing",
            "current_agent": None,
            "results": {},
            "start_time": datetime.now(),
            "conflicts": []
        }

        try:
            self.logger.info(f"Starting project processing: {project_id}")
            
            # Process through agents in dependency order
            agent_sequence = ["analyst", "architect", "developer", "tester"]
            current_data = {"project_id": project_id, "requirements": requirements}

            for agent_type in agent_sequence:
                if agent_type not in self.agents:
                    raise ValueError(f"Agent {agent_type} not registered")

                # Check dependencies
                await self._wait_for_dependencies(project_id, agent_type)
                
                # Process with agent
                result = await self._process_with_agent(project_id, agent_type, current_data)
                
                # Store result and prepare for next agent
                self.active_projects[project_id]["results"][agent_type] = result
                current_data = {**current_data, **result}

            # Mark project as completed
            self.active_projects[project_id]["status"] = "completed"
            self.active_projects[project_id]["end_time"] = datetime.now()
            
            return {
                "project_id": project_id,
                "status": "completed",
                "results": self.active_projects[project_id]["results"],
                "processing_time": (
                    self.active_projects[project_id]["end_time"] - 
                    self.active_projects[project_id]["start_time"]
                ).total_seconds()
            }

        except Exception as e:
            self.active_projects[project_id]["status"] = "error"
            self.active_projects[project_id]["error"] = str(e)
            self.logger.error(f"Project processing failed: {str(e)}")
            raise

    async def _process_with_agent(self, project_id: str, agent_type: str, 
                                 input_data: Dict) -> Dict[str, Any]:
        """Process data with a specific agent"""
        
        self.active_projects[project_id]["current_agent"] = agent_type
        agent = self.agents[agent_type]

        self.logger.info(f"Processing with {agent_type} agent for project {project_id}")
        
        try:
            # Initialize agent
            await agent.initialize_processing(project_id, input_data)
            
            # Process data
            result = await agent.process(input_data)
            
            # Finalize processing
            summary = await agent.finalize_processing(success=True)
            
            return result

        except Exception as e:
            await agent.finalize_processing(success=False)
            self.logger.error(f"Agent {agent_type} processing failed: {str(e)}")
            
            # Check for retry possibility
            if await self._should_retry_agent(agent_type, str(e)):
                self.logger.info(f"Retrying {agent_type} agent")
                return await self._process_with_agent(project_id, agent_type, input_data)
            
            raise

    async def _wait_for_dependencies(self, project_id: str, agent_type: str):
        """Wait for dependent agents to complete"""
        
        dependencies = self.agent_dependencies.get(agent_type, [])
        
        for dep_agent in dependencies:
            # Check if dependency completed
            while dep_agent not in self.active_projects[project_id]["results"]:
                self.logger.debug(f"Waiting for {dep_agent} to complete before starting {agent_type}")
                await asyncio.sleep(1)

    async def _should_retry_agent(self, agent_type: str, error_message: str) -> bool:
        """Determine if agent should be retried based on error"""
        
        # Define retryable error patterns
        retryable_errors = [
            "rate limit", "timeout", "connection", "temporary"
        ]
        
        error_lower = error_message.lower()
        return any(pattern in error_lower for pattern in retryable_errors)

    async def get_project_status(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive project status"""
        
        if project_id not in self.active_projects:
            # Try to load from database
            project_data = await self.database.get_project(project_id)
            if project_data:
                return {
                    "project_id": project_id,
                    "status": project_data.get("status", "unknown"),
                    "current_agent": None,
                    "agents": await self._get_agent_statuses(project_id)
                }
            return None

        project_status = self.active_projects[project_id]
        agent_statuses = await self._get_agent_statuses(project_id)
        
        return {
            "project_id": project_id,
            "status": project_status["status"],
            "current_agent": project_status.get("current_agent"),
            "agents": agent_statuses,
            "conflicts": project_status.get("conflicts", []),
            "start_time": project_status.get("start_time"),
            "processing_time": (
                (datetime.now() - project_status["start_time"]).total_seconds()
                if "start_time" in project_status else 0
            )
        }

    async def _get_agent_statuses(self, project_id: str) -> Dict[str, Any]:
        """Get status of all agents for a project"""
        
        statuses = {}
        for agent_type, agent in self.agents.items():
            if agent.current_project_id == project_id:
                statuses[agent_type] = agent.get_status()
            else:
                # Get from database
                db_status = await self.database.get_agent_status(project_id, agent_type)
                statuses[agent_type] = db_status or {"status": "idle", "progress": 0}
        
        return statuses

    async def handle_agent_error(self, project_id: str, agent_type: str, error: str):
        """Handle agent processing errors with escalation"""
        
        self.logger.error(f"Agent error in {agent_type}: {error}")
        
        # Log error to database
        await self.database.log_agent_error(
            project_id=project_id,
            agent_type=agent_type,
            error_message=error
        )

        # Update project status
        if project_id in self.active_projects:
            self.active_projects[project_id]["status"] = "error"
            self.active_projects[project_id]["error"] = {
                "agent": agent_type,
                "message": error,
                "timestamp": datetime.now()
            }

        # Check if error requires human intervention
        if await self._requires_human_intervention(error):
            await self._escalate_to_human(project_id, agent_type, error)

    async def _requires_human_intervention(self, error_message: str) -> bool:
        """Determine if error requires human intervention"""
        
        human_intervention_patterns = [
            "conflict", "ambiguous", "clarification needed", 
            "invalid requirements", "missing information"
        ]
        
        error_lower = error_message.lower()
        return any(pattern in error_lower for pattern in human_intervention_patterns)

    async def _escalate_to_human(self, project_id: str, agent_type: str, error: str):
        """Escalate issue to human intervention"""
        
        conflict_id = await self.database.create_conflict(
            project_id=project_id,
            description=f"Agent {agent_type} error requiring human intervention: {error}",
            agents_involved=[agent_type],
            stage=agent_type
        )
        
        if project_id in self.active_projects:
            self.active_projects[project_id]["conflicts"].append({
                "id": conflict_id,
                "type": "agent_error",
                "description": error,
                "agent": agent_type,
                "timestamp": datetime.now()
            })

        self.logger.info(f"Escalated to human intervention: {conflict_id}")

    def get_all_agents(self) -> Dict[str, Any]:
        """Get information about all registered agents"""
        
        agent_info = {}
        for agent_type, agent in self.agents.items():
            agent_info[agent_type] = {
                "type": agent_type,
                "status": agent.status.value if hasattr(agent, 'status') else "unknown",
                "metrics": agent.get_metrics() if hasattr(agent, 'get_metrics') else {},
                "current_project": agent.current_project_id if hasattr(agent, 'current_project_id') else None
            }
        
        return agent_info

    def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide agent statistics"""
        
        total_agents = len(self.agents)
        active_projects = len(self.active_projects)
        
        # Agent status distribution
        status_counts = {}
        for agent in self.agents.values():
            if hasattr(agent, 'status'):
                status = agent.status.value
                status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_agents": total_agents,
            "active_projects": active_projects,
            "agent_status_distribution": status_counts,
            "registered_agents": list(self.agents.keys())
        }

    async def pause_all_agents(self):
        """Pause all active agents"""
        
        for agent in self.agents.values():
            if hasattr(agent, 'pause_processing'):
                await agent.pause_processing()
        
        self.logger.info("All agents paused")

    async def resume_all_agents(self):
        """Resume all paused agents"""
        
        for agent in self.agents.values():
            if hasattr(agent, 'resume_processing'):
                await agent.resume_processing()
        
        self.logger.info("All agents resumed")

    async def shutdown(self):
        """Gracefully shutdown agent manager"""
        
        self.logger.info("Shutting down agent manager")
        
        # Cancel all active processing
        for agent in self.agents.values():
            if hasattr(agent, 'cancel_processing'):
                await agent.cancel_processing()
        
        # Clear state
        self.agents.clear()
        self.active_projects.clear()
        
        self.logger.info("Agent manager shutdown completed")
'''

    def _generate_workflow_pipeline(self) -> str:
        """Generate workflow pipeline management"""
        
        return '''"""
Comprehensive workflow pipeline for orchestrating sequential agent processing.
Manages dependencies, error recovery, state transitions, and performance monitoring.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class PipelineStage(Enum):
    """Pipeline stage enumeration"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    ANALYZING = "analyzing"
    ARCHITECTING = "architecting"  
    DEVELOPING = "developing"
    TESTING = "testing"
    COMPLETED = "completed"
    ERROR = "error"
    PAUSED = "paused"

class WorkflowPipeline:
    """
    Advanced workflow pipeline for orchestrating agent sequences.
    Features: dependency management, error recovery, monitoring, and optimization.
    """

    def __init__(self, database, logger_instance):
        self.database = database
        self.logger = logger_instance or logger
        self.current_stage = PipelineStage.IDLE
        self.project_id = None
        self.pipeline_data = {}
        
        # Stage configuration
        self.stage_sequence = [
            PipelineStage.ANALYZING,
            PipelineStage.ARCHITECTING,
            PipelineStage.DEVELOPING,
            PipelineStage.TESTING
        ]
        
        # Hooks for custom behavior
        self.stage_hooks: Dict[PipelineStage, List[Callable]] = {
            stage: [] for stage in PipelineStage
        }
        
        # Performance tracking
        self.performance_metrics = {
            "total_pipelines": 0,
            "successful_pipelines": 0,
            "failed_pipelines": 0,
            "average_duration": 0.0,
            "stage_durations": {}
        }

    def register_stage_hook(self, stage: PipelineStage, hook_func: Callable):
        """Register a hook function for a specific stage"""
        self.stage_hooks[stage].append(hook_func)

    async def execute_pipeline(self, project_id: str, initial_requirements: str) -> Dict[str, Any]:
        """Execute the complete agent pipeline for a project"""
        
        try:
            self.project_id = project_id
            self.current_stage = PipelineStage.INITIALIZING
            
            self.logger.info(f"Starting pipeline execution for project {project_id}")
            
            # Initialize pipeline state
            self.pipeline_data = {
                "project_id": project_id,
                "requirements": initial_requirements,
                "current_stage": PipelineStage.INITIALIZING,
                "stage_outputs": {},
                "stage_durations": {},
                "errors": [],
                "warnings": [],
                "start_time": datetime.now(),
                "dependencies_met": set()
            }

            # Update database
            await self.database.update_project_status(project_id, "processing")
            
            # Execute initialization hooks
            await self._execute_stage_hooks(PipelineStage.INITIALIZING)
            
            # Execute stages sequentially
            stage_input = {
                "project_id": project_id, 
                "requirements": initial_requirements
            }

            for stage in self.stage_sequence:
                stage_start_time = datetime.now()
                
                try:
                    self.logger.info(f""""
Backend code generator for FastAPI and Python components.
Generates complete backend architecture including APIs, database operations,
workflow management, and supporting modules.
"""

import json
import os
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

class BackendGenerator:
    """
    Comprehensive backend generator for Python/FastAPI applications.
    Handles generation of all backend components following modular architecture.
    """
    
    def __init__(self, llm_client, logger):
        self.llm_client = llm_client
        self.logger = logger
        self.generated_files = {}
        self.generation_stats = {
            "files_generated": 0,
            "lines_of_code": 0,
            "errors": [],
            "warnings": []
        }

    async def generate_all_backend_files(self, architecture: Dict, tech_stack: Dict, 
                                        specifications: Dict) -> Dict[str, str]:
        """
        Generate all backend files based on specifications.
        
        Args:
            architecture: System architecture specification
            tech_stack: Technology stack choices
            specifications: Detailed technical specifications
            
        Returns:
            Dictionary of filename -> file content mappings
        """
        try:
            self.logger.info("Starting comprehensive backend file generation")
            
            # Generate core application files
            await self._generate_core_files(architecture, tech_stack, specifications)
            
            # Generate agent-related files
            await self._generate_agent_files(specifications)
            
            # Generate workflow management files
            await self._generate_workflow_files(specifications)
            
            # Generate utility and support files
            await self._generate_utility_files(specifications)
            
            # Generate database and persistence files
            await self._generate_database_files(specifications)
            
            self.logger.info(f"Backend generation completed: {self.generation_stats['files_generated']} files, "
                           f"{self.generation_stats['lines_of_code']} lines of code")
            
            return self.generated_files
            
        except Exception as e:
            self.logger.error(f"Backend generation failed: {str(e)}")
            raise

    async def _generate_core_files(self, architecture: Dict, tech_stack: Dict, 
                                  specifications: Dict):
        """Generate core application files (main.py, config.py, etc.)"""
        
        # Generate main FastAPI application
        self.generated_files["main.py"] = await self._generate_fastapi_main(
            architecture, tech_stack, specifications
        )
        
        # Generate configuration management
        self.generated_files["config.py"] = self._generate_config_module()
        
        # Generate LLM client
        self.generated_files["llm_client.py"] = self._generate_llm_client()
        
        # Generate database module
        self.generated_files["database.py"] = await self._generate_database_module(
            specifications.get("database_schema", {})
        )
        
        self._update_stats("core_files", 4)

    async def _generate_agent_files(self, specifications: Dict):
        """Generate agent-related backend files"""
        
        # Ensure agents directory structure
        self.generated_files["agents/__init__.py"] = ""
        
        # Generate base agent class
        self.generated_files["agents/base_agent.py"] = self._generate_base_agent()
        
        # Generate agent manager
        self.generated_files["agents/agent_manager.py"] = self._generate_agent_manager()
        
        # Generate agent registry
        self.generated_files["agents/agent_registry.py"] = self._generate_agent_registry()
        
        self._update_stats("agent_files", 4)

    async def _generate_workflow_files(self, specifications: Dict):
        """Generate workflow management files"""
        
        # Ensure workflow directory structure
        self.generated_files["workflow/__init__.py"] = ""
        
        # Generate pipeline manager
        self.generated_files["workflow/pipeline.py"] = self._generate_workflow_pipeline()
        
        # Generate state manager
        self.generated_files["workflow/state_manager.py"] = self._generate_state_manager()
        
        # Generate message queue system
        self.generated_files["workflow/message_queue.py"] = self._generate_message_queue()
        
        self._update_stats("workflow_files", 4)

    async def _generate_utility_files(self, specifications: Dict):
        """Generate utility and helper files"""
        
        # Generate error handling utilities
        self.generated_files["utils/__init__.py"] = ""
        self.generated_files["utils/error_handler.py"] = self._generate_error_handler()
        
        # Generate logging utilities
        self.generated_files["utils/logger.py"] = self._generate_logger_utils()
        
        # Generate validation utilities
        self.generated_files["utils/validators.py"] = self._generate_validators()
        
        # Generate file operations utilities
        self.generated_files["utils/file_ops.py"] = self._generate_file_operations()
        
        self._update_stats("utility_files", 5)

    async def _generate_database_files(self, specifications: Dict):
        """Generate database and persistence related files"""
        
        # Generate database models
        self.generated_files["models/__init__.py"] = ""
        self.generated_files["models/project.py"] = self._generate_project_model()
        self.generated_files["models/agent.py"] = self._generate_agent_model()
        self.generated_files["models/message.py"] = self._generate_message_model()
        
        # Generate database operations
        self.generated_files["db_operations.py"] = self._generate_db_operations()
        
        self._update_stats("database_files", 5)

    async def _generate_fastapi_main(self, architecture: Dict, tech_stack: Dict, 
                                    specifications: Dict) -> str:
        """Generate main FastAPI application with comprehensive endpoints"""
        
        # Use LLM for dynamic generation based on specifications
        from prompts.developer_prompts import DEVELOPER_PROMPTS
        
        try:
            prompt = DEVELOPER_PROMPTS["fastapi_main"].format(
                api_endpoints=json.dumps(specifications.get("api_endpoints", []), indent=2),
                architecture=json.dumps(architecture, indent=2),
                tech_stack=json.dumps(tech_stack, indent=2)
            )

            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=2500,
                temperature=0.1
            )

            return response.strip()
            
        except Exception as e:
            self.logger.warning(f"LLM generation failed for main.py, using fallback: {str(e)}")
            return self._generate_fastapi_main_fallback()

    def _generate_fastapi_main_fallback(self) -> str:
        """Fallback FastAPI main application when LLM generation fails"""
        
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
    """Application startup and shutdown handler"""
    
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
    """Root endpoint - serve the React application"""
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"message": "BotArmy API is running", "version": "1.0.0"}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected" if database.is_connected() else "disconnected",
        "llm_client": "ready",
        "agents_registered": len(agent_manager.get_all_agents())
    }

# Project Management Endpoints

@app.post("/api/projects", response_model=ProjectResponse)
async def create_project(request: ProjectRequest, background_tasks: BackgroundTasks):
    """Create a new project and start the agent workflow"""
    
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
    """Get project details and current status"""
    
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
    """List all projects with pagination"""
    
    try:
        projects = await database.get_projects(skip=skip, limit=limit)
        return {"projects": projects, "total": len(projects)}
        
    except Exception as e:
        logger.error(f"Error listing projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Agent Status Endpoints

@app.get("/api/agents/{project_id}/{agent_type}/status", response_model=AgentStatusResponse)
async def get_agent_status(project_id: str, agent_type: str):
    """Get current status of a specific agent for a project"""
    
    try:
        agent_status = await database.get_agent_status(project_id, agent_type)
        if not agent_status:
            raise HTTPException(status_code=404, detail="Agent status not found")
            
        messages = await database.get_agent_messages(project_id, agent_type)
        
        return AgentStatusResponse(
            agent_type=agent_type,
            status=agent_status["status"],
            progress=agent_status["progress"],
            messages=messages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents/{project_id}")
async def get_all_agent_statuses(project_id: str):
    """Get status of all agents for a project"""
    
    try:
        agent_types = ["analyst", "architect", "developer", "tester"]
        statuses = {}
        
        for agent_type in agent_types:
            agent_status = await database.get_agent_status(project_id, agent_type)
            if agent_status:
                statuses[agent_type] = agent_status
                
        return {"project_id": project_id, "agents": statuses}
        
    except Exception as e:
        logger.error(f"Error getting agent statuses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Conflict Resolution Endpoints

@app.get("/api/conflicts/{project_id}")
async def get_conflicts(project_id: str):
    """Get all conflicts for a project"""
    
    try:
        conflicts = await database.get_project_conflicts(project_id)
        return {"project_id": project_id, "conflicts": conflicts}
        
    except Exception as e:
        logger.error(f"Error getting conflicts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/conflicts/resolve")
async def resolve_conflict(resolution: ConflictResolution):
    """Resolve a conflict with human input"""
    
    try:
        success = await state_manager.resolve_conflict(
            resolution.action_id,
            resolution.resolution,
            resolution.notes
        )
        
        if success:
            return {"message": "Conflict resolved successfully"}
        else:
            raise HTTPException(status_code=404, detail="Conflict not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving conflict: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# File Management Endpoints

@app.get("/api/files/{project_id}")
async def get_project_files(project_id: str):
    """Get all generated files for a project"""
    
    try:
        files = await database.get_project_files(project_id)
        return {"project_id": project_id, "files": files}
        
    except Exception as e:
        logger.error(f"Error getting project files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files/{project_id}/download")
async def download_project_files(project_id: str):
    """Download all project files as a ZIP archive"""
    
    try:
        from utils.file_ops import create_project_archive
        
        archive_path = await create_project_archive(project_id)
        
        def iter_file():
            with open(archive_path, "rb") as file_like:
                yield from file_like
                
        return StreamingResponse(
            iter_file(),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={project_id}.zip"}
        )
        
    except Exception as e:
        logger.error(f"Error downloading project files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Server-Sent Events for real-time updates
@app.get("/api/stream")
async def stream_events(project_id: Optional[str] = None):
    """Stream real-time events to clients"""
    
    async def event_generator():
        while True:
            try:
                # Get latest events from database
                events = await database.get_recent_events(project_id)
                
                for event in events:
                    yield f"data: {json.dumps(event)}\\n\\n"
                    
                await asyncio.sleep(1)  # Poll every second
                
            except Exception as e:
                logger.error(f"Error in event stream: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\\n\\n"
                break
    
    return StreamingResponse(
        event_generator(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

# System Information Endpoints

@app.get("/api/system/stats")
async def get_system_stats():
    """Get system statistics and performance metrics"""
    
    try:
        stats = {
            "llm_usage": llm_client.get_usage_stats(),
            "database_stats": await database.get_stats(),
            "agent_stats": agent_manager.get_stats(),
            "workflow_stats": await workflow_pipeline.get_stats()
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting system stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
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

    async def _generate_database_module(self, schema: Dict) -> str:
        """Generate database operations module with comprehensive functionality"""
        
        try:
            from prompts.developer_prompts import DEVELOPER_PROMPTS
            
            prompt = DEVELOPER_PROMPTS["database_module"].format(
                schema=json.dumps(schema, indent=2)
            )

            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.1
            )

            return response.strip()
            
        except Exception as e:
            self.logger.warning(f"LLM generation failed for database.py, using fallback: {str(e)}")
            return self._generate_database_fallback()

    def _generate_database_fallback(self) -> str:
        """Fallback database module when LLM generation fails"""
        
        return '''"""
Database operations and management for BotArmy application.
Provides comprehensive database functionality using SQLite with async operations.
"""

import sqlite3
import aiosqlite
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

class Database:
    """
    Comprehensive database manager for BotArmy application.
    Handles projects, agents, messages, conflicts, and file storage.
    """

    def __init__(self, database_url: str):
        self.database_url = database_url.replace("sqlite:///", "")
        self.connection = None
        self._stats = {
            "queries_executed": 0,
            "errors": 0,
            "last_error": None
        }

    async def initialize(self):
        """Initialize database and create all required tables"""
        
        try:
            self.connection = await aiosqlite.connect(self.database_url)
            await self.connection.execute("PRAGMA foreign_keys = ON")
            await self._create_tables()
            await self.connection.commit()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            self._stats["errors"] += 1
            self._stats["last_error"] = str(e)
            raise

    async def _create_tables(self):
        """Create all required database tables"""
        
        # Projects table
        await self.connection.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                requirements TEXT NOT NULL,
                status TEXT DEFAULT 'created',
                user_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT DEFAULT '{}'
            )
        ''')

        # Agents table
        await self.connection.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                agent_type TEXT NOT NULL,
                status TEXT DEFAULT 'idle',
                progress INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id),
                UNIQUE(project_id, agent_type)
            )
        ''')

        # Messages table
        await self.connection.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                from_agent TEXT,
                to_agent TEXT,
                content TEXT NOT NULL,
                message_type TEXT DEFAULT 'info',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')

        # Conflicts table
        await self.connection.execute('''
            CREATE TABLE IF NOT EXISTS conflicts (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                description TEXT NOT NULL,
                agents_involved TEXT NOT NULL,
                stage TEXT,
                status TEXT DEFAULT 'pending',
                resolution TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')

        # Files table
        await self.connection.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                generated_by TEXT,
                file_type TEXT,
                size INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')

        # Events table for real-time updates
        await self.connection.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT,
                event_type TEXT NOT NULL,
                event_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    # Project Operations

    async def create_project(self, requirements: str, user_id: str = None) -> str:
        """Create a new project and return its ID"""
        
        project_id = str(uuid.uuid4())
        
        try:
            await self.connection.execute(
                '''INSERT INTO projects (id, requirements, user_id) 
                   VALUES (?, ?, ?)''',
                (project_id, requirements, user_id)
            )
            
            # Initialize agent statuses
            agent_types = ["analyst", "architect", "developer", "tester"]
            for agent_type in agent_types:
                await self.connection.execute(
                    '''INSERT INTO agents (project_id, agent_type) 
                       VALUES (?, ?)''',
                    (project_id, agent_type)
                )
            
            await self.connection.commit()
            self._stats["queries_executed"] += len(agent_types) + 1
            
            await self._create_event(project_id, "project_created", {
                "project_id": project_id,
                "requirements": requirements[:100] + "..." if len(requirements) > 100 else requirements
            })
            
            return project_id
            
        except Exception as e:
            await self.connection.rollback()
            logger.error(f"Error creating project: {str(e)}")
            self._stats["errors"] += 1
            self._stats["last_error"] = str(e)
            raise

    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project by ID"""
        
        try:
            cursor = await self.connection.execute(
                '''SELECT * FROM projects WHERE id = ?''',
                (project_id,)
            )
            row = await cursor.fetchone()
            
            if row:
                return {
                    "id": row[0],
                    "requirements": row[1],
                    "status": row[2],
                    "user_id": row[3],
                    "created_at": row[4],
                    "updated_at": row[5],
                    "metadata": json.loads(row[6]) if row[6] else {}
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting project {project_id}: {str(e)}")
            self._stats["errors"] += 1
            self._stats["last_error"] = str(e)
            return None

    async def get_projects(self, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """Get paginated list of projects"""
        
        try:
            cursor = await self.connection.execute(
                '''SELECT * FROM projects ORDER BY created_at DESC LIMIT ? OFFSET ?''',
                (limit, skip)
            )
            rows = await cursor.fetchall()
            
            projects = []
            for row in rows:
                projects.append({
                    "id": row[0],
                    "requirements": row[1],
                    "status": row[2],
                    "user_id": row[3],
                    "created_at": row[4],
                    "updated_at": row[5],
                    "metadata": json.loads(row[6]) if row[6] else {}
                })
            
            return projects
            
        except Exception as e:
            logger.error(f"Error getting projects: {str(e)}")
            self._stats["errors"] += 1
            self._stats["last_error"] = str(e)
            return []

    async def update_project_status(self, project_id: str, status: str):
        """Update project status"""
        
        try:
            await self.connection.execute(
                '''UPDATE projects SET status = ?, updated_at = CURRENT_TIMESTAMP 
                   WHERE id = ?''',
                (status, project_id)
            )
            await self.connection.commit()
            
            await self._create_event(project_id, "project_status_updated", {
                "project_id": project_id,
                "status": status
            })
            
        except Exception as e:
            logger.error(f"Error updating project status: {str(e)}")
            self._stats["errors"] += 1
            self._stats["last_error"] = str(e)
            raise

    # Agent Operations

    async def update_agent_status(self, project_id: str, agent_type: str, 
                                 status: str, progress: int = None):
        """Update agent status and progress"""
        
        try:
            if progress is not None:
                await self.connection.execute(
                    '''UPDATE agents SET status = ?, progress = ?, updated_at = CURRENT_TIMESTAMP 
                       WHERE project_id = ? AND agent_type = ?''',
                    (status, progress, project_id, agent_type)
                )
            else:
                await self.connection.execute(
                    '''UPDATE agents SET status = ?, updated_at = CURRENT_TIMESTAMP 
                       WHERE project_id = ? AND agent_type = ?''',
                    (status, project_id, agent_type)
                )
            
            await self.connection.commit()
            
            await self._create_event(project_id, "agent_status_updated", {
                "project_id": project_id,
                "agent_type": agent_type,
                "status": status,
                "progress": progress
            })
            
        except Exception as e:
            logger.error(f"Error updating agent status: {str(e)}")
            self._stats["errors"] += 1
            self._stats["last_error"] = str(e)
            raise

    async def get_agent_status(self, project_id: str, agent_type: str) -> Optional[Dict[str, Any]]:
        """Get current status of a specific agent"""
        
        try:
            cursor = await self.connection.execute(
                '''SELECT * FROM agents WHERE project_id = ? AND agent_type = ?''',
                (project_id, agent_type)
            )
            row = await cursor.fetchone()
            
            if row:
                return {
                    "id": row[0],
                    "project_id": row[1],
                    "agent_type": row[2],
                    "status": row[3],
                    "progress": row[4],
                    "created_at": row[5],
                    "updated_at": row[6]
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting agent status: {str(e)}")
            self._stats["errors"] += 1
            self._stats["last_error"] = str(e)
            return None

    # Message Operations

    async def create_message(self, project_id: str, from_agent: str, 
                           to_agent: str, content: Dict[str, Any]) -> str:
        """Create a new message between agents"""
        
        message_id = str(uuid.uuid4())
        
        try:
            await self.connection.execute(
                '''INSERT INTO messages (id, project_id, from_agent, to_agent, content) 
                   VALUES (?, ?, ?, ?, ?)''',
                (message_id, project_id, from_agent, to_agent, json.dumps(content))
            )
            await self.connection.commit()
            
            await self._create_event(project_id, "message_created", {
                "message_id": message_id,
                "from_agent": from_agent,
                "to_agent": to_agent
            })
            
            return message_id
            
        except Exception as e:
            logger.error(f"Error creating message: {str(e)}")
            self._stats["errors"] += 1
            self._stats["last_error"] = str(e)
            raise

    async def get_agent_messages(self, project_id: str, agent_type: str) -> List[Dict[str, Any]]:
        """Get all messages for a specific agent"""
        
        try:
            cursor = await self.connection.execute(
                '''SELECT * FROM messages 
                   WHERE project_id = ? AND (from_agent = ? OR to_agent = ?)
                   ORDER BY created_at DESC''',
                (project_id, agent_type, agent_type)
            )
            rows = await cursor.fetchall()
            
            messages = []
            for row in rows:
                messages.append({
                    "id": row[0],
                    "project_id": row[1],
                    "from_agent": row[2],
                    "to_agent": row[3],
                    "content": json.loads(row[4]) if row[4] else {},
                    "message_type": row[5],
                    "created_at": row[6]
                })
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting agent messages: {str(e)}")
            self._stats["errors"] += 1
            self._stats["last_error"] = str(e)
            return []

    # Conflict Operations

    async def create_conflict(self, project_id: str, description: str, 
                            agents_involved: List[str], stage: str = None) -> str:
        """Create a new conflict record"""
        
        conflict_id = str(uuid.uuid4())
        
        try:
            await self.connection.execute(
                '''INSERT INTO conflicts (id, project_id, description, agents_involved, stage) 
                   VALUES (?, ?, ?, ?, ?)''',
                (conflict_id, project_id, description, json.dumps(agents_involved), stage)
            )
            await self.connection.commit()
            
            await self._create_event(project_id, "conflict_created", {
                "conflict_id": conflict_id,
                "description": description,
                "agents_involved": agents_involved
            })
            
            return conflict_id
            
        except Exception as e:
            logger.error(f"Error creating conflict: {str(e)}")
            self._stats["errors"] += 1
            self._stats["last_error"] = str(e)
            raise

    async def resolve_conflict(self, conflict_id: str, resolution: str):
        """Mark a conflict as resolved"""
        
        try:
            await self.connection.execute(
                '''UPDATE conflicts SET status = 'resolved', resolution = ?, 
                   resolved_at = CURRENT_TIMESTAMP WHERE id = ?''',
                (resolution, conflict_id)
            )
            await self.connection.commit()
            
        except Exception as e:
            logger.error(f"Error resolving conflict: {str(e)}")
            self._stats["errors"] += 1
            self._stats["last_error"] = str(e)
            raise

    async def get_project_conflicts(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all conflicts for a project"""
        
        try:
            cursor = await self.connection.execute(
                '''SELECT * FROM conflicts WHERE project_id = ? ORDER BY created_at DESC''',
                (project_id,)
            )
            rows = await cursor.fetchall()
            
            conflicts = []
            for row in rows:
                conflicts.append({
                    "id": row[0],
                    "project_id": row[1],
                    "description": row[2],
                    "agents_involved": json.loads(row[3]) if row[3] else [],
                    "stage": row[4],
                    "status": row[5],
                    "resolution": row[6],
                    "created_at": row[7],
                    "resolved_at": row[8]
                })
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Error getting project conflicts: {str(e)}")
            self._stats["errors"] += 1
            self._stats["last_error"] = str(e)
            return []

    # File Operations

    async def save_file(self, project_id: str, filename: str, content: str, 
                       generated_by: str, file_type: str = None):
        """Save a generated file to the database"""
        
        try:
            file_size = len(content)
            if not file_type:
                file_type = filename.split('.')[-1] if '.' in filename else 'unknown'
            
            await self.connection.execute(
                '''INSERT INTO files (project_id, filename, content, generated_by, file_type, size) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (project_id, filename, content, generated_by, file_type, file_size)
            )
            await self.connection.commit()
            
        except Exception as e:
            logger.error(f"Error saving file {filename}: {str(e)}")
            self._stats["errors"] += 1
            self._stats["last_error"] = str(e)
            raise

    async def get_project_files(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all files for a project"""
        
        try:
            cursor = await self.connection.execute(
                '''SELECT * FROM files WHERE project_id = ? ORDER BY filename''',
                (project_id,)
            )
            rows = await cursor.fetchall()
            
            files = []
            for row in rows:
                files.append({
                    "id": row[0],
                    "project_id": row[1],
                    "filename": row[2],
                    "content": row[3],
                    "generated_by": row[4],
                    "file_type": row[5],
                    "size": row[6],
                    "created_at": row[7]
                })
            
            return files
            
        except Exception as e:
            logger.error(f"Error getting project files: {str(e)}")
            self._stats["errors"] += 1
            self._stats["last_error"] = str(e)
            return []

    # Event Operations for Real-time Updates

    async def _create_event(self, project_id: str, event_type: str, event_data: Dict[str, Any]):
        """Create an event for real-time updates"""
        
        try:
            await self.connection.execute(
                '''INSERT INTO events (project_id, event_type, event_data) 
                   VALUES (?, ?, ?)''',
                (project_id, event_type, json.dumps(event_data))
            )
            await self.connection.commit()
            
        except Exception as e:
            logger.error(f"Error creating event: {str(e)}")
            # Don't raise here as events are auxiliary

    async def get_recent_events(self, project_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent events for real-time updates"""
        
        try:
            if project_id:
                cursor = await self.connection.execute(
                    '''SELECT * FROM events WHERE project_id = ? 
                       ORDER BY created_at DESC LIMIT ?''',
                    (project_id, limit)
                )
            else:
                cursor = await self.connection.execute(
                    '''SELECT * FROM events ORDER BY created_at DESC LIMIT ?''',
                    (limit,)
                )
            
            rows = await cursor.fetchall()
            
            events = []
            for row in rows:
                events.append({
                    "id": row[0],
                    "project_id": row[1],
                    "event_type": row[2],
                    "event_data": json.loads(row[3]) if row[3] else {},
                    "created_at": row[4]
                })
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting recent events: {str(e)}")
            return []

    # Utility Methods

    async def log_agent_error(self, project_id: str, agent_type: str, error_message: str):
        """Log an agent error"""
        
        try:
            await self.create_message(
                project_id=project_id,
                from_agent="system",
                to_agent=agent_type,
                content={
                    "type": "error",
                    "message": error_message,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error logging agent error: {str(e)}")

    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        
        try:
            # Get table counts
            tables = ["projects", "agents", "messages", "conflicts", "files", "events"]
            counts = {}
            
            for table in tables:
                cursor = await self.connection.execute(f"SELECT COUNT(*) FROM {table}")
                row = await cursor.fetchone()
                counts[table] = row[0] if row else 0
            
            return {
                **self._stats,
                "table_counts": counts,
                "database_file": self.database_url
            }
            
        except Exception as e:
            logger.error(f"Error getting database stats: {str(e)}")
            return self._stats

    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.connection is not None

    async def close(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            self.connection = None
            logger.info("Database connection closed")
'''

    def _generate_config_module(self) -> str:
        """Generate configuration module with comprehensive settings"""
        
        return '''"""
Configuration management for BotArmy application.
Handles environment variables, settings validation, and application configuration.
"""

import os
from typing import Optional, List
from pydantic import BaseSettings, Field, validator
import logging

class Settings(BaseSettings):
    """Application settings loaded from environment variables with validation."""

    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o-mini", description="OpenAI model to use")
    openai_max_tokens: int = Field(default=2000, ge=1, le=8000, description="Maximum tokens per request")
    openai_temperature: float = Field(default=0.2, ge=0.0, le=2.0, description="Generation temperature")
    openai_timeout: int = Field(default=60, ge=10, le=300, description="Request timeout in seconds")

    # Database Configuration
    database_url: str = Field(default="sqlite:///./data/botarmy.db", description="Database connection URL")
    database_pool_size: int = Field(default=5, ge=1, le=20, description="Database connection pool size")

    # Application Configuration
    app_name: str = Field(default="BotArmy", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    max_concurrent_projects: int = Field(default=10, ge=1, le=100, description="Maximum concurrent projects")

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, ge=1, le=65535, description="Server port")
    workers: int = Field(default=1, ge=1, le=8, description="Number of worker processes")

    # Security Configuration
    secret_key: str = Field(default="your-secret-key-change-in-production", min_length=32, description="Secret key for sessions")
    cors_origins: List[str] = Field(default=["*"], description="CORS allowed origins")
    rate_limit_requests: int = Field(default=100, ge=1, description="Rate limit requests per minute")

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="./data/logs/app.log", description="Log file path")
    log_rotation: str = Field(default="1 day", description="Log rotation period")
    log_retention: str = Field(default="30 days", description="Log retention period")

    # File Storage Configuration
    upload_dir: str = Field(default="./data/uploads", description="File upload directory")
    max_file_size: int = Field(default=10485760, ge=1024, description="Maximum file size in bytes (10MB)")
    allowed_file_types: List[str] = Field(default=[".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".md", ".txt"], description="Allowed file extensions")

    # Agent Configuration
    agent_timeout: int = Field(default=300, ge=30, le=1800, description="Agent processing timeout in seconds")
    max_retries: int = Field(default=3, ge=1, le=10, description="Maximum retry attempts")
    retry_delay: float = Field(default=1.0, ge=0.1, le=10.0, description="Retry delay in seconds")

    # Workflow Configuration
    pipeline_timeout: int = Field(default=1800, ge=60, le=7200, description="Pipeline timeout in seconds")
    conflict_resolution_timeout: int = Field(default=3600, ge=60, description="Conflict resolution timeout")

    # Performance Configuration
    enable_caching: bool = Field(default=True, description="Enable response caching")
    cache_ttl: int = Field(default=300, ge=60, le=3600, description="Cache TTL in seconds")
    enable_compression: bool = Field(default=True, description="Enable response compression")

    # Monitoring Configuration
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    metrics_port: int = Field(default=8001, ge=1, le=65535, description="Metrics server port")

    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'log_level must be one of {valid_levels}')
        return v.upper()

    @validator('openai_api_key')
    def validate_api_key(cls, v):
        if not v or v == 'your_openai_api_key_here':
            raise ValueError('OpenAI API key must be provided')
        return v

    @validator('secret_key')
    def validate_secret_key(cls, v):
        if v == 'your-secret-key-change-in-production':
            import secrets
            return secrets.token_urlsafe(32)
        return v

    @validator('database_url')
    def validate_database_url(cls, v):
        if not v.startswith(('sqlite:///', 'postgresql://', 'mysql://')):
            raise ValueError('Invalid database URL format')
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        validate_assignment = True

    def create_directories(self):
        """Create necessary directories for the application"""
        directories = [
            os.path.dirname(self.database_url.replace("sqlite:///", "")),
            os.path.dirname(self.log_file),
            self.upload_dir,
            "./data/projects",
            "./data/backups",
            "./data/cache"
        ]
        
        for directory in directories:
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

    def setup_logging(self):
        """Setup application logging based on configuration"""
        
        # Ensure log directory exists
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )

        # Set specific logger levels
        logging.getLogger("uvicorn").setLevel(logging.INFO)
        logging.getLogger("fastapi").setLevel(logging.INFO)

    def get_database_config(self) -> dict:
        """Get database-specific configuration"""
        return {
            "url": self.database_url,
            "pool_size": self.database_pool_size,
            "timeout": 30,
            "echo": self.debug
        }

    def get_llm_config(self) -> dict:
        """Get LLM client configuration"""
        return {
            "api_key": self.openai_api_key,
            "model": self.openai_model,
            "max_tokens": self.openai_max_tokens,
            "temperature": self.openai_temperature,
            "timeout": self.openai_timeout,
            "max_retries": self.max_retries
        }

    def get_server_config(self) -> dict:
        """Get server configuration for uvicorn"""
        return {
            "host": self.host,
            "port": self.port,
            "workers": self.workers if not self.debug else 1,
            "reload": self.debug,
            "log_level": self.log_level.lower(),
            "access_log": True
        }

# Global settings instance
settings = Settings()

# Initialize directories and logging on import
settings.create_directories()
settings.setup_logging()

def get_settings() -> Settings:
    """Get application settings instance"""
    return settings

def reload_settings():
    """Reload settings from environment/config files"""
    global settings
    settings = Settings()
    settings.create_directories()
    settings.setup_logging()
    return settings
'''

    def _generate_llm_client(self) -> str:
        """Generate LLM client with enhanced features and error handling"""
        
        return '''"""
OpenAI API client with advanced retry logic, token tracking, and error handling.
Provides robust LLM integration with comprehensive monitoring and optimization.
"""

import asyncio
import json
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta

from openai import AsyncOpenAI, APIError, RateLimitError, APITimeoutError
from config import get_settings

logger = logging.getLogger(__name__)

@dataclass
class LLMMetrics:
    """Metrics tracking for LLM usage"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    average_response_time: float = 0.0
    last_request_time: Optional[datetime] = None

class LLMClient:
    """
    Advanced OpenAI API client with comprehensive error handling and monitoring.
    Features: retry logic, token tracking, cost calculation, rate limiting, caching.
    """

    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenAI(
            api_key=self.settings.openai_api_key,
            timeout=self.settings.openai_timeout
        )
        
        self.metrics = LLMMetrics()
        self._response_cache = {}
        self._rate_limiter = asyncio.Semaphore(10)  # Max 10 concurrent requests
        
        # Token costs per 1K tokens (GPT-4o-mini pricing as of 2024)
        self.token_costs = {
            "gpt-4o-mini": {
                "input": 0.00015,   # $0.15 per 1M input tokens
                "output": 0.0006    # $0.60 per 1M output tokens
            },
            "gpt-4o": {
                "input": 0.005,     # $5.00 per 1M input tokens  
                "output": 0.015     # $15.00 per 1M output tokens
            },
            "gpt-4-turbo": {
                "input": 0.01,      # $10.00 per 1M input tokens
                "output": 0.03      # $30.00 per 1M output tokens
            }
        }

    async def generate(self, prompt: str, max_tokens: int = None, 
                      temperature: float = None, max_retries: int = None,
                      system_message: str = None, use_cache: bool = True) -> str:
        """
        Generate completion from OpenAI API with comprehensive error handling.

        Args:
            prompt: Input prompt for completion
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-2)
            max_retries: Maximum retry attempts
            system_message: Optional system message
            use_cache: Whether to use response caching

        Returns:
            Generated text completion

        Raises:
            Exception: If all retry attempts fail
        """
        
        # Use defaults from settings
        max_tokens = max_tokens or self.settings.openai_max_tokens
        temperature = temperature or self.settings.openai_temperature
        max_retries = max_retries or self.settings.max_retries

        # Check cache first
        if use_cache:
            cache_key = self._generate_cache_key(prompt, max_tokens, temperature, system_message)
            if cache_key in self._response_cache:
                cached_response = self._response_cache[cache_key]
                if self._is_cache_valid(cached_response):
                    logger.debug("Using cached response")
                    return cached_response["content"]

        # Rate limiting
        async with self._rate_limiter:
            return await self._generate_with_retry(
                prompt, max_tokens, temperature, max_retries, system_message, use_cache
            )

    async def _generate_with_retry(self, prompt: str, max_tokens: int, 
                                  temperature: float, max_retries: int,
                                  system_message: str, use_cache: bool) -> str:
        """Internal method with retry logic"""
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                
                # Prepare messages
                messages = []
                if system_message:
                    messages.append({"role": "system", "content": system_message})
                messages.append({"role": "user", "content": prompt})

                # Make API request
                response = await self.client.chat.completions.create(
                    model=self.settings.openai_model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )

                # Track metrics
                processing_time = time.time() - start_time
                self._track_successful_request(response.usage, processing_time)

                completion = response.choices[0].message.content

                # Cache response if enabled
                if use_cache:
                    cache_key = self._generate_cache_key(prompt, max_tokens, temperature, system_message)
                    self._cache_response(cache_key, completion)

                logger.debug(f"LLM request completed in {processing_time:.2f}s")
                return completion

            except RateLimitError as e:
                logger.warning(f"Rate limit hit on attempt {attempt + 1}: {str(e)}")
                last_exception = e
                
                if attempt < max_retries:
                    # Exponential backoff with jitter
                    wait_time = (2 ** attempt) + (time.time() % 1)
                    await asyncio.sleep(wait_time)
                    continue

            except APITimeoutError as e:
                logger.warning(f"API timeout on attempt {attempt + 1}: {str(e)}")
                last_exception = e
                
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue

            except APIError as e:
                logger.error(f"API error on attempt {attempt + 1}: {str(e)}")
                last_exception = e
                
                # Don't retry on certain errors
                if e.status_code in [400, 401, 403]:
                    break
                    
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue

            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                last_exception = e
                
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue

        # All retries failed
        self._track_failed_request()
        raise Exception(f"LLM API failed after {max_retries + 1} attempts. Last error: {str(last_exception)}")

    def _track_successful_request(self, usage, processing_time: float):
        """Track successful request metrics"""
        
        if usage:
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens

            # Calculate cost
            model_costs = self.token_costs.get(self.settings.openai_model, self.token_costs["gpt-4o-mini"])
            input_cost = (input_tokens / 1000) * model_costs["input"]
            output_cost = (output_tokens / 1000) * model_costs["output"]
            request_cost = input_cost + output_cost

            # Update metrics
            self.metrics.total_requests += 1
            self.metrics.successful_requests += 1
            self.metrics.total_tokens += total_tokens
            self.metrics.total_cost += request_cost
            
            # Update average response time
            if self.metrics.average_response_time == 0:
                self.metrics.average_response_time = processing_time
            else:
                self.metrics.average_response_time = (
                    (self.metrics.average_response_time * (self.metrics.successful_requests - 1) + processing_time) /
                    self.metrics.successful_requests
                )
            
            self.metrics.last_request_time = datetime.now()

    def _track_failed_request(self):
        """Track failed request metrics"""
        self.metrics.total_requests += 1
        self.metrics.failed_requests += 1

    def _generate_cache_key(self, prompt: str, max_tokens: int, 
                           temperature: float, system_message: str) -> str:
        """Generate cache key for request parameters"""
        import hashlib
        
        key_data = f"{prompt}:{max_tokens}:{temperature}:{system_message or ''}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _cache_response(self, cache_key: str, content: str):
        """Cache response with timestamp"""
        self._response_cache[cache_key] = {
            "content": content,
            "timestamp": datetime.now(),
            "ttl": self.settings.cache_ttl if hasattr(self.settings, 'cache_ttl') else 300
        }

        # Clean old cache entries
        self._cleanup_cache()

    def _is_cache_valid(self, cached_response: Dict) -> bool:
        """Check if cached response is still valid"""
        if not cached_response:
            return False
            
        cache_age = datetime.now() - cached_response["timestamp"]
        return cache_age.total_seconds() < cached_response["ttl"]

    def _cleanup_cache(self):
        """Remove expired cache entries"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, cached_response in self._response_cache.items():
            cache_age = current_time - cached_response["timestamp"]
            if cache_age.total_seconds() >= cached_response["ttl"]:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._response_cache[key]

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get comprehensive usage statistics"""
        
        success_rate = (
            (self.metrics.successful_requests / self.metrics.total_requests * 100)
            if self.metrics.total_requests > 0 else 0
        )
        
        return {
            "total_requests": self.metrics.total_requests,
            "successful_requests": self.metrics.successful_requests,
            "failed_requests": self.metrics.failed_requests,
            "success_rate": round(success_rate, 2),
            "total_tokens": self.metrics.total_tokens,
            "total_cost": round(self.metrics.total_cost, 4),
            "average_response_time": round(self.metrics.average_response_time, 2),
            "average_tokens_per_request": (
                self.metrics.total_tokens / self.metrics.successful_requests 
                if self.metrics.successful_requests > 0 else 0
            ),
            "cache_size": len(self._response_cache),
            "last_request": self.metrics.last_request_time.isoformat() if self.metrics.last_request_time else None,
            "model": self.settings.openai_model
        }

    def reset_usage_stats(self):
        """Reset usage tracking counters"""
        self.metrics = LLMMetrics()
        logger.info("LLM usage statistics reset")

    def clear_cache(self):
        """Clear response cache"""
        self._response_cache.clear()
        logger.info("LLM response cache cleared")

    async def batch_generate(self, prompts: List[str], **kwargs) -> List[str]:
        """Generate completions for multiple prompts in parallel"""
        
        tasks = []
        for prompt in prompts:
            task = self.generate(prompt, **kwargs)
            tasks.append(task)
        
        try:
            results = await asyncio.gather(*tasks)
            return results
        except Exception as e:
            logger.error(f"Batch generation failed: {str(e)}")
            raise

    def get_health_status(self) -> Dict[str, Any]:
        """Get client health status"""
        
        recent_requests = self.metrics.total_requests >= 1
        recent_success = (
            self.metrics.successful_requests / max(self.metrics.total_requests, 1)
        ) >= 0.8
        
        status = "healthy" if recent_requests and recent_success else "degraded"
        
        return {
            "status": status,
            "api_key_configured": bool(self.settings.openai_api_key),
            "model": self.settings.openai_model,
            "last_request": self.metrics.last_request_time,
            "success_rate": (
                self.metrics.successful_requests / max(self.metrics.total_requests, 1) * 100
            )
        }
'''

    def _generate_base_agent(self) -> str:
        """Generate comprehensive base agent class"""
        
        return '''"""
Base agent class with comprehensive functionality for all BotArmy agents.
Provides common interfaces, error handling, state management, and communication.
"""

import time
import json
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    PROCESSING = "processing"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"

class BaseAgent(ABC):
    """
    Base class for all BotArmy agents providing comprehensive common functionality.
    Features: status management, error handling, message passing, metrics tracking.
    """

    def __init__(self, agent_type: str, llm_client, database, logger):
        self.agent_type = agent_type
        self.llm_client = llm_client
        self.database = database
        self.logger = logger or logging.getLogger(f"agents.{agent_type}")

        # State management
        self.status = AgentStatus.IDLE
        self.progress = 0
        self.current_project_id = None
        self.processing_data = {}

        # Timing and performance
        self.start_time = None
        self.processing_time = 0
        self.last_activity = datetime.now()

        # Error handling
        self.error_count = 0
        self.last_error = None
        self.max_errors = 5

        # Metrics
        self.metrics = {
            "total_processed": 0,
            "successful_completions": 0,
            "errors": 0,
            "average_processing_time": 0.0,
            "total_tokens_used": 0
        }

        # Message queue
        self.message_queue = []
        self.message_handlers = {}

        self.logger.info(f"{self.agent_type} agent initialized")

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return results.
        Must be implemented by each agent.
        
        Args:
            input_data: Input data for processing
            
        Returns:
            Processing results
        """
        pass

    async def initialize_processing(self, project_id: str, input_data: Dict[str, Any]) -> bool:
        """Initialize agent for processing a new project"""
        
        try:
            self.current_project_id = project_id
            self.start_time = time.time()
            self.processing_data = input_data.copy()
            self.progress = 0
            self.error_count = 0
            
            await self._update_status(AgentStatus.INITIALIZING, 0)
            
            # Validate input data
            if not await self._validate_input(input_data):
                raise ValueError("Input validation failed")
            
            self.logger.info(f"Initialized processing for project {project_id}")
            return True
            
        except Exception as e:
            await self._handle_error(f"Initialization failed: {str(e)}")
            return False

    async def finalize_processing(self, success: bool = True) -> Dict[str, Any]:
        """Finalize processing and return summary"""
        
        if self.start_time:
            self.processing_time = time.time() - self.start_time
            
        # Update metrics
        self.metrics["total_processed"] += 1
        if success:
            self.metrics["successful_completions"] += 1
            await self._update_status(AgentStatus.COMPLETED, 100)
        else:
            self.metrics["errors"] += 1
            await self._update_status(AgentStatus.ERROR, self.progress)

        # Update average processing time
        if self.metrics["successful_completions"] > 0:
            total_time = (self.metrics["average_processing_time"] * 
                         (self.metrics["successful_completions"] - 1) + self.processing_time)
            self.metrics["average_processing_time"] = total_time / self.metrics["successful_completions"]

        summary = {
            "agent_type": self.agent_type,
            "project_id": self.current_project_id,
            "status": self.status.value,
            "processing_time": self.processing_time,
            "success": success,
            "error_count": self.error_count,
            "tokens_used": getattr(self.llm_client, 'total_tokens_used', 0) - self.metrics["total_tokens_used"]
        }

        # Update token usage
        self.metrics["total_tokens_used"] = getattr(self.llm_client, 'total_tokens_used', 0)

        self.logger.info(f"Finalized processing: {summary}")
        return summary

    async def _update_status(self, status: AgentStatus, progress: int = None):
        """Update agent status and progress"""
        
        self.status = status
        if progress is not None:
            self.progress = max(0, min(100, progress))
        
        self.last_activity = datetime.now()

        # Update database
        if self.current_project_id:
            try:
                await self.database.update_agent_status(
                    project_id=self.current_project_id,
                    agent_type=self.agent_type,
                    status=status.value,
                    progress=self.progress
                )
            except Exception as e:
                self.logger.error(f"Failed to update database status: {str(e)}")

        self.logger.debug(f"{self.agent_type} status: {status.value} ({self.progress}%)")

    async def _handle_error(self, error_message: str, critical: bool = False):
        """Handle agent errors with logging and recovery"""
        
        self.error_count += 1
        self.last_error = {
            "message": error_message,
            "timestamp": datetime.now(),
            "project_id": self.current_project_id
        }

        self.logger.error(f"{self.agent_type} error: {error_message}")
        
        # Update status
        if critical or self.error_count >= self.max_errors:
            await self._update_status(AgentStatus.ERROR)
        
        # Log to database
        if self.current_project_id:
            try:
                await self.database.log_agent_error(
                    project_id=self.current_project_id,
                    agent_type=self.agent_type,
                    error_message=error_message
                )
            except Exception as e:
                self.logger.error(f"Failed to log error to database: {str(e)}")

        # Send error message to other agents if needed
        await self._broadcast_message({
            "type": "error",
            "message": error_message,
            "agent": self.agent_type,
            "critical": critical
        })

    async def _validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data - can be overridden by specific agents"""
        
        required_fields = getattr(self, 'REQUIRED_FIELDS', ['project_id'])
        
        for field in required_fields:
            if field not in input_data:
                await self._handle_error(f"Missing required field: {field}")
                return False
        
        return True

    async def _send_message(self, to_agent: str, content: Dict[str, Any], 
                           message_type: str = "info") -> str:
        """Send message to another agent"""
        
        try:
            message_id = await self.database.create_message(
                project_id=self.current_project_id,
                from_agent=self.agent_type,
                to_agent=to_agent,
                content={
                    "type": message_type,
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            self.logger.debug(f"Message sent to {to_agent}: {message_id}")
            return message_id
            
        except Exception as e:
            self.logger.error(f"Failed to send message to {to_agent}: {str(e)}")
            raise

    async def _broadcast_message(self, content: Dict[str, Any], message_type: str = "broadcast"):
        """Broadcast message to all other agents"""
        
        other_agents = ["analyst", "architect", "developer", "tester"]
        other_agents.remove(self.agent_type)
        
        tasks = []
        for agent in other_agents:
            task = self._send_message(agent, content, message_type)
            tasks.append(task)
        
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            self.logger.error(f"Broadcast failed: {str(e)}")

    async def _receive_messages(self) -> List[Dict[str, Any]]:
        """Receive pending messages for this agent"""
        
        if not self.current_project_id:
            return []
        
        try:
            messages = await self.database.get_agent_messages(
                self.current_project_id, 
                self.agent_type
            )
            return messages
        except Exception as e:
            self.logger.error(f"Failed to receive messages: {str(e)}")
            return []

    def register_message_handler(self, message_type: str, handler_func):
        """Register handler for specific message types"""
        self.message_handlers[message_type] = handler_func

    async def process_messages(self):
        """Process pending messages using registered handlers"""
        
        messages = await self._receive_messages()
        
        for message in messages:
            try:
                content = message.get("content", {})
                msg_type = content.get("type", "info")
                
                if msg_type in self.message_handlers:
                    await self.message_handlers[msg_type](message)
                else:
                    await self._handle_default_message(message)
                    
            except Exception as e:
                self.logger.error(f"Error processing message: {str(e)}")

    async def _handle_default_message(self, message: Dict[str, Any]):
        """Default message handler"""
        self.logger.info(f"Received message from {message.get('from_agent', 'unknown')}")

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status"""
        
        return {
            "agent_type": self.agent_type,
            "status": self.status.value,
            "progress": self.progress,
            "project_id": self.current_project_id,
            "processing_time": self.processing_time,
            "last_activity": self.last_activity.isoformat(),
            "error_count": self.error_count,
            "last_error": self.last_error,
            "metrics": self.metrics.copy()
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        
        success_rate = (
            (self.metrics["successful_completions"] / max(self.metrics["total_processed"], 1)) * 100
        )
        
        return {
            **self.metrics,
            "success_rate": round(success_rate, 2),
            "errors_per_processing": (
                self.metrics["errors"] / max(self.metrics["total_processed"], 1)
            ),
            "average_tokens_per_processing": (
                self.metrics["total_tokens_used"] / max(self.metrics["total_processed"], 1)
            )
        }

    async def pause_processing(self):
        """Pause current processing"""
        if self.status == AgentStatus.PROCESSING:
            await self._update_status(AgentStatus.WAITING)
            self.logger.info(f"{self.agent_type} processing paused")

    async def resume_processing(self):
        """Resume paused processing"""
        if self.status == AgentStatus.WAITING:
            await self._update_status(AgentStatus.PROCESSING, self.progress)
            self.logger.info(f"{self.agent_type} processing resumed")

    async def cancel_processing(self):
        """Cancel current processing"""
        await self._update_status(AgentStatus.CANCELLED)
        self.logger.info(f"{self.agent_type} processing cancelled")

    def reset_state(self):
        """Reset agent to initial state"""
        self.status = AgentStatus.IDLE
        self.progress = 0
        self.current_project_id = None
        self.processing_data = {}
        self.start_time = None
        self.processing_time = 0
        self.error_count = 0
        self.last_error = None
        self.message_queue = []
        
        self.logger.info(f"{self.agent_type} state reset")

    def __repr__(self):
        return f"<{self.__class__.__name__}(type={self.agent_type}, status={self.status.value})>"
'''
'''
            