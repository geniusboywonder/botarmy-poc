"""
Backend code generator for FastAPI and Python components.
"""

import json
from typing import Dict, Any, List

class BackendGenerator:
    """Generates backend Python code files."""
    
    def __init__(self, llm_client, logger):
        self.llm_client = llm_client
        self.logger = logger
    
    async def generate_fastapi_main(self, architecture: Dict, tech_stack: Dict, 
                                   specifications: Dict) -> str:
        """Generate main FastAPI application file."""
        
        from ...prompts.developer_prompts import DEVELOPER_PROMPTS
        
        prompt = DEVELOPER_PROMPTS["fastapi_main"].format(
            api_endpoints=json.dumps(specifications.get("api_endpoints", []), indent=2),
            architecture=json.dumps(architecture, indent=2)
        )

        response = await self.llm_client.generate(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.1
        )

        return response.strip()

    async def generate_database_module(self, schema: Dict) -> str:
        """Generate database operations module."""
        
        from ...prompts.developer_prompts import DEVELOPER_PROMPTS
        
        prompt = DEVELOPER_PROMPTS["database_module"].format(
            schema=json.dumps(schema, indent=2)
        )

        response = await self.llm_client.generate(
            prompt=prompt,
            max_tokens=1500,
            temperature=0.1
        )

        return response.strip()

    def generate_config_module(self) -> str:
        """Generate configuration module."""
        
        return '''"""
Configuration management for BotArmy application.
"""

import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 2000
    openai_temperature: float = 0.2

    # Database Configuration
    database_url: str = "sqlite:///./data/botarmy.db"

    # Application Configuration
    app_name: str = "BotArmy"
    app_version: str = "1.0.0"
    debug: bool = False

    # Replit Configuration
    replit_db_url: Optional[str] = None

    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "./data/logs/app.log"

    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings."""
    return settings
'''

    def generate_llm_client(self) -> str:
        """Generate LLM client module."""
        
        return '''"""
OpenAI API client with retry logic and error handling.
"""

import asyncio
import json
import time
from typing import Optional, Dict, Any
from openai import AsyncOpenAI
from config import get_settings

class LLMClient:
    """
    Simplified OpenAI API client with built-in retry logic and token tracking.
    """

    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        self.total_tokens_used = 0
        self.total_requests = 0
        self.total_cost = 0.0

        # Token costs per 1K tokens (GPT-4o-mini pricing)
        self.token_costs = {
            "input": 0.00015,   # $0.15 per 1M input tokens
            "output": 0.0006    # $0.60 per 1M output tokens
        }

    async def generate(self, prompt: str, max_tokens: int = None, 
                      temperature: float = None, max_retries: int = 3) -> str:
        """
        Generate completion from OpenAI API with retry logic.

        Args:
            prompt: Input prompt for completion
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            max_retries: Maximum retry attempts

        Returns:
            Generated text completion

        Raises:
            Exception: If all retry attempts fail
        """
        max_tokens = max_tokens or self.settings.openai_max_tokens
        temperature = temperature or self.settings.openai_temperature

        for attempt in range(max_retries):
            try:
                start_time = time.time()

                response = await self.client.chat.completions.create(
                    model=self.settings.openai_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )

                # Track usage and costs
                self._track_usage(response.usage)

                completion = response.choices[0].message.content
                processing_time = time.time() - start_time

                self.total_requests += 1

                return completion

            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"LLM API failed after {max_retries} attempts: {str(e)}")

                # Exponential backoff
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)

    def _track_usage(self, usage):
        """Track token usage and calculate costs."""
        if usage:
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens

            # Calculate costs
            input_cost = (input_tokens / 1000) * self.token_costs["input"]
            output_cost = (output_tokens / 1000) * self.token_costs["output"]
            request_cost = input_cost + output_cost

            self.total_tokens_used += total_tokens
            self.total_cost += request_cost

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics."""
        return {
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens_used,
            "total_cost": round(self.total_cost, 4),
            "average_tokens_per_request": (
                self.total_tokens_used / self.total_requests 
                if self.total_requests > 0 else 0
            )
        }

    def reset_usage_stats(self):
        """Reset usage tracking counters."""
        self.total_tokens_used = 0
        self.total_requests = 0
        self.total_cost = 0.0
'''

    def generate_workflow_pipeline(self) -> str:
        """Generate workflow pipeline module."""
        
        return '''"""
Agent workflow pipeline for sequential processing.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from enum import Enum

class WorkflowStage(Enum):
    """Workflow stages enum."""
    IDLE = "idle"
    ANALYZING = "analyzing"
    ARCHITECTING = "architecting"
    DEVELOPING = "developing"
    TESTING = "testing"
    COMPLETED = "completed"
    ERROR = "error"

class WorkflowPipeline:
    """
    Orchestrates sequential agent processing pipeline.
    """

    def __init__(self, database, logger):
        self.database = database
        self.logger = logger
        self.current_stage = WorkflowStage.IDLE
        self.project_id = None
        self.pipeline_data = {}

    async def start_pipeline(self, project_id: str, requirements: str) -> Dict[str, Any]:
        """Start the agent workflow pipeline."""
        
        self.project_id = project_id
        self.current_stage = WorkflowStage.ANALYZING
        
        # Initialize pipeline data
        self.pipeline_data = {
            "project_id": project_id,
            "requirements": requirements,
            "stage_results": {},
            "errors": [],
            "start_time": asyncio.get_event_loop().time()
        }

        self.logger.info(f"Starting workflow pipeline for project {project_id}")
        
        return {
            "status": "started",
            "project_id": project_id,
            "current_stage": self.current_stage.value
        }

    async def process_stage(self, stage: WorkflowStage, agent, input_data: Dict) -> Dict[str, Any]:
        """Process a single workflow stage."""
        
        try:
            self.logger.info(f"Processing stage: {stage.value}")
            self.current_stage = stage
            
            # Update database with current stage
            await self.database.update_project_stage(
                project_id=self.project_id,
                stage=stage.value
            )

            # Process with agent
            result = await agent.process(input_data)
            
            # Store stage result
            self.pipeline_data["stage_results"][stage.value] = result
            
            self.logger.info(f"Completed stage: {stage.value}")
            return result

        except Exception as e:
            error_msg = f"Stage {stage.value} failed: {str(e)}"
            self.logger.error(error_msg)
            
            self.pipeline_data["errors"].append({
                "stage": stage.value,
                "error": error_msg,
                "timestamp": asyncio.get_event_loop().time()
            })
            
            self.current_stage = WorkflowStage.ERROR
            raise

    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status."""
        
        return {
            "project_id": self.project_id,
            "current_stage": self.current_stage.value,
            "completed_stages": list(self.pipeline_data["stage_results"].keys()),
            "errors": self.pipeline_data["errors"],
            "processing_time": (
                asyncio.get_event_loop().time() - 
                self.pipeline_data.get("start_time", 0)
            )
        }

    async def handle_conflict(self, conflict_data: Dict) -> Dict[str, Any]:
        """Handle agent conflicts during pipeline."""
        
        conflict_id = await self.database.create_conflict(
            project_id=self.project_id,
            description=conflict_data.get("description"),
            agents_involved=conflict_data.get("agents", []),
            stage=self.current_stage.value
        )

        self.logger.warning(f"Conflict detected in stage {self.current_stage.value}: {conflict_id}")
        
        return {
            "conflict_id": conflict_id,
            "requires_human_intervention": True,
            "conflict_data": conflict_data
        }

    def reset_pipeline(self):
        """Reset pipeline for new project."""
        self.current_stage = WorkflowStage.IDLE
        self.project_id = None
        self.pipeline_data = {}
'''

    async def generate_agent_files(self, specifications: Dict) -> Dict[str, str]:
        """Generate all backend agent-related files."""
        
        files = {}
        
        # Generate workflow state manager
        files["workflow/state_manager.py"] = self._generate_state_manager()
        
        # Generate agent manager
        files["agents/agent_manager.py"] = self._generate_agent_manager()
        
        return files

    def _generate_state_manager(self) -> str:
        """Generate state manager for workflow."""
        
        return '''"""
State management for workflow pipeline.
"""

import json
import asyncio
from typing import Dict, Any, Optional
from enum import Enum

class StateManager:
    """
    Manages workflow state transitions and persistence.
    """

    def __init__(self, database, logger):
        self.database = database
        self.logger = logger
        self._state_cache = {}

    async def save_state(self, project_id: str, state_data: Dict[str, Any]):
        """Save workflow state to database."""
        
        state_json = json.dumps(state_data)
        
        await self.database.update_project_metadata(
            project_id=project_id,
            metadata={"workflow_state": state_data}
        )
        
        self._state_cache[project_id] = state_data
        self.logger.debug(f"Saved state for project {project_id}")

    async def load_state(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Load workflow state from database."""
        
        if project_id in self._state_cache:
            return self._state_cache[project_id]

        project_data = await self.database.get_project(project_id)
        if project_data and project_data.get("metadata"):
            state_data = project_data["metadata"].get("workflow_state")
            if state_data:
                self._state_cache[project_id] = state_data
                return state_data

        return None

    async def transition_state(self, project_id: str, from_state: str, to_state: str) -> bool:
        """Perform state transition with validation."""
        
        valid_transitions = {
            "idle": ["analyzing"],
            "analyzing": ["architecting", "error"],
            "architecting": ["developing", "error"],
            "developing": ["testing", "error"],
            "testing": ["completed", "error"],
            "error": ["analyzing", "architecting", "developing", "testing"],
            "completed": []
        }

        if to_state not in valid_transitions.get(from_state, []):
            self.logger.error(f"Invalid state transition: {from_state} -> {to_state}")
            return False

        # Update state
        state_data = await self.load_state(project_id) or {}
        state_data["current_stage"] = to_state
        state_data["previous_stage"] = from_state
        state_data["transition_time"] = asyncio.get_event_loop().time()

        await self.save_state(project_id, state_data)
        
        self.logger.info(f"State transition: {from_state} -> {to_state}")
        return True

    def clear_cache(self, project_id: str = None):
        """Clear state cache."""
        if project_id:
            self._state_cache.pop(project_id, None)
        else:
            self._state_cache.clear()
'''

    def _generate_agent_manager(self) -> str:
        """Generate agent manager for coordinating agents."""
        
        return '''"""
Agent manager for coordinating multiple agents.
"""

import asyncio
from typing import Dict, List, Any, Optional

class AgentManager:
    """
    Coordinates multiple agents and manages their interactions.
    """

    def __init__(self, database, logger):
        self.database = database
        self.logger = logger
        self.agents = {}
        self.active_projects = {}

    def register_agent(self, agent_type: str, agent_instance):
        """Register an agent with the manager."""
        self.agents[agent_type] = agent_instance
        self.logger.info(f"Registered agent: {agent_type}")

    async def process_project(self, project_id: str, requirements: str) -> Dict[str, Any]:
        """Process a complete project through all agents."""
        
        self.active_projects[project_id] = {
            "status": "processing",
            "current_agent": None,
            "results": {}
        }

        try:
            # Stage 1: Analyst
            analyst_result = await self._run_agent("analyst", project_id, {
                "project_id": project_id,
                "requirements": requirements
            })

            # Stage 2: Architect
            architect_result = await self._run_agent("architect", project_id, analyst_result)

            # Stage 3: Developer
            developer_result = await self._run_agent("developer", project_id, architect_result)

            # Stage 4: Tester
            tester_result = await self._run_agent("tester", project_id, developer_result)

            # Mark project as completed
            self.active_projects[project_id]["status"] = "completed"
            
            return {
                "project_id": project_id,
                "status": "completed",
                "results": {
                    "analyst": analyst_result,
                    "architect": architect_result,
                    "developer": developer_result,
                    "tester": tester_result
                }
            }

        except Exception as e:
            self.active_projects[project_id]["status"] = "error"
            self.logger.error(f"Project processing failed: {str(e)}")
            raise

    async def _run_agent(self, agent_type: str, project_id: str, input_data: Dict) -> Dict[str, Any]:
        """Run a specific agent with input data."""
        
        if agent_type not in self.agents:
            raise ValueError(f"Agent {agent_type} not registered")

        self.active_projects[project_id]["current_agent"] = agent_type
        agent = self.agents[agent_type]

        self.logger.info(f"Running agent {agent_type} for project {project_id}")
        
        try:
            result = await agent.process(input_data)
            self.active_projects[project_id]["results"][agent_type] = result
            return result

        except Exception as e:
            self.logger.error(f"Agent {agent_type} failed: {str(e)}")
            raise

    async def get_project_status(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a project."""
        
        if project_id not in self.active_projects:
            # Try to load from database
            project_data = await self.database.get_project(project_id)
            if project_data:
                return {
                    "project_id": project_id,
                    "status": project_data.get("status", "unknown"),
                    "current_agent": None
                }
            return None

        return self.active_projects[project_id]

    async def handle_agent_error(self, project_id: str, agent_type: str, error: str):
        """Handle agent processing errors."""
        
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
                "message": error
            }

    def get_all_agents(self) -> Dict[str, Any]:
        """Get information about all registered agents."""
        
        return {
            agent_type: {
                "type": agent_type,
                "status": "ready" if agent else "not_loaded"
            }
            for agent_type, agent in self.agents.items()
        }
'''
