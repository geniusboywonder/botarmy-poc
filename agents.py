import asyncio
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from database import DatabaseManager
from llm_client import LLMClient
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):

    def __init__(self, agent_id: str, llm_client: LLMClient,
                 db: DatabaseManager):
        self.agent_id = agent_id
        self.llm_client = llm_client
        self.db = db
        self.status = "idle"
        self.current_task = None
        self.max_attempts = 3
        self.confidence_threshold = 0.7

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return system prompt for this agent"""
        pass

    @abstractmethod
    async def process_message(self, message: Dict) -> Dict:
        """Process incoming message and return response"""
        pass

    async def send_message(self,
                           project_id: str,
                           to_agent: str,
                           message_type: str,
                           content: Dict,
                           confidence: float = None):
        """Send message to another agent"""
        message_id = self.db.add_message(project_id=project_id,
                                         from_agent=self.agent_id,
                                         to_agent=to_agent,
                                         message_type=message_type,
                                         content=content,
                                         confidence=confidence)
        logger.info(f"{self.agent_id} sent message {message_id} to {to_agent}")
        return message_id

    async def escalate_to_human(self, project_id: str, issue: str,
                                options: List[Dict]):
        """Escalate decision to human"""
        conn = sqlite3.connect(self.db.db_path)
        action_id = str(uuid.uuid4())

        conn.execute(
            '''
            INSERT INTO actions (id, project_id, title, description, priority, options)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (action_id, project_id, f"{self.agent_id} needs decision", issue,
              "high", json.dumps(options)))

        conn.commit()
        conn.close()
        return action_id

    def update_status(self, status: str, task: str = None):
        """Update agent status"""
        self.status = status
        self.current_task = task
        logger.info(f"{self.agent_id} status: {status} - {task}")


class AnalystAgent(BaseAgent):

    def __init__(self, llm_client: LLMClient, db: DatabaseManager):
        super().__init__("analyst", llm_client, db)

    def get_system_prompt(self) -> str:
        return """You are a Business Analyst AI responsible for analyzing requirements and creating user stories.

        Your tasks:
        1. Analyze user requirements for clarity and completeness
        2. Create detailed user stories with acceptance criteria
        3. Identify potential risks and constraints
        4. Generate success metrics

        Always respond with structured JSON containing:
        - analysis: Your analysis of the requirements
        - user_stories: Array of user stories with acceptance criteria
        - risks: Identified risks and mitigation strategies
        - success_metrics: Measurable success criteria
        - confidence: Your confidence score (0.0 to 1.0)
        - next_steps: What should happen next

        Be concise but thorough. Ask for clarification if requirements are unclear."""

    async def process_message(self, message: Dict) -> Dict:
        """Process requirements and create analysis"""
        self.update_status("thinking", "Analyzing requirements")

        content = message["content"]
        project_id = message["project_id"]

        if message["message_type"] == "start_analysis":
            requirements = content.get("requirements", "")

            prompt = f"""
            Analyze these product requirements and create a comprehensive analysis:

            Requirements: {requirements}

            Create user stories, identify risks, and suggest success metrics.
            Respond with JSON only.
            """

            response = await self.llm_client.generate_response(
                prompt=prompt,
                system_prompt=self.get_system_prompt(),
                temperature=0.3)

            if response["success"]:
                try:
                    analysis = json.loads(response["content"])
                    confidence = analysis.get("confidence", 0.8)

                    # Send to architect
                    await self.send_message(project_id=project_id,
                                            to_agent="architect",
                                            message_type="handoff",
                                            content=analysis,
                                            confidence=confidence)

                    self.update_status("idle", "Analysis complete")

                    return {
                        "status": "complete",
                        "analysis": analysis,
                        "tokens_used": response["tokens_used"]
                    }

                except json.JSONDecodeError:
                    self.update_status("error",
                                       "Invalid JSON response from LLM")
                    return {
                        "status": "error",
                        "message": "Invalid analysis format"
                    }
            else:
                self.update_status("error", f"LLM error: {response['error']}")
                return {"status": "error", "message": response["error"]}


class ArchitectAgent(BaseAgent):

    def __init__(self, llm_client: LLMClient, db: DatabaseManager):
        super().__init__("architect", llm_client, db)

    def get_system_prompt(self) -> str:
        return """You are a Software Architect AI responsible for creating technical designs.

        Your tasks:
        1. Review business analysis and user stories
        2. Create system architecture and component design
        3. Select appropriate technology stack
        4. Design API specifications and data models
        5. Plan deployment and infrastructure

        Always respond with structured JSON containing:
        - architecture: High-level system design
        - components: List of components with responsibilities
        - tech_stack: Selected technologies with justification
        - api_design: API endpoints and data models
        - deployment_plan: Infrastructure and deployment strategy
        - confidence: Your confidence score (0.0 to 1.0)
        - concerns: Any technical concerns or trade-offs

        Focus on simple, maintainable solutions for POC development."""

    async def process_message(self, message: Dict) -> Dict:
        """Process analysis and create architecture"""
        self.update_status("thinking", "Creating architecture")

        content = message["content"]
        project_id = message["project_id"]

        if message["message_type"] == "handoff":
            analysis = content

            prompt = f"""
            Based on this business analysis, create a technical architecture:

            Analysis: {json.dumps(analysis, indent=2)}

            Design a simple, maintainable architecture suitable for a POC.
            Focus on React frontend, FastAPI backend, and SQLite database.
            Respond with JSON only.
            """

            response = await self.llm_client.generate_response(
                prompt=prompt,
                system_prompt=self.get_system_prompt(),
                temperature=0.2)

            if response["success"]:
                try:
                    architecture = json.loads(response["content"])
                    confidence = architecture.get("confidence", 0.8)

                    # Send to developer
                    await self.send_message(project_id=project_id,
                                            to_agent="developer",
                                            message_type="handoff",
                                            content={
                                                "analysis": analysis,
                                                "architecture": architecture
                                            },
                                            confidence=confidence)

                    self.update_status("idle", "Architecture complete")

                    return {
                        "status": "complete",
                        "architecture": architecture,
                        "tokens_used": response["tokens_used"]
                    }

                except json.JSONDecodeError:
                    self.update_status("error",
                                       "Invalid JSON response from LLM")
                    return {
                        "status": "error",
                        "message": "Invalid architecture format"
                    }
            else:
                self.update_status("error", f"LLM error: {response['error']}")
                return {"status": "error", "message": response["error"]}


# Additional agent classes (DeveloperAgent, TesterAgent) follow similar pattern...
