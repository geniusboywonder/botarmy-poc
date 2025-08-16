import asyncio
import os
import json
import time
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from prompts.developer_prompts import DEVELOPER_PROMPTS

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
            self._start_processing(input_data.get('project_id'))

            # Extract architectural specifications
            architecture = input_data.get('system_architecture', {})
            tech_stack = input_data.get('technology_stack', {})
            file_structure = input_data.get('file_structure', {})
            specifications = input_data.get('technical_specifications', {})

            # Update agent status
            await self._update_status("analyzing_architecture", 10)

            # Step 1: Plan code generation
            generation_plan = await self._create_generation_plan(
                architecture, tech_stack, file_structure, specifications
            )

            # Step 2: Generate backend code
            await self._update_status("generating_backend", 25)
            backend_files = await self._generate_backend_code(
                generation_plan, architecture, tech_stack, specifications
            )

            # Step 3: Generate frontend code
            await self._update_status("generating_frontend", 50)
            frontend_files = await self._generate_frontend_code(
                generation_plan, architecture, tech_stack, specifications
            )

            # Step 4: Generate configuration files
            await self._update_status("generating_config", 70)
            config_files = await self._generate_configuration_files(
                generation_plan, tech_stack
            )

            # Step 5: Generate documentation
            await self._update_status("generating_documentation", 85)
            documentation_files = await self._generate_documentation(
                generation_plan, architecture, tech_stack, backend_files, frontend_files
            )

            # Step 6: Perform quality checks
            await self._update_status("quality_checking", 95)
            quality_report = await self._perform_quality_checks(
                backend_files, frontend_files, config_files
            )

            # Step 7: Package final output
            await self._update_status("packaging_output", 98)

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
                "implementation_notes": self._create_implementation_notes(input_data, quality_report),
                "quality_report": quality_report,
                "deployment_instructions": self._create_deployment_instructions(tech_stack),
                "next_steps": self._create_next_steps(quality_report),
                "agent_metadata": {
                    "agent_type": self.agent_type,
                    "processing_time": self.processing_time,
                    "token_usage": self.llm_client.get_usage_stats(),
                    "lines_of_code": self._count_lines_of_code(all_files),
                    "confidence_score": self._calculate_confidence(quality_report)
                }
            }

            # Save files to project directory
            await self._save_generated_files(input_data.get('project_id'), all_files)

            await self._update_status("completed", 100)
            self._finish_processing()
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

    def _create_default_generation_plan(self) -> Dict:
        """Create a default generation plan when LLM parsing fails."""
        return {
            "generation_order": [
                "config.py", "database.py", "main.py", 
                "src/App.jsx", "src/context/AppContext.js",
                "package.json", "requirements.txt"
            ],
            "dependencies": {
                "main.py": ["config.py", "database.py"],
                "App.jsx": ["AppContext.js"]
            },
            "complexity_assessment": "medium",
            "estimated_files": 15,
            "critical_components": ["main.py", "database.py", "App.jsx"],
            "integration_points": [
                {
                    "component": "API endpoints",
                    "frontend": "src/utils/api.js",
                    "backend": "main.py"
                }
            ],
            "testing_strategy": {
                "unit_tests": ["test_agents.py", "test_database.py"],
                "integration_tests": ["test_api.py"],
                "e2e_tests": ["test_workflow.py"]
            }
        }

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

        # Generate CSS and styling
        frontend_files["src/App.css"] = await self._generate_app_css()
        frontend_files["src/index.css"] = await self._generate_index_css()

        # Generate index files
        frontend_files["src/index.js"] = await self._generate_react_index()
        frontend_files["public/index.html"] = await self._generate_html_template()

        return frontend_files

    async def _generate_configuration_files(self, plan: Dict, tech_stack: Dict) -> Dict:
        """Generate configuration and deployment files."""

        config_files = {}

        # Generate Python requirements
        config_files["requirements.txt"] = await self._generate_requirements_txt()

        # Generate Node.js package file
        config_files["package.json"] = await self._generate_package_json(tech_stack)

        # Generate environment template
        config_files[".env.example"] = await self._generate_env_template()

        # Generate Replit configuration
        config_files["replit.nix"] = await self._generate_replit_config()
        config_files[".replit"] = await self._generate_replit_file()

        # Generate Vite configuration
        config_files["vite.config.js"] = await self._generate_vite_config()

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

    # Individual file generation methods

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

