import asyncio
import os
import json
import time
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from .code_generators.backend_generator import BackendGenerator
from .code_generators.frontend_generator import FrontendGenerator
from .quality.quality_checker import QualityChecker
from .file_management.file_manager import FileManager
from .developer_utils import DeveloperUtils
from prompts.developer_prompts import DEVELOPER_PROMPTS

class DeveloperAgent(BaseAgent):
    """
    Core Developer Agent responsible for orchestrating code generation
    using specialized generator modules.
    """

    def __init__(self, llm_client, database, logger):
        super().__init__(
            agent_type="developer",
            llm_client=llm_client,
            database=database,
            logger=logger
        )
        
        # Initialize specialized modules
        self.backend_generator = BackendGenerator(llm_client, logger)
        self.frontend_generator = FrontendGenerator(llm_client, logger)
        self.quality_checker = QualityChecker(logger)
        self.file_manager = FileManager(logger)
        self.utils = DeveloperUtils()
        
        # Core configuration
        self.supported_languages = ["python", "javascript", "typescript", "html", "css", "sql"]
        self.quality_threshold = 0.7  # Minimum quality score for acceptance

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing orchestration - delegates to specialized modules.
        
        Args:
            input_data: Dictionary containing architect output with specifications
            
        Returns:
            Dictionary containing generated code files and metadata
        """
        try:
            project_id = input_data.get('project_id')
            self.logger.info(f"Developer agent processing project {project_id}")
            self._start_processing(project_id)

            # Extract specifications
            architecture = input_data.get('system_architecture', {})
            tech_stack = input_data.get('technology_stack', {})
            file_structure = input_data.get('file_structure', {})
            specifications = input_data.get('technical_specifications', {})

            await self._update_status("analyzing_architecture", 10)

            # Step 1: Create generation plan
            generation_plan = await self._create_generation_plan(
                architecture, tech_stack, file_structure, specifications
            )

            # Step 2: Generate backend code
            await self._update_status("generating_backend", 25)
            backend_files = await self.backend_generator.generate_backend_code(
                generation_plan, architecture, tech_stack, specifications
            )

            # Step 3: Generate frontend code  
            await self._update_status("generating_frontend", 50)
            frontend_files = await self.frontend_generator.generate_frontend_code(
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
            all_files = {
                **backend_files,
                **frontend_files, 
                **config_files,
                **documentation_files
            }
            
            quality_report = await self.quality_checker.perform_comprehensive_quality_check(
                backend_files, frontend_files, config_files
            )

            # Step 7: Package and save files
            await self._update_status("packaging_output", 98)
            
            # Use file manager to organize and save files
            project_structure = await self.file_manager.create_project_structure(
                project_id, all_files
            )

            # Generate final output
            output = await self._generate_final_output(
                input_data, all_files, generation_plan, quality_report, project_structure
            )

            await self._update_status("completed", 100)
            self._finish_processing()
            self.logger.info(f"Developer agent completed project {project_id}")

            return output

        except Exception as e:
            await self._handle_error(f"Developer agent processing failed: {str(e)}")
            raise

    async def _create_generation_plan(self, architecture: Dict, tech_stack: Dict, 
                                      file_structure: Dict, specifications: Dict) -> Dict:
        """Create a comprehensive plan for code generation."""
        
        prompt = DEVELOPER_PROMPTS.get("create_generation_plan", "").format(
            architecture=json.dumps(architecture, indent=2),
            tech_stack=json.dumps(tech_stack, indent=2),
            file_structure=json.dumps(file_structure, indent=2),
            specifications=json.dumps(specifications, indent=2)
        )

        try:
            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.2
            )
            
            plan = json.loads(response)
            return self.utils.validate_generation_plan(plan)
            
        except (json.JSONDecodeError, Exception):
            self.logger.warning("Failed to parse LLM generation plan, using default")
            return self.utils.create_default_generation_plan()

    async def _generate_configuration_files(self, plan: Dict, tech_stack: Dict) -> Dict:
        """Generate configuration and deployment files using utilities."""
        
        config_files = {}
        
        # Generate standard config files
        config_generators = {
            "requirements.txt": self.utils.generate_requirements_txt,
            "package.json": lambda: self.utils.generate_package_json(tech_stack),
            ".env.example": self.utils.generate_env_template,
            "replit.nix": self.utils.generate_replit_config,
            ".replit": self.utils.generate_replit_file,
            "vite.config.js": self.utils.generate_vite_config,
            ".gitignore": self.utils.generate_gitignore
        }
        
        for filename, generator in config_generators.items():
            try:
                config_files[filename] = await generator()
            except Exception as e:
                self.logger.error(f"Failed to generate {filename}: {str(e)}")
                config_files[filename] = f"# Error generating {filename}: {str(e)}"
                
        return config_files

    async def _generate_documentation(self, plan: Dict, architecture: Dict, tech_stack: Dict,
                                      backend_files: Dict, frontend_files: Dict) -> Dict:
        """Generate comprehensive documentation using utilities."""
        
        doc_files = {}
        
        # Generate documentation files
        try:
            doc_files["README.md"] = await self.utils.generate_readme(
                architecture, tech_stack, plan
            )
            
            doc_files["docs/API.md"] = await self.utils.generate_api_docs(
                backend_files
            )
            
            doc_files["docs/DEPLOYMENT.md"] = await self.utils.generate_deployment_docs(
                tech_stack
            )
            
            doc_files["docs/DEVELOPMENT.md"] = await self.utils.generate_development_docs(
                backend_files, frontend_files
            )
            
        except Exception as e:
            self.logger.error(f"Documentation generation error: {str(e)}")
            doc_files["README.md"] = f"# Project Documentation\n\nError generating documentation: {str(e)}"
            
        return doc_files

    async def _generate_final_output(self, input_data: Dict, all_files: Dict, 
                                     generation_plan: Dict, quality_report: Dict,
                                     project_structure: Dict) -> Dict[str, Any]:
        """Generate the final comprehensive output."""
        
        return {
            "project_id": input_data.get('project_id'),
            "generated_files": all_files,
            "file_count": len(all_files),
            "generation_plan": generation_plan,
            "project_structure": project_structure,
            "implementation_notes": self.utils.create_implementation_notes(
                input_data, quality_report
            ),
            "quality_report": quality_report,
            "deployment_instructions": self.utils.create_deployment_instructions(
                input_data.get('technology_stack', {})
            ),
            "next_steps": self.utils.create_next_steps(quality_report),
            "agent_metadata": {
                "agent_type": self.agent_type,
                "processing_time": self.processing_time,
                "token_usage": self.llm_client.get_usage_stats(),
                "lines_of_code": self.utils.count_lines_of_code(all_files),
                "confidence_score": self.utils.calculate_confidence(quality_report),
                "quality_threshold_met": quality_report.get("quality_score", 0) >= self.quality_threshold
            }
        }

    def get_module_status(self) -> Dict[str, Any]:
        """Get status of all modules for debugging."""
        return {
            "core_agent": self.get_status(),
            "backend_generator": getattr(self.backend_generator, 'last_generation_time', None),
            "frontend_generator": getattr(self.frontend_generator, 'last_generation_time', None),
            "quality_checker": getattr(self.quality_checker, 'last_check_time', None),
            "file_manager": getattr(self.file_manager, 'last_operation_time', None)
        }
