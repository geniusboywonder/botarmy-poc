import json
import asyncio
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from ..prompts.architect_prompts import ARCHITECT_PROMPTS

class ArchitectAgent(BaseAgent):
    """
    Architect Agent responsible for creating technical design and system architecture
    based on analyzed requirements from the Analyst Agent.
    """

    def __init__(self, llm_client, database, logger):
        super().__init__(
            agent_type="architect",
            llm_client=llm_client,
            database=database,
            logger=logger
        )
        self.design_patterns = [
            "mvc", "microservices", "layered", "clean_architecture", 
            "hexagonal", "cqrs", "event_sourcing"
        ]
        self.tech_stacks = {
            "web": ["react", "vue", "angular", "svelte"],
            "backend": ["fastapi", "express", "spring", "django"],
            "database": ["postgresql", "mysql", "mongodb", "sqlite"],
            "deployment": ["docker", "kubernetes", "serverless"]
        }

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process analyst output and create technical architecture.

        Args:
            input_data: Dictionary containing analyst output with user stories

        Returns:
            Dictionary containing technical design and architecture decisions
        """
        try:
            self.logger.info(f"Architect agent processing input for project {input_data.get('project_id')}")

            # Extract user stories and requirements
            user_stories = input_data.get('user_stories', [])
            requirements = input_data.get('requirements', {})
            constraints = input_data.get('constraints', {})

            # Update agent status
            await self._update_status("analyzing_requirements")

            # Step 1: Analyze technical requirements
            tech_analysis = await self._analyze_technical_requirements(
                user_stories, requirements, constraints
            )

            # Step 2: Select technology stack
            await self._update_status("selecting_technology_stack")
            tech_stack = await self._select_technology_stack(tech_analysis)

            # Step 3: Design system architecture
            await self._update_status("designing_architecture")
            architecture = await self._design_system_architecture(
                tech_analysis, tech_stack, user_stories
            )

            # Step 4: Create file structure
            await self._update_status("creating_file_structure")
            file_structure = await self._create_file_structure(architecture, tech_stack)

            # Step 5: Generate technical specifications
            await self._update_status("generating_specifications")
            specifications = await self._generate_technical_specifications(
                architecture, tech_stack, file_structure
            )

            # Compile final output
            output = {
                "project_id": input_data.get('project_id'),
                "technical_analysis": tech_analysis,
                "technology_stack": tech_stack,
                "system_architecture": architecture,
                "file_structure": file_structure,
                "technical_specifications": specifications,
                "estimated_complexity": self._calculate_complexity(user_stories),
                "development_timeline": self._estimate_timeline(user_stories, tech_stack),
                "risk_assessment": self._assess_risks(tech_stack, architecture),
                "agent_metadata": {
                    "agent_type": self.agent_type,
                    "processing_time": self.processing_time,
                    "token_usage": self.token_usage,
                    "confidence_score": self._calculate_confidence(tech_analysis)
                }
            }

            await self._update_status("completed")
            self.logger.info(f"Architect agent completed processing for project {input_data.get('project_id')}")

            return output

        except Exception as e:
            await self._handle_error(f"Architect agent processing failed: {str(e)}")
            raise

    async def _analyze_technical_requirements(self, user_stories: List[Dict], 
                                            requirements: Dict, constraints: Dict) -> Dict:
        """Analyze user stories to extract technical requirements."""

        prompt = ARCHITECT_PROMPTS["analyze_requirements"].format(
            user_stories=json.dumps(user_stories, indent=2),
            functional_requirements=json.dumps(requirements.get('functional', {}), indent=2),
            non_functional_requirements=json.dumps(requirements.get('non_functional', {}), indent=2),
            constraints=json.dumps(constraints, indent=2)
        )

        response = await self.llm_client.generate(
            prompt=prompt,
            max_tokens=1500,
            temperature=0.2
        )

        # Parse structured response
        try:
            analysis = json.loads(response)
            return {
                "core_features": analysis.get("core_features", []),
                "integration_points": analysis.get("integration_points", []),
                "data_requirements": analysis.get("data_requirements", {}),
                "performance_requirements": analysis.get("performance_requirements", {}),
                "security_requirements": analysis.get("security_requirements", {}),
                "scalability_needs": analysis.get("scalability_needs", {}),
                "ui_complexity": analysis.get("ui_complexity", "medium"),
                "backend_complexity": analysis.get("backend_complexity", "medium")
            }
        except json.JSONDecodeError:
            self.logger.error("Failed to parse technical analysis response")
            return self._create_default_analysis(user_stories)

    async def _select_technology_stack(self, tech_analysis: Dict) -> Dict:
        """Select appropriate technology stack based on technical analysis."""

        prompt = ARCHITECT_PROMPTS["select_tech_stack"].format(
            technical_analysis=json.dumps(tech_analysis, indent=2),
            available_stacks=json.dumps(self.tech_stacks, indent=2),
            constraints="free, open-source, lightweight, cloud-native"
        )

        response = await self.llm_client.generate(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.1
        )

        try:
            stack = json.loads(response)
            # Validate and set defaults for POC
            return {
                "frontend": stack.get("frontend", "react"),
                "backend": stack.get("backend", "fastapi"),
                "database": stack.get("database", "sqlite"),
                "styling": stack.get("styling", "tailwindcss"),
                "deployment": stack.get("deployment", "replit"),
                "real_time": stack.get("real_time", "sse"),
                "testing": stack.get("testing", "pytest"),
                "justification": stack.get("justification", {}),
                "alternatives": stack.get("alternatives", {})
            }
        except json.JSONDecodeError:
            return self._create_default_tech_stack()

    async def _design_system_architecture(self, tech_analysis: Dict, 
                                         tech_stack: Dict, user_stories: List) -> Dict:
        """Design high-level system architecture."""

        prompt = ARCHITECT_PROMPTS["design_architecture"].format(
            technical_analysis=json.dumps(tech_analysis, indent=2),
            technology_stack=json.dumps(tech_stack, indent=2),
            user_stories=json.dumps(user_stories[:5], indent=2)  # Limit for token efficiency
        )

        response = await self.llm_client.generate(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.2
        )

        try:
            architecture = json.loads(response)
            return {
                "architectural_pattern": architecture.get("pattern", "layered"),
                "components": architecture.get("components", []),
                "data_flow": architecture.get("data_flow", []),
                "api_design": architecture.get("api_design", {}),
                "security_layers": architecture.get("security_layers", []),
                "deployment_architecture": architecture.get("deployment", {}),
                "scalability_strategy": architecture.get("scalability", {}),
                "monitoring_strategy": architecture.get("monitoring", {})
            }
        except json.JSONDecodeError:
            return self._create_default_architecture(tech_stack)

    async def _create_file_structure(self, architecture: Dict, tech_stack: Dict) -> Dict:
        """Generate project file and folder structure."""

        prompt = ARCHITECT_PROMPTS["create_file_structure"].format(
            architecture=json.dumps(architecture, indent=2),
            tech_stack=json.dumps(tech_stack, indent=2),
            project_type="web_application"
        )

        response = await self.llm_client.generate(
            prompt=prompt,
            max_tokens=1500,
            temperature=0.1
        )

        try:
            structure = json.loads(response)
            return {
                "root_files": structure.get("root_files", []),
                "backend_structure": structure.get("backend", {}),
                "frontend_structure": structure.get("frontend", {}),
                "config_files": structure.get("config", []),
                "documentation": structure.get("docs", []),
                "deployment_files": structure.get("deployment", []),
                "testing_structure": structure.get("tests", {})
            }
        except json.JSONDecodeError:
            return self._create_default_file_structure(tech_stack)

    async def _generate_technical_specifications(self, architecture: Dict, 
                                               tech_stack: Dict, file_structure: Dict) -> Dict:
        """Generate detailed technical specifications."""

        return {
            "api_endpoints": await self._define_api_endpoints(architecture),
            "database_schema": await self._define_database_schema(architecture),
            "component_specifications": await self._define_components(architecture),
            "integration_requirements": await self._define_integrations(architecture),
            "performance_requirements": self._define_performance_requirements(architecture),
            "security_requirements": self._define_security_requirements(architecture),
            "testing_requirements": self._define_testing_requirements(file_structure)
        }

    def _calculate_complexity(self, user_stories: List) -> str:
        """Calculate project complexity based on user stories."""
        story_count = len(user_stories)
        if story_count < 5:
            return "low"
        elif story_count < 15:
            return "medium"
        else:
            return "high"

    def _estimate_timeline(self, user_stories: List, tech_stack: Dict) -> Dict:
        """Estimate development timeline."""
        base_days = len(user_stories) * 0.5  # 0.5 days per user story

        # Adjust based on technology complexity
        if tech_stack.get("frontend") in ["react", "vue"]:
            base_days *= 1.2
        if tech_stack.get("backend") in ["fastapi", "django"]:
            base_days *= 1.1

        return {
            "estimated_days": int(base_days),
            "phases": {
                "setup": 1,
                "backend": int(base_days * 0.4),
                "frontend": int(base_days * 0.4),
                "integration": int(base_days * 0.2)
            }
        }

    def _assess_risks(self, tech_stack: Dict, architecture: Dict) -> List[Dict]:
        """Assess technical risks."""
        risks = []

        # Technology risks
        if tech_stack.get("database") == "sqlite":
            risks.append({
                "type": "scalability",
                "description": "SQLite may not scale for high concurrency",
                "severity": "medium",
                "mitigation": "Plan migration to PostgreSQL for production"
            })

        # Architecture risks
        if architecture.get("architectural_pattern") == "monolithic":
            risks.append({
                "type": "maintainability",
                "description": "Monolithic architecture may become hard to maintain",
                "severity": "low",
                "mitigation": "Consider microservices for future iterations"
            })

        return risks

    def _calculate_confidence(self, tech_analysis: Dict) -> float:
        """Calculate confidence score for architectural decisions."""
        # Simple confidence calculation based on completeness
        required_fields = ["core_features", "data_requirements", "performance_requirements"]
        completed_fields = sum(1 for field in required_fields if tech_analysis.get(field))
        return completed_fields / len(required_fields)

    # Helper methods for default fallbacks
    def _create_default_analysis(self, user_stories: List) -> Dict:
        """Create default technical analysis if LLM parsing fails."""
        return {
            "core_features": ["user_management", "data_processing", "ui_interface"],
            "integration_points": ["database", "external_apis"],
            "data_requirements": {"storage": "relational", "volume": "small"},
            "performance_requirements": {"response_time": "< 2s", "concurrent_users": "< 100"},
            "security_requirements": {"authentication": "required", "authorization": "role_based"},
            "scalability_needs": {"initial": "single_server", "future": "horizontal"},
            "ui_complexity": "medium",
            "backend_complexity": "medium"
        }

    def _create_default_tech_stack(self) -> Dict:
        """Create default technology stack for POC."""
        return {
            "frontend": "react",
            "backend": "fastapi", 
            "database": "sqlite",
            "styling": "tailwindcss",
            "deployment": "replit",
            "real_time": "sse",
            "testing": "pytest",
            "justification": {"reason": "POC optimized for rapid development"},
            "alternatives": {}
        }

    def _create_default_architecture(self, tech_stack: Dict) -> Dict:
        """Create default architecture pattern."""
        return {
            "architectural_pattern": "layered",
            "components": ["frontend", "api", "business_logic", "data_layer"],
            "data_flow": ["user -> frontend -> api -> business -> data"],
            "api_design": {"style": "REST", "format": "JSON"},
            "security_layers": ["input_validation", "authentication", "authorization"],
            "deployment_architecture": {"type": "single_server", "platform": tech_stack.get("deployment")},
            "scalability_strategy": {"initial": "vertical", "future": "horizontal"},
            "monitoring_strategy": {"logging": "structured", "metrics": "basic"}
        }

    def _create_default_file_structure(self, tech_stack: Dict) -> Dict:
        """Create default file structure."""
        return {
            "root_files": ["README.md", "requirements.txt", "main.py", ".gitignore"],
            "backend": {
                "main.py": "FastAPI application entry point",
                "agents/": "Agent implementations",
                "database.py": "Database operations",
                "config.py": "Configuration management"
            },
            "frontend": {
                "src/": "React source code",
                "public/": "Static assets",
                "package.json": "Node dependencies"
            },
            "config": [".env.example", "replit.nix"],
            "docs": ["API.md", "DEPLOYMENT.md"],
            "deployment": ["Dockerfile", "docker-compose.yml"],
            "tests": {"unit/": "Unit tests", "integration/": "Integration tests"}
        }

    async def _define_api_endpoints(self, architecture: Dict) -> List[Dict]:
        """Define API endpoints based on architecture."""
        return [
            {"method": "POST", "path": "/api/projects", "description": "Create new project"},
            {"method": "GET", "path": "/api/projects/{id}", "description": "Get project details"},
            {"method": "POST", "path": "/api/projects/{id}/start", "description": "Start agent workflow"},
            {"method": "GET", "path": "/api/stream", "description": "Server-sent events for real-time updates"},
            {"method": "GET", "path": "/api/agents/status", "description": "Get all agent statuses"},
            {"method": "POST", "path": "/api/conflicts/resolve", "description": "Resolve agent conflicts"}
        ]

    async def _define_database_schema(self, architecture: Dict) -> Dict:
        """Define database schema."""
        return {
            "tables": {
                "projects": ["id", "requirements", "status", "created_at", "updated_at"],
                "messages": ["id", "project_id", "from_agent", "to_agent", "content", "status", "created_at"],
                "agents": ["id", "project_id", "agent_type", "status", "progress", "metadata"],
                "conflicts": ["id", "project_id", "description", "resolution", "resolved_by", "created_at"],
                "files": ["id", "project_id", "filename", "content", "file_type", "generated_by"]
            },
            "indexes": ["projects.status", "messages.project_id", "agents.project_id"],
            "relationships": [
                "messages.project_id -> projects.id",
                "agents.project_id -> projects.id",
                "conflicts.project_id -> projects.id"
            ]
        }

    async def _define_components(self, architecture: Dict) -> Dict:
        """Define component specifications."""
        return {
            "Dashboard": "Main layout component with navigation and agent panels",
            "AgentPanel": "Display agent status, progress, and conversation history",
            "ActionQueue": "Human intervention requests and conflict resolution",
            "ProjectViewer": "Project requirements and generated file display",
            "StatusBar": "System health, performance metrics, and connection status"
        }

    async def _define_integrations(self, architecture: Dict) -> List[Dict]:
        """Define integration requirements."""
        return [
            {"service": "OpenAI API", "purpose": "LLM completion", "auth": "API key"},
            {"service": "File System", "purpose": "Project file storage", "auth": "none"},
            {"service": "SQLite", "purpose": "Data persistence", "auth": "none"}
        ]

    def _define_performance_requirements(self, architecture: Dict) -> Dict:
        """Define performance requirements."""
        return {
            "response_time": {"api": "< 2s", "ui": "< 1s", "agent": "< 30s"},
            "throughput": {"concurrent_users": 10, "requests_per_second": 50},
            "resource_usage": {"memory": "< 512MB", "cpu": "< 80%", "storage": "< 1GB"}
        }

    def _define_security_requirements(self, architecture: Dict) -> Dict:
        """Define security requirements."""
        return {
            "authentication": "API key based for OpenAI",
            "input_validation": "All user inputs sanitized",
            "data_protection": "Environment variables for secrets",
            "api_security": "CORS configuration and rate limiting"
        }

    def _define_testing_requirements(self, file_structure: Dict) -> Dict:
        """Define testing requirements."""
        return {
            "unit_tests": "Test all agent functions and API endpoints",
            "integration_tests": "Test agent workflow and database operations",
            "e2e_tests": "Test complete user workflows",
            "coverage_target": "80% minimum"
        }