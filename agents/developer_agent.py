import json
import asyncio
import os
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from ..prompts.developer_prompts import DEVELOPER_PROMPTS

class DeveloperAgent(BaseAgent):
    """
    Developer Agent responsible for generating working code implementations
    based on architectural specifications from the Architect Agent.
    """

    def __init__(self, llm_client, database, logger):
        super().__init__(
            agent_type="developer",
            llm_client=llm_client,
            database=database,
            logger=logger
        )
        self.supported_languages = ["python", "javascript", "typescript", "html", "css", "sql"]
        self.code_templates = {
            "fastapi": self._get_fastapi_templates(),
            "react": self._get_react_templates(),
            "database": self._get_database_templates()
        }
        self.quality_checks = {
            "syntax": True,
            "security": True,
            "performance": True,
            "documentation": True
        }

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process architect output and generate working code implementations.

        Args:
            input_data: Dictionary containing architect output with technical specifications

        Returns:
            Dictionary containing generated code files and implementation details
        """
        try:
            self.logger.info(f"Developer agent processing input for project {input_data.get('project_id')}")

            # Extract architectural specifications
            architecture = input_data.get('system_architecture', {})
            tech_stack = input_data.get('technology_stack', {})
            file_structure = input_data.get('file_structure', {})
            specifications = input_data.get('technical_specifications', {})

            # Update agent status
            await self._update_status("analyzing_architecture")

            # Step 1: Plan code generation
            generation_plan = await self._create_generation_plan(
                architecture, tech_stack, file_structure, specifications
            )

            # Step 2: Generate backend code
            await self._update_status("generating_backend")
            backend_files = await self._generate_backend_code(
                generation_plan, architecture, tech_stack, specifications
            )

            # Step 3: Generate frontend code
            await self._update_status("generating_frontend")
            frontend_files = await self._generate_frontend_code(
                generation_plan, architecture, tech_stack, specifications
            )

            # Step 4: Generate configuration files
            await self._update_status("generating_config")
            config_files = await self._generate_configuration_files(
                generation_plan, tech_stack
            )

            # Step 5: Generate documentation
            await self._update_status("generating_documentation")
            documentation_files = await self._generate_documentation(
                generation_plan, architecture, tech_stack, backend_files, frontend_files
            )

            # Step 6: Perform quality checks
            await self._update_status("quality_checking")
            quality_report = await self._perform_quality_checks(
                backend_files, frontend_files, config_files
            )

            # Step 7: Package final output
            await self._update_status("packaging_output")

            # Compile all generated files
            all_files = {
                **backend_files,
                **frontend_files,
                **config_files,
                **documentation_files
            }

            output = {
                "project_id": input_data.get('project_id'),
                "generated_files": all_files,
                "file_count": len(all_files),
                "generation_plan": generation_plan,
                "implementation_notes": self._create_implementation_notes(generation_plan),
                "quality_report": quality_report,
                "deployment_instructions": self._create_deployment_instructions(tech_stack),
                "next_steps": self._create_next_steps(quality_report),
                "agent_metadata": {
                    "agent_type": self.agent_type,
                    "processing_time": self.processing_time,
                    "token_usage": self.token_usage,
                    "lines_of_code": self._count_lines_of_code(all_files),
                    "confidence_score": self._calculate_confidence(quality_report)
                }
            }

            # Save files to project directory
            await self._save_generated_files(input_data.get('project_id'), all_files)

            await self._update_status("completed")
            self.logger.info(f"Developer agent completed processing for project {input_data.get('project_id')}")

            return output

        except Exception as e:
            await self._handle_error(f"Developer agent processing failed: {str(e)}")
            raise

    async def _create_generation_plan(self, architecture: Dict, tech_stack: Dict, 
                                    file_structure: Dict, specifications: Dict) -> Dict:
        """Create a plan for code generation based on specifications."""

        prompt = DEVELOPER_PROMPTS["create_generation_plan"].format(
            architecture=json.dumps(architecture, indent=2),
            tech_stack=json.dumps(tech_stack, indent=2),
            file_structure=json.dumps(file_structure, indent=2),
            specifications=json.dumps(specifications, indent=2)
        )

        response = await self.llm_client.generate(
            prompt=prompt,
            max_tokens=1500,
            temperature=0.2
        )

        try:
            plan = json.loads(response)
            return {
                "generation_order": plan.get("generation_order", []),
                "dependencies": plan.get("dependencies", {}),
                "complexity_assessment": plan.get("complexity", "medium"),
                "estimated_files": plan.get("estimated_files", 10),
                "critical_components": plan.get("critical_components", []),
                "integration_points": plan.get("integration_points", []),
                "testing_strategy": plan.get("testing_strategy", {})
            }
        except json.JSONDecodeError:
            return self._create_default_generation_plan()

    async def _generate_backend_code(self, plan: Dict, architecture: Dict, 
                                   tech_stack: Dict, specifications: Dict) -> Dict:
        """Generate backend code files."""

        backend_files = {}

        # Generate main FastAPI application
        backend_files["main.py"] = await self._generate_fastapi_main(
            architecture, tech_stack, specifications
        )

        # Generate database module
        backend_files["database.py"] = await self._generate_database_module(
            specifications.get("database_schema", {})
        )

        # Generate configuration module
        backend_files["config.py"] = await self._generate_config_module()

        # Generate LLM client
        backend_files["llm_client.py"] = await self._generate_llm_client()

        # Generate base agent class
        backend_files["agents/__init__.py"] = ""
        backend_files["agents/base_agent.py"] = await self._generate_base_agent()

        # Generate workflow manager
        backend_files["workflow/__init__.py"] = ""
        backend_files["workflow/pipeline.py"] = await self._generate_workflow_pipeline()
        backend_files["workflow/state_manager.py"] = await self._generate_state_manager()

        return backend_files

    async def _generate_frontend_code(self, plan: Dict, architecture: Dict,
                                    tech_stack: Dict, specifications: Dict) -> Dict:
        """Generate frontend React code files."""

        frontend_files = {}

        # Generate main App component
        frontend_files["src/App.jsx"] = await self._generate_react_app()

        # Generate context for state management
        frontend_files["src/context/AppContext.js"] = await self._generate_app_context()

        # Generate core components
        components = ["Dashboard", "AgentPanel", "ActionQueue", "ProjectViewer", "StatusBar"]
        for component in components:
            frontend_files[f"src/components/{component}.jsx"] = await self._generate_react_component(
                component, specifications.get("component_specifications", {})
            )

        # Generate utility modules
        frontend_files["src/utils/api.js"] = await self._generate_api_utils()
        frontend_files["src/utils/formatting.js"] = await self._generate_formatting_utils()

        # Generate package.json
        frontend_files["package.json"] = await self._generate_package_json(tech_stack)

        # Generate index files
        frontend_files["src/index.js"] = await self._generate_react_index()
        frontend_files["public/index.html"] = await self._generate_html_template()

        return frontend_files

    async def _generate_configuration_files(self, plan: Dict, tech_stack: Dict) -> Dict:
        """Generate configuration and deployment files."""

        config_files = {}

        # Generate requirements.txt
        config_files["requirements.txt"] = await self._generate_requirements_txt()

        # Generate environment template
        config_files[".env.example"] = await self._generate_env_template()

        # Generate Replit configuration
        config_files["replit.nix"] = await self._generate_replit_config()
        config_files[".replit"] = await self._generate_replit_file()

        # Generate Docker files for alternative deployment
        config_files["Dockerfile"] = await self._generate_dockerfile()
        config_files["docker-compose.yml"] = await self._generate_docker_compose()

        # Generate .gitignore
        config_files[".gitignore"] = await self._generate_gitignore()

        return config_files

    async def _generate_documentation(self, plan: Dict, architecture: Dict, tech_stack: Dict,
                                    backend_files: Dict, frontend_files: Dict) -> Dict:
        """Generate project documentation."""

        doc_files = {}

        # Generate main README
        doc_files["README.md"] = await self._generate_readme(
            architecture, tech_stack, plan
        )

        # Generate API documentation
        doc_files["docs/API.md"] = await self._generate_api_docs(backend_files)

        # Generate deployment guide
        doc_files["docs/DEPLOYMENT.md"] = await self._generate_deployment_docs(tech_stack)

        # Generate developer guide
        doc_files["docs/DEVELOPMENT.md"] = await self._generate_development_docs(
            backend_files, frontend_files
        )

        return doc_files

    # Code generation methods for specific files

    async def _generate_fastapi_main(self, architecture: Dict, tech_stack: Dict, 
                                   specifications: Dict) -> str:
        """Generate main FastAPI application file."""

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

    async def _generate_database_module(self, schema: Dict) -> str:
        """Generate database module with SQLite operations."""

        prompt = DEVELOPER_PROMPTS["database_module"].format(
            schema=json.dumps(schema, indent=2)
        )

        response = await self.llm_client.generate(
            prompt=prompt,
            max_tokens=1500,
            temperature=0.1
        )

        return response.strip()

    async def _generate_config_module(self) -> str:
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
    database_url: str = "sqlite:///./data/messages.db"

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

    async def _generate_llm_client(self) -> str:
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

    async def _generate_base_agent(self) -> str:
        """Generate base agent class."""

        return '''"""
