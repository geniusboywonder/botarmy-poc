"""
BotArmy Backend Generator - Main Orchestrator
Lightweight coordinator that delegates to specialized managers for backend code generation.
Follows the modularization plan to replace the monolithic complete_backend_generator.py.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import specialized managers
from .app_core.app_core_manager import AppCoreManager
from .agent_system.agent_system_manager import AgentSystemManager  
from .workflow.workflow_manager import WorkflowManager
from .data_models.data_models_manager import DataModelsManager
from .utilities.utilities_manager import UtilitiesManager
from .infrastructure.infrastructure_manager import InfrastructureManager

class BackendGenerator:
    """
    Main orchestrator for backend code generation.
    Coordinates specialized managers to generate complete backend architecture.
    
    This replaces the monolithic complete_backend_generator.py with a modular approach
    that delegates to specialized managers for different concerns.
    """

    def __init__(self, llm_client, logger):
        self.llm_client = llm_client
        self.logger = logger
        
        # Initialize specialized managers
        self.managers = {
            'app_core': AppCoreManager(llm_client, logger),
            'agent_system': AgentSystemManager(llm_client, logger),
            'workflow': WorkflowManager(llm_client, logger),
            'data_models': DataModelsManager(llm_client, logger),
            'utilities': UtilitiesManager(llm_client, logger),
            'infrastructure': InfrastructureManager(llm_client, logger)
        }
        
        # Generation statistics
        self.generation_stats = {
            "total_files": 0,
            "total_lines": 0,
            "managers_used": 0,
            "errors": [],
            "warnings": [],
            "start_time": None,
            "end_time": None
        }

    async def generate_all_backend_files(self, architecture: Dict, tech_stack: Dict, 
                                        specifications: Dict) -> Dict[str, str]:
        """
        Generate all backend files using specialized managers.
        
        Args:
            architecture: System architecture specification
            tech_stack: Technology stack choices  
            specifications: Detailed technical specifications
            
        Returns:
            Dictionary of filename -> file content mappings
        """
        
        self.generation_stats["start_time"] = datetime.now()
        self.logger.info("Starting modular backend generation")
        
        try:
            # Aggregate all generated files
            all_files = {}
            
            # Execute managers in dependency order
            manager_order = [
                ('app_core', 'Core application components'),
                ('data_models', 'Data models and schemas'),
                ('utilities', 'Utility functions and helpers'),
                ('agent_system', 'Agent coordination system'),
                ('workflow', 'Workflow management system'),
                ('infrastructure', 'Infrastructure and deployment')
            ]
            
            for manager_key, description in manager_order:
                self.logger.info(f"Generating {description}")
                
                try:
                    manager = self.managers[manager_key]
                    manager_files = await manager.generate_all(specifications)
                    
                    # Merge files from this manager
                    all_files.update(manager_files)
                    self.generation_stats["managers_used"] += 1
                    
                    self.logger.info(f"Generated {len(manager_files)} files from {manager_key}")
                    
                except Exception as e:
                    error_msg = f"Manager {manager_key} failed: {str(e)}"
                    self.logger.error(error_msg)
                    self.generation_stats["errors"].append(error_msg)
                    
                    # Continue with other managers
                    continue
            
            # Update final statistics
            self.generation_stats["total_files"] = len(all_files)
            self.generation_stats["total_lines"] = sum(
                content.count('\n') + 1 for content in all_files.values()
            )
            self.generation_stats["end_time"] = datetime.now()
            
            self.logger.info(f"Backend generation completed: {self.generation_stats['total_files']} files, "
                           f"{self.generation_stats['total_lines']} lines")
            
            return all_files
            
        except Exception as e:
            self.generation_stats["end_time"] = datetime.now()
            self.logger.error(f"Backend generation failed: {str(e)}")
            raise

    async def generate_partial(self, manager_names: List[str], specifications: Dict) -> Dict[str, str]:
        """
        Generate files from specific managers only.
        
        Args:
            manager_names: List of manager names to use
            specifications: Generation specifications
            
        Returns:
            Dictionary of generated files
        """
        
        self.logger.info(f"Generating partial backend from managers: {manager_names}")
        
        all_files = {}
        
        for manager_name in manager_names:
            if manager_name not in self.managers:
                self.logger.warning(f"Unknown manager: {manager_name}")
                continue
                
            try:
                manager = self.managers[manager_name]
                manager_files = await manager.generate_all(specifications)
                all_files.update(manager_files)
                
                self.logger.info(f"Generated {len(manager_files)} files from {manager_name}")
                
            except Exception as e:
                self.logger.error(f"Partial generation failed for {manager_name}: {str(e)}")
                continue
        
        return all_files

    def get_generation_stats(self) -> Dict[str, Any]:
        """Get comprehensive generation statistics."""
        
        # Calculate processing time if available
        processing_time = 0
        if self.generation_stats["start_time"] and self.generation_stats["end_time"]:
            delta = self.generation_stats["end_time"] - self.generation_stats["start_time"]
            processing_time = delta.total_seconds()
        
        # Get manager-specific statistics
        manager_stats = {}
        for name, manager in self.managers.items():
            manager_stats[name] = manager.get_manager_stats()
        
        return {
            **self.generation_stats,
            "processing_time": processing_time,
            "manager_stats": manager_stats,
            "success_rate": (
                (self.generation_stats["managers_used"] - len(self.generation_stats["errors"])) /
                max(self.generation_stats["managers_used"], 1) * 100
            )
        }

    def validate_dependencies(self) -> Dict[str, bool]:
        """
        Validate that all manager dependencies are satisfied.
        
        Returns:
            Dictionary of manager -> validation status
        """
        
        validation_results = {}
        
        for name, manager in self.managers.items():
            try:
                # Each manager should implement a validate_dependencies method
                if hasattr(manager, 'validate_dependencies'):
                    validation_results[name] = manager.validate_dependencies()
                else:
                    validation_results[name] = True
                    
            except Exception as e:
                self.logger.error(f"Dependency validation failed for {name}: {str(e)}")
                validation_results[name] = False
        
        return validation_results

    def get_available_managers(self) -> List[str]:
        """Get list of available manager names."""
        return list(self.managers.keys())

    def reset_stats(self):
        """Reset generation statistics."""
        self.generation_stats = {
            "total_files": 0,
            "total_lines": 0,
            "managers_used": 0,
            "errors": [],
            "warnings": [],
            "start_time": None,
            "end_time": None
        }
        
        # Reset manager statistics
        for manager in self.managers.values():
            if hasattr(manager, 'reset_stats'):
                manager.reset_stats()
