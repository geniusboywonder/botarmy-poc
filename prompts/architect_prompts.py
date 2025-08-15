"""
Architect Agent prompt templates for technical design and architecture decisions.
"""

ARCHITECT_PROMPTS = {
    "analyze_requirements": """
You are a senior software architect analyzing user requirements to extract technical specifications.

USER STORIES:
{user_stories}

FUNCTIONAL REQUIREMENTS:
{functional_requirements}

NON-FUNCTIONAL REQUIREMENTS:  
{non_functional_requirements}

CONSTRAINTS:
{constraints}

Analyze these requirements and provide a structured technical analysis in JSON format:

{{
  "core_features": ["feature1", "feature2", ...],
  "integration_points": ["system1", "system2", ...],
  "data_requirements": {{
    "storage_type": "relational|document|graph|file",
    "data_volume": "small|medium|large",
    "consistency_needs": "eventual|strong",
    "backup_requirements": "daily|weekly|none"
  }},
  "performance_requirements": {{
    "response_time": "< Xs",
    "concurrent_users": "< N users",
    "throughput": "< N req/sec",
    "availability": "99.X%"
  }},
  "security_requirements": {{
    "authentication": "required|optional|none",
    "authorization": "role_based|attribute_based|none", 
    "data_encryption": "required|optional|none",
    "audit_logging": "required|optional|none"
  }},
  "scalability_needs": {{
    "initial_scale": "single_server|multi_server|distributed",
    "growth_pattern": "linear|exponential|seasonal",
    "bottlenecks": ["cpu", "memory", "storage", "network"]
  }},
  "ui_complexity": "low|medium|high",
  "backend_complexity": "low|medium|high"
}}

Focus on extracting concrete, measurable requirements. Be specific about performance numbers and scalability needs.
""",

    "select_tech_stack": """
You are a senior software architect selecting the optimal technology stack for a project.

TECHNICAL ANALYSIS:
{technical_analysis}

AVAILABLE TECHNOLOGY OPTIONS:
{available_stacks}

PROJECT CONSTRAINTS:
{constraints}

Select the most appropriate technology stack and provide justification in JSON format:

{{
  "frontend": "react|vue|angular|svelte|vanilla",
  "backend": "fastapi|express|spring|django|flask",
  "database": "postgresql|mysql|mongodb|sqlite|redis",
  "styling": "tailwindcss|bootstrap|material-ui|styled-components",
  "deployment": "replit|railway|vercel|heroku|aws",
  "real_time": "websockets|sse|polling|none",
  "testing": "pytest|jest|cypress|selenium",
  "justification": {{
    "frontend": "reason for frontend choice",
    "backend": "reason for backend choice", 
    "database": "reason for database choice",
    "deployment": "reason for deployment choice"
  }},
  "alternatives": {{
    "frontend": ["alt1", "alt2"],
    "backend": ["alt1", "alt2"],
    "deployment": ["alt1", "alt2"]
  }},
  "trade_offs": {{
    "performance": "impact on performance",
    "complexity": "impact on complexity",
    "cost": "impact on cost",
    "scalability": "impact on scalability"
  }}
}}

Prioritize free, open-source, lightweight solutions suitable for rapid POC development.
""",

    "design_architecture": """
You are a senior software architect designing the system architecture for a web application.

TECHNICAL ANALYSIS:
{technical_analysis}

SELECTED TECHNOLOGY STACK:
{technology_stack}

KEY USER STORIES:
{user_stories}

Design a high-level system architecture and provide detailed specifications in JSON format:

{{
  "pattern": "layered|microservices|mvc|hexagonal|clean",
  "components": [
    {{
      "name": "component_name",
      "purpose": "component purpose", 
      "responsibilities": ["responsibility1", "responsibility2"],
      "interfaces": ["interface1", "interface2"],
      "dependencies": ["dependency1", "dependency2"]
    }}
  ],
  "data_flow": [
    {{
      "from": "source_component",
      "to": "destination_component", 
      "data": "data_description",
      "protocol": "REST|GraphQL|WebSocket|SSE"
    }}
  ],
  "api_design": {{
    "style": "REST|GraphQL|RPC",
    "versioning": "url|header|query",
    "format": "JSON|XML|MessagePack",
    "authentication": "JWT|API_Key|OAuth|Session"
  }},
  "security_layers": [
    {{
      "layer": "input_validation|authentication|authorization|encryption",
      "implementation": "specific implementation approach",
      "tools": ["tool1", "tool2"]
    }}
  ],
  "deployment": {{
    "architecture": "single_server|multi_server|serverless|container",
    "scalability": "vertical|horizontal|auto_scaling",
    "load_balancing": "required|optional|none",
    "caching": "redis|memcached|cdn|none"
  }},
  "monitoring": {{
    "logging": "structured|unstructured|none",
    "metrics": "prometheus|datadog|custom|none", 
    "alerting": "email|slack|webhook|none",
    "health_checks": "endpoint|script|external"
  }}
}}

Focus on simplicity and rapid development while maintaining good architectural principles.
""",

    "create_file_structure": """
You are a senior software architect creating the optimal file and folder structure for a project.

SYSTEM ARCHITECTURE:
{architecture}

TECHNOLOGY STACK:
{tech_stack}

PROJECT TYPE:
{project_type}

Create a comprehensive file and folder structure in JSON format:

{{
  "root_files": [
    {{
      "filename": "README.md",
      "purpose": "Project documentation and setup instructions"
    }},
    {{
      "filename": "requirements.txt", 
      "purpose": "Python dependencies"
    }}
  ],
  "backend": {{
    "main.py": "FastAPI application entry point",
    "config.py": "Configuration and environment variables",
    "database.py": "Database connection and operations",
    "agents/": {{
      "__init__.py": "Package initialization",
      "base_agent.py": "Base agent class with common functionality",
      "analyst_agent.py": "Requirements analysis agent",
      "architect_agent.py": "Technical architecture agent",
      "developer_agent.py": "Code generation agent",
      "tester_agent.py": "Quality assurance agent"
    }},
    "workflow/": {{
      "__init__.py": "Package initialization", 
      "pipeline.py": "Agent orchestration and workflow management",
      "state_manager.py": "Workflow state tracking"
    }},
    "prompts/": {{
      "__init__.py": "Package initialization",
      "analyst_prompts.py": "Analyst agent prompt templates",
      "architect_prompts.py": "Architect agent prompt templates"
    }}
  }},
  "frontend": {{
    "src/": {{
      "App.jsx": "Main React application component",
      "index.js": "Application entry point",
      "components/": {{
        "Dashboard.jsx": "Main dashboard layout",
        "AgentPanel.jsx": "Agent status and conversation display", 
        "ActionQueue.jsx": "Human intervention queue",
        "ProjectViewer.jsx": "Project files and specification viewer",
        "StatusBar.jsx": "System health and progress monitoring"
      }},
      "context/": {{
        "AppContext.js": "Global application state management"
      }},
      "utils/": {{
        "api.js": "API client utilities",
        "formatting.js": "Data formatting helpers"
      }}
    }},
    "public/": {{
      "index.html": "HTML template",
      "favicon.ico": "Application icon"
    }},
    "package.json": "Node.js dependencies and scripts"
  }},
  "config": [
    {{
      "filename": ".env.example",
      "purpose": "Environment variable template"
    }},
    {{
      "filename": "replit.nix", 
      "purpose": "Replit environment configuration"
    }}
  ],
  "docs": [
    {{
      "filename": "API.md",
      "purpose": "API documentation"
    }},
    {{
      "filename": "DEPLOYMENT.md",
      "purpose": "Deployment instructions"
    }}
  ],
  "tests": {{
    "unit/": {{
      "test_agents.py": "Agent unit tests",
      "test_api.py": "API endpoint tests"
    }},
    "integration/": {{
      "test_workflow.py": "Workflow integration tests",
      "test_database.py": "Database integration tests"
    }},
    "conftest.py": "Pytest configuration and fixtures"
  }}
}}

Ensure the structure supports clean separation of concerns, easy testing, and scalable development.
"""
}