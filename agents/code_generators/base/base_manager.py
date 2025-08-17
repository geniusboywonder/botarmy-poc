"""
Base Manager Interface
Provides consistent interface for all specialized managers in the backend generation system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime


class BaseManager(ABC):
    """
    Base class for all backend generation managers.
    Ensures consistent interface and common functionality across all managers.
    """

    def __init__(self, llm_client, logger):
        self.llm_client = llm_client
        self.logger = logger
        self.generators = {}
        
        # Manager statistics
        self.stats = {
            "files_generated": 0,
            "generators_used": 0,
            "errors": [],
            "warnings": [],
            "last_generation": None
        }

    @abstractmethod
    async def generate_all(self, specifications: Dict) -> Dict[str, str]:
        """
        Generate all files managed by this manager.
        
        Args:
            specifications: Technical specifications for generation
            
        Returns:
            Dictionary of filename -> content mappings
        """
        pass

    @abstractmethod
    def get_manager_stats(self) -> Dict[str, Any]:
        """
        Return generation statistics for this manager.
        
        Returns:
            Statistics dictionary with generation metrics
        """
        pass

    def validate_dependencies(self) -> bool:
        """
        Validate that all dependencies for this manager are satisfied.
        Can be overridden by specific managers.
        
        Returns:
            True if dependencies are satisfied, False otherwise
        """
        return True

    def _update_stats(self, files_count: int, generator_name: str = None):
        """Update manager statistics after generation."""
        self.stats["files_generated"] += files_count
        if generator_name:
            self.stats["generators_used"] += 1
        self.stats["last_generation"] = datetime.now()

    def _log_error(self, error_message: str):
        """Log and track errors."""
        self.stats["errors"].append({
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        })
        self.logger.error(error_message)

    def _log_warning(self, warning_message: str):
        """Log and track warnings."""
        self.stats["warnings"].append({
            "message": warning_message,
            "timestamp": datetime.now().isoformat()
        })
        self.logger.warning(warning_message)

    def reset_stats(self):
        """Reset manager statistics."""
        self.stats = {
            "files_generated": 0,
            "generators_used": 0,
            "errors": [],
            "warnings": [],
            "last_generation": None
        }
