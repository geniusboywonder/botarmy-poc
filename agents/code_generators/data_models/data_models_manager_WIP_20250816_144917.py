"""
Data Models Manager
Manages generation of data models and database schemas for the BotArmy system.
"""

from typing import Dict, Any
from ..base import BaseManager
from .project_model_generator import ProjectModelGenerator
from .agent_model_generator import AgentModelGenerator
from .message_model_generator import MessageModelGenerator
from .schema_generator import SchemaGenerator


class DataModelsManager(BaseManager):
    """
    Manager for data models and database schemas.
    Generates Pydantic models and database schema definitions.
    """

    def __init__(self, llm_client, logger):
        super().__init__(llm_client, logger)
        
        # Initialize generators
        self.generators = {
            'project_model': ProjectModelGenerator(llm_client, logger),
            'agent_model': AgentModelGenerator(llm_client, logger),
            'message_model': MessageModelGenerator(llm_client, logger),
            'schema': SchemaGenerator(llm_client, logger)
        }

    async def generate_all(self, specifications: Dict) -> Dict[str, str]:
        """Generate all data model files."""
        
        self.logger.info("Generating data models and schemas")
        generated_files = {}
        
        try:
            # Create models directory structure
            generated_files["models/__init__.py"] = ""
            
            # Generate project models
            project_model_content = await self.generators['project_model'].generate(specifications)
            generated_files["models/project.py"] = project_model_content
            self._update_stats(1, "project_model")
            
            # Generate agent models  
            agent_model_content = await self.generators['agent_model'].generate(specifications)
            generated_files["models/agent.py"] = agent_model_content
            self._update_stats(1, "agent_model")
            
            # Generate message models
            message_model_content = await self.generators['message_model'].generate(specifications)
            generated_files["models/message.py"] = message_model_content
            self._update_stats(1, "message_model")
            
            # Generate database schema
            schema_content = await self.generators['schema'].generate(specifications)
            generated_files["db_schema.py"] = schema_content
            self._update_stats(1, "schema")
            
            self.logger.info(f"Generated {len(generated_files)} data model files")
            return generated_files
            
        except Exception as e:
            self._log_error(f"Data models generation failed: {str(e)}")
            raise

    def get_manager_stats(self) -> Dict[str, Any]:
        """Get comprehensive manager statistics."""
        
        generator_stats = {}
        for name, generator in self.generators.items():
            generator_stats[name] = generator.get_generator_stats()
        
        return {
            "manager_type": "data_models",
            "manager_stats": self.stats,
            "generator_stats": generator_stats,
            "files_types": ["models/project.py", "models/agent.py", "models/message.py", "db_schema.py"]
        }

    def validate_dependencies(self) -> bool:
        """Validate dependencies for data models."""
        
        # Data models have minimal dependencies 
        if not self.llm_client:
            self._log_error("LLM client not available for data models generation")
            return False
            
        return True