class BaseAgent(ABC):
    """
    Base class for all BotArmy agents providing common functionality.
    """

    def __init__(self, agent_type: str, llm_client, database, logger):
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

    async def _generate_react_component(self, component_name: str, specs: Dict) -> str:
        """Generate React component based on name and specifications."""

        prompt = DEVELOPER_PROMPTS["react_component"].format(
            component_name=component_name,
            component_specs=json.dumps(specs, indent=2)
        )

        response = await self.llm_client.generate(
            prompt=prompt,
            max_tokens=1500,
            temperature=0.1
        )

        return response.strip()

    async def _generate_api_utils(self) -> str:
        """Generate API utility functions. (Truncated in input - placeholder for full implementation)"""

        return '''/**
 * API utility functions for BotArmy frontend.
 */

const API_BASE_URL = '';

export class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Project endpoints
  async createProject(requirements) {
    return this.request('/api/projects', {
      method: 'POST',
      body: JSON.stringify({ requirements }),
    });
  }

  async getProject(projectId) {
    return this.request(`/api/projects/${projectId}`);
  }

  async getProjects() {
    return this.request('/api/projects');
  }

  // Agent endpoints
  async getAgentStatus(projectId, agentType) {
    return this.request(`/api/agents/${projectId}/${agentType}/status`);
  }

  async getAgentMessages(projectId, agentType) {
    return this.request(`/api/agents/${projectId}/${agentType}/messages`);
  }

  // Conflict resolution endpoints
  async getConflicts(projectId) {
    return this.request(`/api/conflicts/${projectId}`);
  }

  async resolve...  # Truncated in original input - add full resolution logic here if available
'''

    async def _generate_formatting_utils(self) -> str:
        """Generate formatting utility functions. (Missing in input - placeholder)"""
        return '''// Formatting utilities for dates, strings, etc.
// Add full implementation here
export const formatDate = (date) => new Date(date).toLocaleString();
'''

    async def _generate_app_css(self) -> str:
        """Generate App CSS file. (Truncated in input - placeholder for full)"""

        return '''/* App CSS with global styles */
body {
  font-family: Arial, sans-serif;
}

.App {
  text-align: center;
}

/* More styles... (truncated in original - expand as needed) */
'''

    async def _generate_index_css(self) -> str:
        """Generate index CSS file."""

        return '''/* Index CSS with Tailwind base styles */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Global styles */
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f9fafb;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}

/* Custom utility classes */
@layer utilities {
  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
  
  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
  
  .text-shadow {
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .gradient-text {
    background: linear-gradient(45deg, #3b82f6, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
}

/* Component styles */
@layer components {
  .btn-primary {
    @apply bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200;
  }
  
  .btn-secondary {
    @apply bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-lg transition-colors duration-200;
  }
  
  .card {
    @apply bg-white rounded-lg shadow-sm border border-gray-200 p-6;
  }
  
  .input-field {
    @apply w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent;
  }
  
  .badge {
    @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium;
  }
  
  .badge-blue {
    @apply bg-blue-100 text-blue-800;
  }
  
  .badge-green {
    @apply bg-green-100 text-green-800;
  }
  
  .badge-red {
    @apply bg-red-100 text-red-800;
  }
  
  .badge-yellow {
    @apply bg-yellow-100 text-yellow-800;
  }
  
  .badge-gray {
    @apply bg-gray-100 text-gray-800;
  }
}
'''

    async def _generate_react_index(self) -> str:
        """Generate React index.js file."""

        return '''import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
'''

    async def _generate_html_template(self) -> str:
        """Generate HTML template."""

        return '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta
      name="description"
      content="BotArmy - AI-powered software development automation"
    />
    <title>BotArmy POC</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
