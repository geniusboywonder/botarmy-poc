"""
Utilities Manager
Manages generation of utility functions and helper modules.
"""

from typing import Dict, Any
from ..base import BaseManager
from .error_handler_generator import ErrorHandlerGenerator
from .logger_generator import LoggerGenerator
from .validator_generator import ValidatorGenerator
from .file_ops_generator import FileOpsGenerator


class UtilitiesManager(BaseManager):
    """
    Manager for utility functions and helper modules.
    Generates error handling, logging, validation, and file operations.
    """

    def __init__(self, llm_client, logger):
        super().__init__(llm_client, logger)
        
        # Initialize generators
        self.generators = {
            'error_handler': ErrorHandlerGenerator(llm_client, logger),
            'logger': LoggerGenerator(llm_client, logger),
            'validator': ValidatorGenerator(llm_client, logger),
            'file_ops': FileOpsGenerator(llm_client, logger)
        }

    async def generate_all(self, specifications: Dict) -> Dict[str, str]:
        """Generate all utility files."""
        
        self.logger.info("Generating utility modules")
        generated_files = {}
        
        try:
            # Create utils directory structure
            generated_files["utils/__init__.py"] = ""
            
            # Generate error handler
            error_handler_content = await self.generators['error_handler'].generate(specifications)
            generated_files["utils/error_handler.py"] = error_handler_content
            self._update_stats(1, "error_handler")
            
            # Generate logger utilities
            logger_content = await self.generators['logger'].generate(specifications)
            generated_files["utils/logger.py"] = logger_content
            self._update_stats(1, "logger")
            
            # Generate validators
            validator_content = await self.generators['validator'].generate(specifications)
            generated_files["utils/validators.py"] = validator_content
            self._update_stats(1, "validator")
            
            # Generate file operations
            file_ops_content = await self.generators['file_ops'].generate(specifications)
            generated_files["utils/file_ops.py"] = file_ops_content
            self._update_stats(1, "file_ops")
            
            self.logger.info(f"Generated {len(generated_files)} utility files")
            return generated_files
            
        except Exception as e:
            self._log_error(f"Utilities generation failed: {str(e)}")
            raise

    def get_manager_stats(self) -> Dict[str, Any]:
        """Get comprehensive manager statistics."""
        
        generator_stats = {}
        for name, generator in self.generators.items():
            generator_stats[name] = generator.get_generator_stats()
        
        return {
            "manager_type": "utilities",
            "manager_stats": self.stats,
            "generator_stats": generator_stats,
            "files_types": ["utils/error_handler.py", "utils/logger.py", "utils/validators.py", "utils/file_ops.py"]
        }

    def validate_dependencies(self) -> bool:
        """Validate dependencies for utilities."""
        
        # Utilities have minimal dependencies
        if not self.llm_client:
            self._log_error("LLM client not available for utilities generation")
            return False
            
        return True
