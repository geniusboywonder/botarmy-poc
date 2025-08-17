"""
Specialized Agent Generators - Individual agent implementations.
"""

from ..base.base_generator import BaseGenerator


class AnalystAgentGenerator(BaseGenerator):
    """Generates the Analyst Agent implementation."""
    
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
    
    async def generate(self, specifications: dict) -> str:
        """Generate analyst agent implementation."""
        try:
            return self._generate_analyst_agent()
        except Exception as e:
            self.manager.logger.error(f"Analyst agent generation failed: {e}")
            return self.get_fallback_template()
    
    def _generate_analyst_agent(self) -> str:
        """Generate comprehensive analyst agent."""
        return '''"""
Analyst Agent - Converts requirements into structured user stories and specifications.
"""

import json
import re
from typing import Dict, Any, List
from .base_agent import BaseAgent

class AnalystAgent(BaseAgent):
    """
    Analyzes project requirements and converts them into structured specifications.
    """
    
    def __init__(self, llm_client, database, logger):
        super().__init__(llm_client, database, logger, "analyst")
        
        # Analysis configuration
        self.max_user_stories = 20
        self.min_acceptance_criteria = 3
        self.priority_levels = ["High", "Medium", "Low"]
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate analyst input data."""
        required_fields = ['requirements', 'project_id']
        return all(field in input_data for field in required_fields)
    
    def validate_output(self, output_data: Dict[str, Any]) -> bool:
        """Validate analyst output structure."""
        if output_data.get('status') == 'error':
            return True  # Error responses are valid
        
        required_fields = ['user_stories', 'technical_requirements', 'stakeholders']
        return all(field in output_data for field in required_fields)
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process requirements into structured specifications."""
        
        requirements = input_data['requirements']
        project_id = input_data['project_id']
        
        self.logger.info(f"Analyzing requirements for project {project_id}")
        
        # Generate user stories
        user_stories = await self._generate_user_stories(requirements)
        
        # Extract technical requirements
        technical_requirements = await self._extract_technical_requirements(requirements)
        
        # Identify stakeholders
        stakeholders = await self._identify_stakeholders(requirements)
        
        # Assess complexity and effort
        complexity_assessment = await self._assess_complexity(user_stories, technical_requirements)
        
        # Generate acceptance criteria
        acceptance_criteria = await self._generate_acceptance_criteria(user_stories)
        
        return {
            'agent_type': 'analyst',
            'status': 'completed',
            'project_id': project_id,
            'user_stories': user_stories,
            'technical_requirements': technical_requirements,
            'stakeholders': stakeholders,
            'complexity_assessment': complexity_assessment,
            'acceptance_criteria': acceptance_criteria,
            'recommendations': await self._generate_recommendations(
                user_stories, technical_requirements, complexity_assessment
            )
        }
    
    async def _generate_user_stories(self, requirements: str) -> List[Dict[str, Any]]:
        """Generate user stories from requirements."""
        
        prompt = f"""
Analyze the following project requirements and create detailed user stories:

Requirements:
{requirements}

Create user stories in the following JSON format:
[
  {{
    "id": "US001",
    "title": "Brief story title",
    "description": "As a [user type], I want [goal] so that [benefit]",
    "priority": "High/Medium/Low",
    "story_points": 1-13,
    "epic": "Epic category name",
    "acceptance_criteria": [
      "Given [context], when [action], then [outcome]"
    ]
  }}
]

Focus on:
- Clear user personas and roles
- Specific, testable outcomes
- Appropriate story sizing
- Logical epic groupings

Generate 5-15 comprehensive user stories that cover all requirements.
Return ONLY valid JSON.
"""
        
        response = await self.llm_client.generate(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.1
        )
        
        try:
            user_stories = json.loads(response.strip())
            
            # Validate structure
            if not isinstance(user_stories, list):
                raise ValueError("User stories must be a list")
            
            # Ensure required fields
            for story in user_stories:
                if not all(field in story for field in ['id', 'title', 'description', 'priority']):
                    raise ValueError("Missing required user story fields")
            
            self.logger.info(f"Generated {len(user_stories)} user stories")
            return user_stories
            
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Failed to parse user stories: {e}")
            return self._get_fallback_user_stories()
    
    async def _extract_technical_requirements(self, requirements: str) -> Dict[str, Any]:
        """Extract technical requirements and constraints."""
        
        prompt = f"""
Extract technical requirements from the project requirements:

Requirements:
{requirements}

Identify and categorize technical requirements in JSON format:
{{
  "functional_requirements": [
    "Specific functional requirement"
  ],
  "non_functional_requirements": {{
    "performance": ["Performance requirements"],
    "security": ["Security requirements"],
    "scalability": ["Scalability requirements"],
    "usability": ["Usability requirements"]
  }},
  "constraints": {{
    "technology": ["Technology constraints"],
    "budget": ["Budget constraints"],
    "timeline": ["Timeline constraints"],
    "compliance": ["Compliance requirements"]
  }},
  "integrations": [
    {{
      "system": "External system name",
      "type": "API/Database/File/etc",
      "description": "Integration description"
    }}
  ]
}}

Return ONLY valid JSON.
"""
        
        response = await self.llm_client.generate(
            prompt=prompt,
            max_tokens=1500,
            temperature=0.1
        )
        
        try:
            technical_reqs = json.loads(response.strip())
            self.logger.info("Extracted technical requirements")
            return technical_reqs
            
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse technical requirements")
            return self._get_fallback_technical_requirements()
    
    async def _identify_stakeholders(self, requirements: str) -> List[Dict[str, Any]]:
        """Identify project stakeholders and their roles."""
        
        prompt = f"""
Identify stakeholders from the project requirements:

Requirements:
{requirements}

List stakeholders in JSON format:
[
  {{
    "role": "Stakeholder role/title",
    "type": "Primary/Secondary/Key",
    "responsibilities": ["List of responsibilities"],
    "influence": "High/Medium/Low",
    "involvement": "Daily/Weekly/Monthly/As-needed"
  }}
]

Include typical roles like:
- End users
- Business owners
- IT administrators
- Compliance officers
- External partners

Return ONLY valid JSON.
"""
        
        response = await self.llm_client.generate(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.1
        )
        
        try:
            stakeholders = json.loads(response.strip())
            self.logger.info(f"Identified {len(stakeholders)} stakeholder groups")
            return stakeholders
            
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse stakeholders")
            return self._get_fallback_stakeholders()
    
    async def _assess_complexity(self, user_stories: List[Dict], 
                                technical_requirements: Dict) -> Dict[str, Any]:
        """Assess project complexity and effort estimation."""
        
        total_story_points = sum(story.get('story_points', 5) for story in user_stories)
        num_integrations = len(technical_requirements.get('integrations', []))
        num_nfr = sum(len(reqs) for reqs in technical_requirements.get('non_functional_requirements', {}).values())
        
        # Simple complexity scoring
        complexity_score = total_story_points + (num_integrations * 3) + (num_nfr * 2)
        
        if complexity_score < 30:
            complexity_level = "Low"
            estimated_weeks = 2-4
        elif complexity_score < 80:
            complexity_level = "Medium" 
            estimated_weeks = 4-8
        else:
            complexity_level = "High"
            estimated_weeks = 8-16
        
        return {
            'overall_complexity': complexity_level,
            'complexity_score': complexity_score,
            'estimated_effort_weeks': f"{estimated_weeks[0]}-{estimated_weeks[1]}",
            'story_points_total': total_story_points,
            'risk_factors': [
                'Multiple integrations required' if num_integrations > 3 else None,
                'Complex non-functional requirements' if num_nfr > 10 else None,
                'Large number of user stories' if len(user_stories) > 15 else None
            ],
            'recommendations': [
                'Consider phased delivery approach' if complexity_level == "High" else None,
                'Prototype key integrations early' if num_integrations > 2 else None,
                'Establish clear acceptance criteria' if total_story_points > 50 else None
            ]
        }
    
    async def _generate_acceptance_criteria(self, user_stories: List[Dict]) -> Dict[str, List[str]]:
        """Generate additional acceptance criteria for user stories."""
        
        criteria_map = {}
        for story in user_stories:
            story_id = story['id']
            existing_criteria = story.get('acceptance_criteria', [])
            
            if len(existing_criteria) < self.min_acceptance_criteria:
                # Generate additional criteria using LLM
                additional_criteria = await self._generate_additional_criteria(story)
                criteria_map[story_id] = existing_criteria + additional_criteria
            else:
                criteria_map[story_id] = existing_criteria
        
        return criteria_map
    
    async def _generate_additional_criteria(self, story: Dict) -> List[str]:
        """Generate additional acceptance criteria for a user story."""
        
        prompt = f"""
Generate additional acceptance criteria for this user story:

Title: {story['title']}
Description: {story['description']}
Existing Criteria: {story.get('acceptance_criteria', [])}

Generate 2-3 additional acceptance criteria in the format:
"Given [context], when [action], then [outcome]"

Focus on:
- Edge cases and error handling
- User experience considerations
- Data validation requirements
- Performance expectations

Return as a JSON array of strings.
"""
        
        try:
            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=500,
                temperature=0.2
            )
            
            additional_criteria = json.loads(response.strip())
            return additional_criteria if isinstance(additional_criteria, list) else []
            
        except Exception:
            # Fallback criteria
            return [
                f"Given invalid input, when user submits data, then appropriate error message is displayed",
                f"Given successful completion, when user performs action, then confirmation is provided"
            ]
    
    async def _generate_recommendations(self, user_stories: List[Dict], 
                                      technical_requirements: Dict,
                                      complexity_assessment: Dict) -> List[str]:
        """Generate project recommendations."""
        
        recommendations = []
        
        # Based on complexity
        if complexity_assessment['overall_complexity'] == "High":
            recommendations.extend([
                "Consider MVP approach with phased delivery",
                "Establish clear milestone checkpoints",
                "Plan for additional testing phases"
            ])
        
        # Based on integrations
        integrations = technical_requirements.get('integrations', [])
        if len(integrations) > 2:
            recommendations.append("Prototype key integrations early to validate feasibility")
        
        # Based on user stories
        high_priority_stories = [s for s in user_stories if s.get('priority') == 'High']
        if len(high_priority_stories) > 10:
            recommendations.append("Consider breaking high-priority features into smaller releases")
        
        # Generic recommendations
        recommendations.extend([
            "Establish regular stakeholder review sessions",
            "Implement continuous integration/deployment pipeline",
            "Plan for comprehensive user acceptance testing"
        ])
        
        return recommendations
    
    def _get_fallback_user_stories(self) -> List[Dict[str, Any]]:
        """Fallback user stories if generation fails."""
        return [
            {
                "id": "US001",
                "title": "Basic user access",
                "description": "As a user, I want to access the system so that I can use its features",
                "priority": "High",
                "story_points": 3,
                "epic": "Core Functionality"
            }
        ]
    
    def _get_fallback_technical_requirements(self) -> Dict[str, Any]:
        """Fallback technical requirements."""
        return {
            "functional_requirements": ["Basic system functionality"],
            "non_functional_requirements": {
                "performance": ["System should respond within 3 seconds"],
                "security": ["User authentication required"],
                "scalability": ["Support concurrent users"],
                "usability": ["Intuitive user interface"]
            },
            "constraints": {
                "technology": ["Web-based application"],
                "budget": ["Cost-effective solution"],
                "timeline": ["Reasonable development timeline"]
            },
            "integrations": []
        }
    
    def _get_fallback_stakeholders(self) -> List[Dict[str, Any]]:
        """Fallback stakeholders list."""
        return [
            {
                "role": "End Users",
                "type": "Primary",
                "responsibilities": ["Use the system", "Provide feedback"],
                "influence": "High",
                "involvement": "Daily"
            },
            {
                "role": "Project Owner",
                "type": "Key",
                "responsibilities": ["Define requirements", "Make decisions"],
                "influence": "High",
                "involvement": "Weekly"
            }
        ]
    
    def get_fallback_template(self) -> str:
        """Get fallback analyst agent template."""
        return '''"""
Fallback Analyst Agent with basic functionality.
"""

from .base_agent import BaseAgent

class AnalystAgent(BaseAgent):
    def __init__(self, llm_client, database, logger):
        super().__init__(llm_client, database, logger, "analyst")
    
    def validate_input(self, input_data):
        return 'requirements' in input_data
    
    def validate_output(self, output_data):
        return 'user_stories' in output_data or 'status' in output_data
    
    async def process(self, input_data):
        return {
            'agent_type': 'analyst',
            'status': 'completed',
            'user_stories': [],
            'message': 'Fallback processing mode'
        }
'''
