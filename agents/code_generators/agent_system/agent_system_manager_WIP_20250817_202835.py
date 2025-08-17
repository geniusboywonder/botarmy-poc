"""
Agent System Manager - Modular agent orchestration and management.
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Type
from datetime import datetime
from abc import ABC, abstractmethod

from ..base.base_manager import BaseManager
from ..base.base_generator import BaseGenerator


class BaseAgentGenerator(BaseGenerator):
    """Base class for agent code generators."""
    
    def __init__(self, manager: 'AgentSystemManager'):
        super().__init__()
        self.manager = manager
    
    def get_fallback_template(self) -> str:
        """Get basic agent template for fallbacks."""
        return '''"""
Basic agent implementation with error handling.
"""

import asyncio
from typing import Dict, Any

class Agent:
    """Base agent with minimal functionality."""
    
    def __init__(self, llm_client, logger):
        self.llm_client = llm_client
        self.logger = logger
        self.agent_type = "base"
        self.status = "ready"
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results."""
        try:
            self.logger.info(f"Processing with {self.agent_type} agent")
            # Basic processing logic
            return {
                "agent_type": self.agent_type,
                "status": "completed",
                "result": "Basic processing completed",
                "timestamp": asyncio.get_event_loop().time()
            }
        except Exception as e:
            self.logger.error(f"Agent processing failed: {str(e)}")
            return {
                "agent_type": self.agent_type,
                "status": "error",
                "error": str(e)
            }