Base agent class with common functionality for all BotArmy agents.
"""

import time
import json
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from database import Database

class BaseAgent(ABC):
    """
    Base class for all BotArmy agents providing common functionality.
    """

    def __init__(self, agent_type: str, llm_client, database: Database, logger):
        self.agent_type = agent_type
        self.llm_client = llm_client
        self.database = database
        self.logger = logger

        # Tracking variables
        self.start_time = None
        self.processing_time = 0
        self.token_usage = 0
        self.status = "idle"
        self.progress = 0
        self.current_project_id = None

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return results.
        Must be implemented by each agent.
        """
        pass

    async def _update_status(self, status: str, progress: int = None):
        """Update agent status in database and log."""
        self.status = status
        if progress is not None:
            self.progress = progress

        # Update database
        if self.current_project_id:
            await self.database.update_agent_status(
                project_id=self.current_project_id,
                agent_type=self.agent_type,
                status=status,
                progress=self.progress
            )

        # Log status change
        self.logger.info(f"{self.agent_type} agent status: {status} ({self.progress}%)")

    async def _handle_error(self, error_message: str):
        """Handle agent errors with logging and status update."""
        self.logger.error(f"{self.agent_type} agent error: {error_message}")
        await self._update_status("error", self.progress)

        # Save error to database
        if self.current_project_id:
            await self.database.log_agent_error(
                project_id=self.current_project_id,
                agent_type=self.agent_type,
                error_message=error_message
            )

    async def _send_message(self, to_agent: str, content: Dict[str, Any]):
        """Send message to another agent through the message queue."""
        message_id = await self.database.create_message(
            project_id=self.current_project_id,
            from_agent=self.agent_type,
            to_agent=to_agent,
            content=content
        )

        self.logger.info(f"Message sent from {self.agent_type} to {to_agent}: {message_id}")
        return message_id

    async def _validate_input(self, input_data: Dict[str, Any], required_fields: list) -> bool:
        """Validate that input data contains required fields."""
        missing_fields = [field for field in required_fields if field not in input_data]

        if missing_fields:
            error_msg = f"Missing required fields: {missing_fields}"
            await self._handle_error(error_msg)
            return False

        return True

    def _start_processing(self, project_id: str):
        """Initialize processing tracking."""
        self.current_project_id = project_id
        self.start_time = time.time()
        self.status = "processing"
        self.progress = 0

    def _finish_processing(self):
        """Finalize processing tracking."""
        if self.start_time:
            self.processing_time = time.time() - self.start_time
        self.status = "completed"
        self.progress = 100

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_type": self.agent_type,
            "status": self.status,
            "progress": self.progress,
            "processing_time": self.processing_time,
            "project_id": self.current_project_id
        }