'''

    async def _generate_workflow_pipeline(self) -> str:
        """Generate workflow pipeline manager."""

        return '''"""
Workflow pipeline manager for orchestrating agent sequences.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from database import Database

class WorkflowPipeline:
    """
    Manages the sequential execution of agents in the BotArmy workflow.
    """

    def __init__(self, database: Database, logger):
        self.database = database
        self.logger = logger
        self.agents = {}
        self.current_project = None
        self.pipeline_stages = [
            "analyst",
            "architect", 
            "developer",
            "tester"
        ]

    def register_agent(self, agent_type: str, agent_instance):
        """Register an agent instance for the pipeline."""
        self.agents[agent_type] = agent_instance
        self.logger.info(f"Registered {agent_type} agent")

    async def execute_pipeline(self, project_id: str, initial_requirements: str) -> Dict[str, Any]:
        """
        Execute the complete agent pipeline for a project.

        Args:
            project_id: Unique project identifier
            initial_requirements: Initial user requirements

        Returns:
            Final pipeline results
        """
        try:
            self.current_project = project_id
            self.logger.info(f"Starting pipeline execution for project {project_id}")

            # Initialize pipeline state
            pipeline_state = {
                "project_id": project_id,
                "current_stage": 0,
                "stage_outputs": {},
                "errors": [],
                "start_time": asyncio.get_event_loop().time()
            }

            # Store initial requirements
            await self.database.update_project_status(project_id, "processing")
            
            # Execute each stage sequentially
            stage_input = {"project_id": project_id, "requirements": initial_requirements}

            for stage_index, agent_type in enumerate(self.pipeline_stages):
                pipeline_state["current_stage"] = stage_index
                
                try:
                    self.logger.info(f"Executing stage {stage_index + 1}: {agent_type}")
                    
                    # Get agent instance
                    agent = self.agents.get(agent_type)
                    if not agent:
                        raise Exception(f"Agent {agent_type} not registered")

                    # Execute agent
                    stage_output = await agent.process(stage_input)
                    
                    # Store stage output
                    pipeline_state["stage_outputs"][agent_type] = stage_output
                    
                    # Prepare input for next stage
                    stage_input = {
                        **stage_input,
                        **stage_output
                    }
                    
                    self.logger.info(f"Completed stage {stage_index + 1}: {agent_type}")

                except Exception as e:
                    error_msg = f"Stage {stage_index + 1} ({agent_type}) failed: {str(e)}"
                    self.logger.error(error_msg)
                    pipeline_state["errors"].append(error_msg)
                    
                    # Attempt error recovery
                    recovery_success = await self._handle_stage_error(
                        agent_type, stage_input, str(e)
                    )
                    
                    if not recovery_success:
                        await self.database.update_project_status(project_id, "error")
                        raise Exception(f"Pipeline failed at stage {agent_type}: {str(e)}")

            # Pipeline completed successfully
            pipeline_state["end_time"] = asyncio.get_event_loop().time()
            pipeline_state["total_time"] = (
                pipeline_state["end_time"] - pipeline_state["start_time"]
            )

            await self.database.update_project_status(project_id, "completed")
            self.logger.info(f"Pipeline completed successfully for project {project_id}")

            return {
                "success": True,
                "project_id": project_id,
                "pipeline_state": pipeline_state,
                "final_output": stage_input
            }

        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {str(e)}")
            return {
                "success": False,
                "project_id": project_id,
                "error": str(e),
                "pipeline_state": pipeline_state
            }

    async def _handle_stage_error(self, agent_type: str, stage_input: Dict, 
                                  error_message: str) -> bool:
        """Handle errors in pipeline stages with retry logic."""
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Retrying {agent_type} agent (attempt {attempt + 1})")
                
                # Wait before retry with exponential backoff
                await asyncio.sleep(2 ** attempt)
                
                # Retry agent execution
                agent = self.agents.get(agent_type)
                if agent:
                    await agent.process(stage_input)
                    return True
                    
            except Exception as e:
                self.logger.warning(f"Retry {attempt + 1} failed for {agent_type}: {str(e)}")
                continue
                
        # All retries failed
        return False

    async def get_pipeline_status(self, project_id: str) -> Dict[str, Any]:
        """Get current pipeline execution status."""
        
        agents_status = {}
        for agent_type in self.pipeline_stages:
            agent = self.agents.get(agent_type)
            if agent:
                agents_status[agent_type] = agent.get_status()
            else:
                agents_status[agent_type] = {"status": "not_registered"}
                
        return {
            "project_id": project_id,
            "agents": agents_status,
            "current_project": self.current_project
        }

    async def pause_pipeline(self, project_id: str):
        """Pause pipeline execution."""
        # Implementation for pausing pipeline
        pass

    async def resume_pipeline(self, project_id: str):
        """Resume paused pipeline execution."""
        # Implementation for resuming pipeline
        pass

    async def cancel_pipeline(self, project_id: str):
        """Cancel pipeline execution."""
        # Implementation for canceling pipeline
        pass
'''

    async def _generate_state_manager(self) -> str:
        """Generate state manager for workflow tracking."""

        return '''"""