'''


class BaseAgentClassGenerator(BaseAgentGenerator):
    """Generates the base agent class."""
    
    async def generate(self, specifications: Dict[str, Any]) -> str:
        """Generate base agent class."""
        try:
            return self._generate_base_agent_class()
        except Exception as e:
            self.manager.logger.error(f"Base agent generation failed: {e}")
            return self.get_fallback_template()
    
    def _generate_base_agent_class(self) -> str:
        """Generate comprehensive base agent class."""
        return '''"""
Base agent class with common functionality for all BotArmy agents.
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from enum import Enum

class AgentStatus(Enum):
    """Agent status enumeration."""
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    WAITING = "waiting"

class BaseAgent(ABC):
    """
    Abstract base class for all BotArmy agents.
    Provides common functionality and enforces interface contracts.
    """
    
    def __init__(self, llm_client, database, logger, agent_type: str):
        self.llm_client = llm_client
        self.database = database
        self.logger = logger
        self.agent_type = agent_type
        self.status = AgentStatus.IDLE
        
        # Tracking metrics
        self.total_requests = 0
        self.total_tokens = 0
        self.total_processing_time = 0.0
        self.error_count = 0
        
        # Current processing context
        self.current_project_id = None
        self.current_request_id = None
        self.processing_start_time = None
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return structured results.
        Must be implemented by all concrete agents.
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data format and requirements.
        Must be implemented by all concrete agents.
        """
        pass
    
    @abstractmethod
    def validate_output(self, output_data: Dict[str, Any]) -> bool:
        """
        Validate output data format and completeness.
        Must be implemented by all concrete agents.
        """
        pass
    
    async def execute_with_tracking(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent processing with comprehensive tracking."""
        
        # Validate input
        if not self.validate_input(input_data):
            raise ValueError(f"Invalid input data for {self.agent_type} agent")
        
        # Setup tracking
        self.status = AgentStatus.PROCESSING
        self.processing_start_time = time.time()
        self.current_project_id = input_data.get('project_id')
        self.current_request_id = f"{self.agent_type}_{int(time.time())}"
        
        try:
            self.logger.info(f"Starting {self.agent_type} agent processing")
            
            # Execute main processing
            result = await self.process(input_data)
            
            # Validate output
            if not self.validate_output(result):
                raise ValueError(f"Invalid output from {self.agent_type} agent")
            
            # Update success metrics
            processing_time = time.time() - self.processing_start_time
            self.total_processing_time += processing_time
            self.total_requests += 1
            self.status = AgentStatus.COMPLETED
            
            # Add metadata to result
            result['_metadata'] = {
                'agent_type': self.agent_type,
                'processing_time': processing_time,
                'request_id': self.current_request_id,
                'timestamp': time.time()
            }
            
            self.logger.info(f"Completed {self.agent_type} processing in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            # Handle errors
            self.error_count += 1
            self.status = AgentStatus.ERROR
            error_msg = f"{self.agent_type} agent failed: {str(e)}"
            
            self.logger.error(error_msg)
            
            # Log error to database if available
            if self.database and self.current_project_id:
                await self.database.log_agent_error(
                    project_id=self.current_project_id,
                    agent_type=self.agent_type,
                    error_message=str(e),
                    request_id=self.current_request_id
                )
            
            return {
                'status': 'error',
                'error': error_msg,
                'agent_type': self.agent_type,
                'request_id': self.current_request_id,
                'timestamp': time.time()
            }
        
        finally:
            # Cleanup
            self.processing_start_time = None
            self.current_project_id = None
            self.current_request_id = None
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics."""
        return {
            'agent_type': self.agent_type,
            'status': self.status.value,
            'metrics': {
                'total_requests': self.total_requests,
                'total_tokens': self.total_tokens,
                'total_processing_time': self.total_processing_time,
                'error_count': self.error_count,
                'average_processing_time': (
                    self.total_processing_time / self.total_requests 
                    if self.total_requests > 0 else 0
                ),
                'error_rate': (
                    self.error_count / self.total_requests 
                    if self.total_requests > 0 else 0
                )
            },
            'current_processing': {
                'project_id': self.current_project_id,
                'request_id': self.current_request_id,
                'processing_duration': (
                    time.time() - self.processing_start_time 
                    if self.processing_start_time else 0
                )
            }
        }
    
    def reset_metrics(self):
        """Reset agent metrics."""
        self.total_requests = 0
        self.total_tokens = 0
        self.total_processing_time = 0.0
        self.error_count = 0
        self.logger.info(f"Reset metrics for {self.agent_type} agent")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform agent health check."""
        return {
            'agent_type': self.agent_type,
            'healthy': self.status != AgentStatus.ERROR,
            'status': self.status.value,
            'llm_client_connected': self.llm_client is not None,
            'database_connected': self.database is not None,
            'uptime_requests': self.total_requests
        }
'''


class AgentRegistryGenerator(BaseAgentGenerator):
    """Generates agent registry for managing multiple agents."""
    
    async def generate(self, specifications: Dict[str, Any]) -> str:
        """Generate agent registry."""
        try:
            return self._generate_agent_registry()
        except Exception as e:
            self.manager.logger.error(f"Agent registry generation failed: {e}")
            return self._get_fallback_registry()
    
    def _generate_agent_registry(self) -> str:
        """Generate comprehensive agent registry."""
        return '''"""
Agent registry for managing and coordinating multiple agents.
"""

import asyncio
from typing import Dict, Any, Optional, List, Type
from .base_agent import BaseAgent, AgentStatus

class AgentRegistry:
    """
    Central registry for managing multiple agents and their lifecycles.
    """
    
    def __init__(self, database, logger):
        self.database = database
        self.logger = logger
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_configs: Dict[str, Dict] = {}
        self.startup_order = ["analyst", "architect", "developer", "tester"]
    
    def register_agent(self, agent_type: str, agent_instance: BaseAgent, 
                      config: Optional[Dict] = None):
        """Register a new agent with the registry."""
        
        if not isinstance(agent_instance, BaseAgent):
            raise ValueError(f"Agent must inherit from BaseAgent: {agent_type}")
        
        self.agents[agent_type] = agent_instance
        self.agent_configs[agent_type] = config or {}
        
        self.logger.info(f"Registered {agent_type} agent")
    
    def unregister_agent(self, agent_type: str):
        """Remove agent from registry."""
        
        if agent_type in self.agents:
            del self.agents[agent_type]
            del self.agent_configs[agent_type]
            self.logger.info(f"Unregistered {agent_type} agent")
    
    def get_agent(self, agent_type: str) -> Optional[BaseAgent]:
        """Get agent instance by type."""
        return self.agents.get(agent_type)
    
    def list_agents(self) -> List[str]:
        """List all registered agent types."""
        return list(self.agents.keys())
    
    async def get_all_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status for all registered agents."""
        
        status_data = {}
        for agent_type, agent in self.agents.items():
            try:
                status_data[agent_type] = await agent.get_status()
            except Exception as e:
                status_data[agent_type] = {
                    'agent_type': agent_type,
                    'status': 'error',
                    'error': f'Status check failed: {str(e)}'
                }
        
        return status_data
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Perform health check on all agents."""
        
        health_data = {
            'overall_healthy': True,
            'agents': {},
            'timestamp': asyncio.get_event_loop().time()
        }
        
        for agent_type, agent in self.agents.items():
            try:
                agent_health = await agent.health_check()
                health_data['agents'][agent_type] = agent_health
                
                if not agent_health.get('healthy', False):
                    health_data['overall_healthy'] = False
                    
            except Exception as e:
                health_data['agents'][agent_type] = {
                    'agent_type': agent_type,
                    'healthy': False,
                    'error': f'Health check failed: {str(e)}'
                }
                health_data['overall_healthy'] = False
        
        return health_data
    
    async def restart_agent(self, agent_type: str) -> Dict[str, Any]:
        """Restart a specific agent."""
        
        if agent_type not in self.agents:
            return {'success': False, 'error': f'Agent {agent_type} not found'}
        
        try:
            agent = self.agents[agent_type]
            
            # Reset metrics and status
            agent.reset_metrics()
            agent.status = AgentStatus.IDLE
            
            self.logger.info(f"Restarted {agent_type} agent")
            
            return {'success': True, 'agent_type': agent_type}
            
        except Exception as e:
            error_msg = f"Failed to restart {agent_type} agent: {str(e)}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
    
    async def shutdown_all(self):
        """Shutdown all agents gracefully."""
        
        self.logger.info("Shutting down all agents...")
        
        for agent_type, agent in self.agents.items():
            try:
                # Wait for any current processing to complete
                if agent.status == AgentStatus.PROCESSING:
                    self.logger.info(f"Waiting for {agent_type} to complete processing...")
                    
                    # Wait up to 30 seconds for completion
                    timeout = 30
                    while agent.status == AgentStatus.PROCESSING and timeout > 0:
                        await asyncio.sleep(1)
                        timeout -= 1
                
                agent.status = AgentStatus.IDLE
                self.logger.info(f"Shutdown {agent_type} agent")
                
            except Exception as e:
                self.logger.error(f"Error shutting down {agent_type}: {str(e)}")
        
        self.logger.info("All agents shutdown complete")
    
    def get_agent_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get performance metrics for all agents."""
        
        metrics = {}
        for agent_type, agent in self.agents.items():
            try:
                status = asyncio.create_task(agent.get_status())
                # Note: This is synchronous, so we get basic metrics only
                metrics[agent_type] = {
                    'total_requests': agent.total_requests,
                    'error_count': agent.error_count,
                    'current_status': agent.status.value
                }
            except Exception as e:
                metrics[agent_type] = {'error': str(e)}
        
        return metrics
'''
    
    def _get_fallback_registry(self) -> str:
        """Get fallback agent registry."""
        return '''"""
Fallback agent registry with basic functionality.
"""

from typing import Dict, Any, Optional

class AgentRegistry:
    def __init__(self, database, logger):
        self.database = database
        self.logger = logger
        self.agents = {}
    
    def register_agent(self, agent_type: str, agent_instance, config=None):
        self.agents[agent_type] = agent_instance
        self.logger.info(f"Registered {agent_type} agent")
    
    def get_agent(self, agent_type: str):
        return self.agents.get(agent_type)
    
    def list_agents(self):
        return list(self.agents.keys())
'''


class AgentManagerGenerator(BaseAgentGenerator):
    """Generates agent manager for orchestration."""
    
    async def generate(self, specifications: Dict[str, Any]) -> str:
        """Generate agent manager."""
        try:
            return self._generate_agent_manager()
        except Exception as e:
            self.manager.logger.error(f"Agent manager generation failed: {e}")
            return self._get_fallback_manager()
    
    def _generate_agent_manager(self) -> str:
        """Generate comprehensive agent manager."""
        return '''"""
Agent manager for orchestrating workflow between multiple agents.
"""

import asyncio
from typing import Dict, Any, List, Optional
from enum import Enum
from .agent_registry import AgentRegistry
from .base_agent import BaseAgent, AgentStatus

class WorkflowStage(Enum):
    """Workflow execution stages."""
    IDLE = "idle"
    ANALYZING = "analyzing"
    ARCHITECTING = "architecting" 
    DEVELOPING = "developing"
    TESTING = "testing"
    COMPLETED = "completed"
    ERROR = "error"
    WAITING_APPROVAL = "waiting_approval"

class AgentManager:
    """
    Orchestrates multiple agents in a sequential workflow pipeline.
    """
    
    def __init__(self, database, logger):
        self.database = database
        self.logger = logger
        self.registry = AgentRegistry(database, logger)
        
        # Workflow state
        self.current_stage = WorkflowStage.IDLE
        self.current_project_id = None
        self.workflow_data = {}
        self.stage_results = {}
        
        # Pipeline configuration
        self.pipeline_stages = [
            ("analyst", WorkflowStage.ANALYZING),
            ("architect", WorkflowStage.ARCHITECTING),
            ("developer", WorkflowStage.DEVELOPING),
            ("tester", WorkflowStage.TESTING)
        ]
        
        self.timeout_seconds = 300  # 5 minutes per agent
        self.max_retries = 3
    
    def register_agent(self, agent_type: str, agent_instance: BaseAgent, 
                      config: Optional[Dict] = None):
        """Register agent with the manager."""
        self.registry.register_agent(agent_type, agent_instance, config)
    
    async def process_project(self, project_id: str, requirements: str) -> Dict[str, Any]:
        """
        Process a complete project through the agent pipeline.
        
        Args:
            project_id: Unique project identifier
            requirements: Initial project requirements
            
        Returns:
            Complete workflow results with all stage outputs
        """
        
        self.current_project_id = project_id
        self.current_stage = WorkflowStage.IDLE
        self.workflow_data = {
            'project_id': project_id,
            'requirements': requirements,
            'start_time': asyncio.get_event_loop().time(),
            'stages_completed': [],
            'errors': []
        }
        self.stage_results = {}
        
        self.logger.info(f"Starting project workflow for {project_id}")
        
        try:
            # Process through each pipeline stage
            current_input = {'project_id': project_id, 'requirements': requirements}
            
            for agent_type, stage in self.pipeline_stages:
                self.current_stage = stage
                
                # Update project status in database
                await self.database.update_project_stage(
                    project_id=project_id,
                    stage=stage.value
                )
                
                # Process stage
                stage_result = await self._process_stage(
                    agent_type, stage, current_input
                )
                
                # Store results and prepare for next stage
                self.stage_results[agent_type] = stage_result
                self.workflow_data['stages_completed'].append(agent_type)
                current_input = stage_result
            
            # Mark as completed
            self.current_stage = WorkflowStage.COMPLETED
            await self.database.update_project_stage(
                project_id=project_id,
                stage=WorkflowStage.COMPLETED.value
            )
            
            total_time = asyncio.get_event_loop().time() - self.workflow_data['start_time']
            
            self.logger.info(f"Project {project_id} completed in {total_time:.2f}s")
            
            return {
                'project_id': project_id,
                'status': 'completed',
                'total_processing_time': total_time,
                'stages_completed': self.workflow_data['stages_completed'],
                'results': self.stage_results
            }
        
        except Exception as e:
            # Handle pipeline failure
            self.current_stage = WorkflowStage.ERROR
            error_msg = f"Pipeline failed at stage {self.current_stage.value}: {str(e)}"
            
            self.logger.error(error_msg)
            self.workflow_data['errors'].append(error_msg)
            
            await self.database.update_project_stage(
                project_id=project_id,
                stage=WorkflowStage.ERROR.value
            )
            
            return {
                'project_id': project_id,
                'status': 'error',
                'error': error_msg,
                'stages_completed': self.workflow_data['stages_completed'],
                'partial_results': self.stage_results
            }
    
    async def _process_stage(self, agent_type: str, stage: WorkflowStage, 
                           input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single workflow stage with an agent."""
        
        agent = self.registry.get_agent(agent_type)
        if not agent:
            raise ValueError(f"Agent {agent_type} not registered")
        
        self.logger.info(f"Processing stage {stage.value} with {agent_type} agent")
        
        # Add stage context to input
        stage_input = {
            **input_data,
            'stage': stage.value,
            'previous_results': self.stage_results
        }
        
        # Process with timeout and retries
        for attempt in range(self.max_retries):
            try:
                # Execute with timeout
                result = await asyncio.wait_for(
                    agent.execute_with_tracking(stage_input),
                    timeout=self.timeout_seconds
                )
                
                # Check for conflicts or issues requiring human intervention
                if result.get('requires_human_approval'):
                    await self._handle_human_intervention(agent_type, stage, result)
                
                return result
                
            except asyncio.TimeoutError:
                error_msg = f"Stage {stage.value} timeout after {self.timeout_seconds}s"
                self.logger.warning(f"{error_msg}, attempt {attempt + 1}/{self.max_retries}")
                
                if attempt == self.max_retries - 1:
                    raise TimeoutError(error_msg)
                
                # Wait before retry
                await asyncio.sleep(2 ** attempt)
                
            except Exception as e:
                error_msg = f"Stage {stage.value} failed: {str(e)}"
                self.logger.warning(f"{error_msg}, attempt {attempt + 1}/{self.max_retries}")
                
                if attempt == self.max_retries - 1:
                    raise
                
                # Wait before retry
                await asyncio.sleep(2 ** attempt)
    
    async def _handle_human_intervention(self, agent_type: str, stage: WorkflowStage, 
                                       result: Dict[str, Any]):
        """Handle cases requiring human intervention."""
        
        self.current_stage = WorkflowStage.WAITING_APPROVAL
        
        # Create intervention request
        intervention_data = {
            'project_id': self.current_project_id,
            'agent_type': agent_type,
            'stage': stage.value,
            'result': result,
            'intervention_reason': result.get('intervention_reason', 'Manual review required')
        }
        
        # Log intervention request
        await self.database.create_intervention_request(
            project_id=self.current_project_id,
            request_data=intervention_data
        )
        
        self.logger.info(f"Human intervention requested for {stage.value} stage")
    
    async def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status."""
        
        return {
            'project_id': self.current_project_id,
            'current_stage': self.current_stage.value,
            'stages_completed': self.workflow_data.get('stages_completed', []),
            'processing_time': (
                asyncio.get_event_loop().time() - 
                self.workflow_data.get('start_time', 0)
            ) if self.workflow_data.get('start_time') else 0,
            'errors': self.workflow_data.get('errors', []),
            'agent_status': await self.registry.get_all_agent_status()
        }
    
    async def resume_workflow(self, project_id: str, stage: str) -> Dict[str, Any]:
        """Resume workflow from a specific stage."""
        
        # Load project data from database
        project_data = await self.database.get_project(project_id)
        if not project_data:
            raise ValueError(f"Project {project_id} not found")
        
        # Resume workflow
        self.current_project_id = project_id
        self.workflow_data = {
            'project_id': project_id,
            'requirements': project_data.get('requirements', ''),
            'start_time': asyncio.get_event_loop().time(),
            'stages_completed': [],
            'errors': []
        }
        
        self.logger.info(f"Resuming workflow for {project_id} from stage {stage}")
        
        # Continue from specified stage
        # Implementation would depend on stage and previous results
        return await self.get_workflow_status()
    
    async def cancel_workflow(self, project_id: str) -> Dict[str, Any]:
        """Cancel ongoing workflow."""
        
        if self.current_project_id == project_id:
            self.current_stage = WorkflowStage.ERROR
            self.workflow_data['errors'].append('Workflow cancelled by user')
            
            await self.database.update_project_stage(
                project_id=project_id,
                stage='cancelled'
            )
            
            self.logger.info(f"Cancelled workflow for project {project_id}")
            
            return {'project_id': project_id, 'status': 'cancelled'}
        
        return {'error': 'No active workflow for project'}
'''
    
    def _get_fallback_manager(self) -> str:
        """Get fallback agent manager."""
        return '''"""
Fallback agent manager with basic functionality.
"""

class AgentManager:
    def __init__(self, database, logger):
        self.database = database
        self.logger = logger
        self.agents = {}
    
    def register_agent(self, agent_type: str, agent_instance, config=None):
        self.agents[agent_type] = agent_instance
    
    async def process_project(self, project_id: str, requirements: str):
        return {
            'project_id': project_id,
            'status': 'basic_processing',
            'message': 'Fallback processing mode'
        }
'''


class AgentSystemManager(BaseManager):
    """Manager for agent system code generation."""
    
    def __init__(self, llm_client=None, logger=None):
        super().__init__('Agent System', llm_client, logger)
        self.generators = {
            'base_agent': BaseAgentClassGenerator(self),
            'agent_registry': AgentRegistryGenerator(self),
            'agent_manager': AgentManagerGenerator(self)
        }
    
    async def generate_module(self, module_name: str, specifications: Dict[str, Any]) -> str:
        """Generate specific agent system module."""
        if module_name in self.generators:
            return await self.generators[module_name].generate(specifications)
        
        self.logger.warning(f"Unknown module: {module_name}")
        return f"# Module {module_name} not implemented"
    
    async def generate_all_modules(self, specifications: Dict[str, Any]) -> Dict[str, str]:
        """Generate all agent system modules."""
        modules = {}
        
        for module_name, generator in self.generators.items():
            try:
                self.logger.info(f"Generating {module_name} module")
                modules[f"agents/{module_name}.py"] = await generator.generate(specifications)
                self.stats['modules_generated'] += 1
                
            except Exception as e:
                self.logger.error(f"Failed to generate {module_name}: {e}")
                modules[f"agents/{module_name}.py"] = generator.get_fallback_template()
                self.stats['generation_errors'] += 1
        
        return modules
    
    def get_module_dependencies(self) -> Dict[str, List[str]]:
        """Get module dependency mapping."""
        return {
            'base_agent': [],
            'agent_registry': ['base_agent'],
            'agent_manager': ['base_agent', 'agent_registry']
        }
    
    def validate_specifications(self, specifications: Dict[str, Any]) -> bool:
        """Validate agent system specifications."""
        required_keys = ['agent_types', 'workflow_stages']
        return all(key in specifications for key in required_keys)
