"""
App Core Manager
Manages generation of core FastAPI application components:
- FastAPI main application
- Configuration management
- Database operations
- LLM client integration
"""

from typing import Dict, Any
from ..base import BaseManager
from .fastapi_generator import FastAPIGenerator
from .config_generator import ConfigGenerator
from .database_generator import DatabaseGenerator
from .llm_client_generator import LLMClientGenerator


class AppCoreManager(BaseManager):
    """
    Manager for core application components.
    Generates the foundational FastAPI application files.
    """

    def __init__(self, llm_client, logger):
        super().__init__(llm_client, logger)
        
        # Initialize generators
        self.generators = {
            'fastapi': FastAPIGenerator(llm_client, logger),
            'config': ConfigGenerator(llm_client, logger),
            'database': DatabaseGenerator(llm_client, logger),
            'llm_client': LLMClientGenerator(llm_client, logger)
        }

    async def generate_all(self, specifications: Dict) -> Dict[str, str]:
        """Generate all core application files."""
        
        self.logger.info("Generating core application components")
        generated_files = {}
        
        try:
            # Generate main FastAPI application
            main_content = await self.generators['fastapi'].generate(specifications)
            generated_files["main.py"] = main_content
            self._update_stats(1, "fastapi")
            
            # Generate configuration module
            config_content = await self.generators['config'].generate(specifications)
            generated_files["config.py"] = config_content
            self._update_stats(1, "config")
            
            # Generate database module
            database_content = await self.generators['database'].generate(specifications)
            generated_files["database.py"] = database_content
            self._update_stats(1, "database")
            
            # Generate LLM client
            llm_client_content = await self.generators['llm_client'].generate(specifications)
            generated_files["llm_client.py"] = llm_client_content
            self._update_stats(1, "llm_client")
            
            self.logger.info(f"Generated {len(generated_files)} core application files")
            return generated_files
            
        except Exception as e:
            self._log_error(f"App core generation failed: {str(e)}")
            raise

    def get_manager_stats(self) -> Dict[str, Any]:
        """Get comprehensive manager statistics."""
        
        generator_stats = {}
        for name, generator in self.generators.items():
            generator_stats[name] = generator.get_generator_stats()
        
        return {
            "manager_type": "app_core",
            "manager_stats": self.stats,
            "generator_stats": generator_stats,
            "files_types": ["main.py", "config.py", "database.py", "llm_client.py"]
        }

    def validate_dependencies(self) -> bool:
        """Validate dependencies for core app components."""
        
        # Core components have minimal external dependencies
        # Mainly validate that LLM client is available
        if not self.llm_client:
            self._log_error("LLM client not available for core app generation")
            return False
            
        return True