'''

    async def _generate_react_app(self) -> str:
        """Generate main React App component."""

        return '''import React from 'react';
import { AppProvider } from './context/AppContext';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  return (
    <AppProvider>
      <div className="App min-h-screen bg-gray-50">
        <Dashboard />
      </div>
    </AppProvider>
  );
}

export default App;
'''

    async def _generate_app_context(self) -> str:
        """Generate React context for state management."""

        return '''import React, { createContext, useContext, useState, useEffect } from 'react';

const AppContext = createContext();

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

export const AppProvider = ({ children }) => {
  // Main application state
  const [project, setProject] = useState({
    id: null,
    requirements: '',
    status: 'idle',
    createdAt: null
  });

  const [agents, setAgents] = useState({
    analyst: { status: 'idle', progress: 0, messages: [] },
    architect: { status: 'idle', progress: 0, messages: [] },
    developer: { status: 'idle', progress: 0, messages: [] },
    tester: { status: 'idle', progress: 0, messages: [] }
  });

  const [actionQueue, setActionQueue] = useState([]);
  const [files, setFiles] = useState({ generated: [], uploads: [] });
  const [systemStatus, setSystemStatus] = useState({
    connected: false,
    performance: { cpu: 0, memory: 0 },
    tokenUsage: { total: 0, cost: 0 }
  });

  // Server-Sent Events connection
  useEffect(() => {
    const eventSource = new EventSource('/api/stream');

    eventSource.onopen = () => {
      setSystemStatus(prev => ({ ...prev, connected: true }));
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleRealtimeUpdate(data);
      } catch (error) {
        console.error('Error parsing SSE data:', error);
      }
    };

    eventSource.onerror = () => {
      setSystemStatus(prev => ({ ...prev, connected: false }));
    };

    return () => {
      eventSource.close();
    };
  }, []);

  // Handle real-time updates from backend
  const handleRealtimeUpdate = (data) => {
    switch (data.type) {
      case 'agent_status':
        setAgents(prev => ({
          ...prev,
          [data.agent]: {
            ...prev[data.agent],
            status: data.status,
            progress: data.progress
          }
        }));
        break;

      case 'message_new':
        setAgents(prev => ({
          ...prev,
          [data.agent]: {
            ...prev[data.agent],
            messages: [...prev[data.agent].messages, data.message]
          }
        }));
        break;

      case 'conflict_detected':
        setActionQueue(prev => [...prev, {
          id: data.id,
          type: 'conflict',
          description: data.description,
          timestamp: new Date(),
          resolved: false
        }]);
        break;

      case 'project_complete':
        setProject(prev => ({ ...prev, status: 'completed' }));
        setFiles(prev => ({ ...prev, generated: data.files }));
        break;

      default:
        console.log('Unknown event type:', data.type);
    }
  };

  // API functions
  const startProject = async (requirements) => {
    try {
      const response = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ requirements })
      });

      const data = await response.json();
      setProject({
        id: data.project_id,
        requirements,
        status: 'processing',
        createdAt: new Date()
      });

      return data;
    } catch (error) {
      console.error('Error starting project:', error);
      throw error;
    }
  };

  const resolveAction = async (actionId, resolution) => {
    try {
      await fetch('/api/conflicts/resolve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action_id: actionId, resolution })
      });

      setActionQueue(prev => 
        prev.map(action => 
          action.id === actionId 
            ? { ...action, resolved: true, resolution }
            : action
        )
      );
    } catch (error) {
      console.error('Error resolving action:', error);
      throw error;
    }
  };

  // Persist state to localStorage
  useEffect(() => {
    const state = { project, agents, actionQueue, files };
    localStorage.setItem('botarmy-state', JSON.stringify(state));
  }, [project, agents, actionQueue, files]);

  // Load state from localStorage on mount
  useEffect(() => {
    const savedState = localStorage.getItem('botarmy-state');
    if (savedState) {
      try {
        const { project: savedProject, agents: savedAgents, 
                actionQueue: savedQueue, files: savedFiles } = JSON.parse(savedState);
        if (savedProject) setProject(savedProject);
        if (savedAgents) setAgents(savedAgents);
        if (savedQueue) setActionQueue(savedQueue);
        if (savedFiles) setFiles(savedFiles);
      } catch (error) {
        console.error('Error loading saved state:', error);
      }
    }
  }, []);

  const value = {
    // State
    project,
    agents,
    actionQueue,
    files,
    systemStatus,

    // Actions
    startProject,
    resolveAction,
    setProject,
    setAgents,
    setActionQueue,
    setFiles
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};
'''

    async def _perform_quality_checks(self, backend_files: Dict, frontend_files: Dict, 
                                    config_files: Dict) -> Dict:
        """Perform basic quality checks on generated code."""

        issues = []
        warnings = []

        # Check for required files
        required_backend = ["main.py", "database.py", "config.py"]
        required_frontend = ["src/App.jsx", "package.json"]
        required_config = ["requirements.txt", ".env.example"]

        for file in required_backend:
            if file not in backend_files:
                issues.append(f"Missing required backend file: {file}")

        for file in required_frontend:
            if file not in frontend_files:
                issues.append(f"Missing required frontend file: {file}")

        for file in required_config:
            if file not in config_files:
                issues.append(f"Missing required config file: {file}")

        # Basic syntax checks (simplified)
        for filename, content in backend_files.items():
            if filename.endswith('.py'):
                if 'import' not in content:
                    warnings.append(f"Python file {filename} may be missing imports")
                if 'def ' not in content and 'class ' not in content:
                    warnings.append(f"Python file {filename} may be missing functions/classes")

        # Security checks
        security_issues = []
        for filename, content in {**backend_files, **frontend_files}.items():
            if 'password' in content.lower() and 'hash' not in content.lower():
                security_issues.append(f"Potential hardcoded password in {filename}")
            if 'api_key' in content and 'env' not in content.lower():
                security_issues.append(f"Potential hardcoded API key in {filename}")

        return {
            "issues": issues,
            "warnings": warnings,
            "security_issues": security_issues,
            "total_files": len(backend_files) + len(frontend_files) + len(config_files),
            "quality_score": self._calculate_quality_score(issues, warnings, security_issues),
            "recommendations": self._generate_quality_recommendations(issues, warnings)
        }

    def _calculate_quality_score(self, issues: List, warnings: List, security_issues: List) -> float:
        """Calculate overall quality score."""
        total_problems = len(issues) + len(warnings) + len(security_issues) * 2
        if total_problems == 0:
            return 1.0
        return max(0.0, 1.0 - (total_problems * 0.1))

    def _generate_quality_recommendations(self, issues: List, warnings: List) -> List[str]:
        """Generate recommendations based on quality issues."""
        recommendations = []

        if issues:
            recommendations.append("Address critical issues before deployment")
        if warnings:
            recommendations.append("Review warnings for potential improvements")
        if not issues and not warnings:
            recommendations.append("Code quality looks good - ready for testing")

        return recommendations

    # Additional helper methods for file generation and utilities

    async def _save_generated_files(self, project_id: str, files: Dict):
        """Save generated files to project directory."""
        project_dir = f"./data/projects/{project_id}/code"
        os.makedirs(project_dir, exist_ok=True)

        for filepath, content in files.items():
            full_path = os.path.join(project_dir, filepath)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

        self.logger.info(f"Saved {len(files)} files to {project_dir}")

    def _count_lines_of_code(self, files: Dict) -> int:
        """Count total lines of code across all files."""
        total_lines = 0
        for content in files.values():
            total_lines += len(content.split('\n'))
        return total_lines

    def _calculate_confidence(self, quality_report: Dict) -> float:
        """Calculate confidence score based on quality metrics."""
        return quality_report.get("quality_score", 0.5)

    def _create_implementation_notes(self, plan: Dict) -> List[str]:
        """Create implementation notes for the generated code."""
        return [
            "Generated code follows FastAPI and React best practices",
            "All files include basic error handling and logging",
            "Database schema created with appropriate indexes",
            "Frontend components use responsive design patterns",
            "Configuration files set up for Replit deployment"
        ]

    def _create_deployment_instructions(self, tech_stack: Dict) -> List[str]:
        """Create deployment instructions."""
        platform = tech_stack.get("deployment", "replit")

        if platform == "replit":
            return [
                "1. Import project to Replit",
                "2. Set environment variables in Secrets tab",
                "3. Run 'pip install -r requirements.txt'",
                "4. Run 'npm install' in frontend directory",
                "5. Click 'Run' button to start application",
                "6. Application will be available at generated URL"
            ]
        else:
            return [
                "1. Clone repository to deployment platform",
                "2. Configure environment variables",
                "3. Install dependencies",
                "4. Run database migrations",
                "5. Start application services"
            ]

    def _create_next_steps(self, quality_report: Dict) -> List[str]:
        """Create next steps based on quality report."""
        steps = []

        if quality_report.get("issues"):
            steps.append("Fix critical issues identified in quality report")

        steps.extend([
            "Run comprehensive testing with Tester agent",
            "Deploy to staging environment for validation",
            "Conduct user acceptance testing",
            "Deploy to production environment"
        ])

        return steps

    # Template and utility methods

    def _get_fastapi_templates(self) -> Dict:
        """Get FastAPI code templates."""
        return {
            "main": "FastAPI application template",
            "router": "API router template",
            "middleware": "Middleware template"
        }

    def _get_react_templates(self) -> Dict:
        """Get React code templates."""
        return {
            "component": "React component template",
            "hook": "Custom hook template",
            "context":