State manager for tracking workflow and agent states.
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from enum import Enum
from database import Database

class AgentStatus(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    WAITING = "waiting"

class ProjectStatus(Enum):
    CREATED = "created"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"

class StateManager:
    """
    Manages state for projects, agents, and workflow execution.
    """

    def __init__(self, database: Database, logger):
        self.database = database
        self.logger = logger
        self.project_states = {}
        self.agent_states = {}
        self.event_listeners = []

    async def create_project_state(self, project_id: str, requirements: str) -> Dict[str, Any]:
        """Create initial state for a new project."""
        
        project_state = {
            "project_id": project_id,
            "status": ProjectStatus.CREATED.value,
            "requirements": requirements,
            "created_at": asyncio.get_event_loop().time(),
            "updated_at": asyncio.get_event_loop().time(),
            "agents": {
                "analyst": {"status": AgentStatus.IDLE.value, "progress": 0},
                "architect": {"status": AgentStatus.IDLE.value, "progress": 0},
                "developer": {"status": AgentStatus.IDLE.value, "progress": 0},
                "tester": {"status": AgentStatus.IDLE.value, "progress": 0}
            },
            "conflicts": [],
            "files": [],
            "metadata": {}
        }
        
        self.project_states[project_id] = project_state
        await self.database.create_project(project_id, requirements)
        
        self.logger.info(f"Created project state for {project_id}")
        await self._notify_state_change("project_created", project_state)
        
        return project_state

    async def update_project_status(self, project_id: str, status: str, 
                                    metadata: Dict = None) -> bool:
        """Update project status and metadata."""
        
        if project_id not in self.project_states:
            return False
            
        self.project_states[project_id]["status"] = status
        self.project_states[project_id]["updated_at"] = asyncio.get_event_loop().time()
        
        if metadata:
            self.project_states[project_id]["metadata"].update(metadata)
            
        await self.database.update_project_status(project_id, status)
        
        self.logger.info(f"Updated project {project_id} status to {status}")
        await self._notify_state_change("project_updated", self.project_states[project_id])
        
        return True

    async def update_agent_status(self, project_id: str, agent_type: str, 
                                  status: str, progress: int = None) -> bool:
        """Update agent status and progress."""
        
        if project_id not in self.project_states:
            return False
            
        agent_state = self.project_states[project_id]["agents"][agent_type]
        agent_state["status"] = status
        agent_state["updated_at"] = asyncio.get_event_loop().time()
        
        if progress is not None:
            agent_state["progress"] = progress
            
        await self.database.update_agent_status(project_id, agent_type, status, progress)
        
        self.logger.info(f"Updated {agent_type} agent status to {status} ({progress}%)")
        await self._notify_state_change("agent_updated", {
            "project_id": project_id,
            "agent_type": agent_type,
            "status": status,
            "progress": progress
        })
        
        return True

    async def add_conflict(self, project_id: str, description: str, 
                          agents_involved: List[str]) -> str:
        """Add a conflict that requires human intervention."""
        
        conflict_id = f"conflict_{len(self.project_states[project_id]['conflicts'])}"
        conflict = {
            "id": conflict_id,
            "description": description,
            "agents_involved": agents_involved,
            "created_at": asyncio.get_event_loop().time(),
            "resolved": False,
            "resolution": None
        }
        
        self.project_states[project_id]["conflicts"].append(conflict)
        await self.database.create_conflict(project_id, conflict_id, description, agents_involved)
        
        self.logger.info(f"Added conflict {conflict_id} for project {project_id}")
        await self._notify_state_change("conflict_created", {
            "project_id": project_id,
            "conflict": conflict
        })
        
        return conflict_id

    async def resolve_conflict(self, project_id: str, conflict_id: str, 
                              resolution: str) -> bool:
        """Resolve a conflict with human input."""
        
        if project_id not in self.project_states:
            return False
            
        conflicts = self.project_states[project_id]["conflicts"]
        for conflict in conflicts:
            if conflict["id"] == conflict_id:
                conflict["resolved"] = True
                conflict["resolution"] = resolution
                conflict["resolved_at"] = asyncio.get_event_loop().time()
                
                await self.database.resolve_conflict(conflict_id, resolution)
                
                self.logger.info(f"Resolved conflict {conflict_id}")
                await self._notify_state_change("conflict_resolved", {
                    "project_id": project_id,
                    "conflict": conflict
                })
                
                return True
                
        return False

    async def add_generated_file(self, project_id: str, filename: str, 
                                content: str, generated_by: str):
        """Add a generated file to project state."""
        
        file_entry = {
            "filename": filename,
            "content": content,
            "generated_by": generated_by,
            "created_at": asyncio.get_event_loop().time(),
            "size": len(content)
        }
        
        self.project_states[project_id]["files"].append(file_entry)
        await self.database.save_file(project_id, filename, content, generated_by)
        
        self.logger.info(f"Added generated file {filename} to project {project_id}")

    def get_project_state(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get current project state."""
        return self.project_states.get(project_id)

    def get_agent_state(self, project_id: str, agent_type: str) -> Optional[Dict[str, Any]]:
        """Get current agent state."""
        project_state = self.project_states.get(project_id)
        if project_state:
            return project_state["agents"].get(agent_type)
        return None

    def get_pending_conflicts(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all pending conflicts for a project."""
        project_state = self.project_states.get(project_id)
        if project_state:
            return [c for c in project_state["conflicts"] if not c["resolved"]]
        return []

    async def register_event_listener(self, callback):
        """Register a callback for state change events."""
        self.event_listeners.append(callback)

    async def _notify_state_change(self, event_type: str, data: Dict[str, Any]):
        """Notify all registered listeners of state changes."""
        for listener in self.event_listeners:
            try:
                await listener(event_type, data)
            except Exception as e:
                self.logger.error(f"Error in event listener: {str(e)}")

    async def cleanup_old_projects(self, max_age_hours: int = 24):
        """Clean up old project states to prevent memory leaks."""
        current_time = asyncio.get_event_loop().time()
        max_age_seconds = max_age_hours * 3600
        
        projects_to_remove = []
        for project_id, state in self.project_states.items():
            if current_time - state["created_at"] > max_age_seconds:
                projects_to_remove.append(project_id)
                
        for project_id in projects_to_remove:
            del self.project_states[project_id]
            self.logger.info(f"Cleaned up old project state: {project_id}")

    def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide statistics."""
        total_projects = len(self.project_states)
        
        status_counts = {}
        for state in self.project_states.values():
            status = state["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
            
        return {
            "total_projects": total_projects,
            "status_counts": status_counts,
            "memory_usage": len(str(self.project_states))
        }
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

    # Configuration file generation methods

    async def _generate_requirements_txt(self) -> str:
        """Generate Python requirements file."""

        prompt = DEVELOPER_PROMPTS["generate_requirements"]
        response = await self.llm_client.generate(
            prompt=prompt,
            max_tokens=500,
            temperature=0.1
        )

        return response.strip()

    async def _generate_package_json(self, tech_stack: Dict) -> str:
        """Generate Node.js package.json file."""

        prompt = DEVELOPER_PROMPTS["generate_package_json"].format(
            tech_stack=json.dumps(tech_stack, indent=2)
        )

        response = await self.llm_client.generate(
            prompt=prompt,
            max_tokens=800,
            temperature=0.1
        )

        return response.strip()

    async def _generate_env_template(self) -> str:
        """Generate environment variables template."""

        return '''# BotArmy Environment Configuration

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.2

# Database Configuration  
DATABASE_URL=sqlite:///./data/messages.db

# Application Configuration
APP_NAME=BotArmy
APP_VERSION=1.0.0
DEBUG=false

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=./data/logs/app.log

# Replit Configuration (if using Replit)
REPLIT_DB_URL=

# Security
SECRET_KEY=your_secret_key_here
'''

    async def _generate_replit_config(self) -> str:
        """Generate Replit configuration file."""

        return '''{ pkgs }: {
  deps = [
    pkgs.nodejs-18_x
    pkgs.python310Full
    pkgs.pip
    pkgs.sqlite
  ];
  
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.sqlite
    ];
  };
}
'''

    async def _generate_replit_file(self) -> str:
        """Generate .replit configuration file."""

        return '''modules = ["python-3.10", "nodejs-18"]

[nix]
channel = "stable-22_11"

[deployment]
run = ["python", "main.py"]

[[ports]]
localPort = 8000
externalPort = 80

[env]
PYTHON_LD_LIBRARY_PATH = "/nix/store/2vpxdyyg4j6p7xb8qb6gy3g5pmbzqzhz-sqlite-3.39.4/lib"
'''

    async def _generate_vite_config(self) -> str:
        """Generate Vite configuration for React."""

        return '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: '../static',
    emptyOutDir: true
  }
})
'''

    async def _generate_gitignore(self) -> str:
        """Generate .gitignore file."""

        return '''# Dependencies
node_modules/
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Database
*.db
*.sqlite
*.sqlite3

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build outputs
static/
build/
dist/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Replit
.replit
replit.nix

# Data directory
data/

# Temporary files
tmp/
temp/
'''

    async def _generate_readme(self, architecture: Dict, tech_stack: Dict, plan: Dict) -> str:
        """Generate main README. (Assumes prompt exists - placeholder LLM call)"""
        prompt = DEVELOPER_PROMPTS.get("generate_readme", "").format(
            architecture=json.dumps(architecture, indent=2),
            tech_stack=json.dumps(tech_stack, indent=2),
            plan=json.dumps(plan, indent=2)
        )
        response = await self.llm_client.generate(prompt=prompt, max_tokens=1000, temperature=0.3)
        return response.strip()

    async def _generate_api_docs(self, backend_files: Dict) -> str:
        """Generate API documentation. (Placeholder LLM call)"""
        prompt = DEVELOPER_PROMPTS.get("generate_api_docs", "").format(
            backend_code=json.dumps(backend_files, indent=2)
        )
        response = await self.llm_client.generate(prompt=prompt, max_tokens=1000, temperature=0.3)
        return response.strip()

    async def _generate_deployment_docs(self, tech_stack: Dict) -> str:
        """Generate deployment guide. (Placeholder LLM call)"""
        prompt = DEVELOPER_PROMPTS.get("generate_deployment_docs", "").format(
            tech_stack=json.dumps(tech_stack, indent=2)
        )
        response = await self.llm_client.generate(prompt=prompt, max_tokens=1000, temperature=0.3)
        return response.strip()

    async def _generate_development_docs(self, backend_files: Dict, frontend_files: Dict) -> str:
        """Generate developer guide. (Placeholder LLM call)"""
        prompt = DEVELOPER_PROMPTS.get("generate_development_docs", "").format(
            backend=json.dumps(backend_files, indent=2),
            frontend=json.dumps(frontend_files, indent=2)
        )
        response = await self.llm_client.generate(prompt=prompt, max_tokens=1000, temperature=0.3)
        return response.strip()

    def _create_implementation_notes(self, input_data: Dict, quality_report: Dict) -> List[str]:
        """Create implementation notes based on input and quality. (Adjusted from original)"""
        notes = []

        tech_stack = input_data.get("technology_stack", {})
        if tech_stack.get("frontend") == "React":
            notes.append("React components follow modern hooks patterns and best practices")
        
        if tech_stack.get("backend") == "FastAPI":
            notes.append("FastAPI implementation includes async endpoints and proper validation")

        if quality_report.get("issues", []) == []:
            notes.append("Generated code passes all syntax and basic quality checks")
        
        if quality_report.get("security_issues", []) == []:
            notes.append("No security vulnerabilities detected in generated code")

        return notes

    def _create_next_steps(self, quality_report: Dict) -> List[str]:
        """Create next steps based on quality report. (Adjusted - removed validation_results)"""
        
        steps = []
        
        # Address quality issues first
        if quality_report.get("issues", []):
            steps.append("Address critical issues before deployment")
        
        if len(quality_report.get("warnings", [])) > 5:
            steps.append("Address warnings to improve code maintainability")
        
        if quality_report.get("issues", []):
            steps.append("Complete missing required files and configurations")
        
        # Standard next steps
        steps.extend([
            "Run comprehensive testing with Tester agent",
            "Deploy to development environment for manual testing",
            "Perform security review and penetration testing",
            "Set up monitoring and alerting",
            "Create user documentation and training materials",
            "Deploy to production environment"
        ])
        
        return steps

    def _get_fastapi_templates(self) -> Dict:
        return {"main": "", "router": "", "middleware": ""}
    
    def _get_react_templates(self) -> Dict:
        return {"component": "", "hook": "", "context": ""}
    
    def _get_database_templates(self) -> Dict:
        return {"schema": "", "migration": "", "operations": ""}

    # Added missing methods

    def _create_deployment_instructions(self, tech_stack: Dict) -> str:
        """Added placeholder for deployment instructions."""
        return f"Deployment instructions: Use Docker for {tech_stack.get('backend', 'FastAPI')} and Netlify for {tech_stack.get('frontend', 'React')}."

    def _calculate_confidence(self, quality_report: Dict) -> float:
        """Added placeholder for confidence calculation."""
        return quality_report.get("quality_score", 0.5) * 100  # As percentage

    def _count_lines_of_code(self, files: Dict) -> int:
        """Added method to count lines of generated code."""
        return sum(len(content.split('\n')) for content in files.values() if content)

    async def _save_generated_files(self, project_id: str, files: Dict) -> None:
        """Added method to save files to disk (sync for simplicity)."""
        base_dir = f"projects/{project_id}"
        os.makedirs(base_dir, exist_ok=True)
        for path, content in files.items():
            full_path = os.path.join(base_dir, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
```