"""
Developer Agent prompts for generating working code implementations.
"""

DEVELOPER_PROMPTS = {
    "create_generation_plan": """
You are an expert software developer creating a code generation plan based on architectural specifications.

Given the following specifications:

Architecture:
{architecture}

Technology Stack:
{tech_stack}

File Structure:
{file_structure}

Technical Specifications:
{specifications}

Create a comprehensive generation plan that includes:

1. Generation order (which files to create first based on dependencies)
2. Dependencies between components
3. Complexity assessment (low/medium/high)
4. Estimated number of files to generate
5. Critical components that need special attention
6. Integration points between frontend and backend
7. Testing strategy for generated code

Return your response as a JSON object with this structure:
{{
    "generation_order": ["file1.py", "file2.jsx", ...],
    "dependencies": {{
        "component1": ["dependency1", "dependency2"],
        ...
    }},
    "complexity": "medium",
    "estimated_files": 15,
    "critical_components": ["database.py", "main.py", "App.jsx"],
    "integration_points": [
        {{
            "component": "API endpoints",
            "frontend": "src/utils/api.js",
            "backend": "main.py"
        }}
    ],
    "testing_strategy": {{
        "unit_tests": ["test files to create"],
        "integration_tests": ["integration scenarios"],
        "e2e_tests": ["end-to-end scenarios"]
    }}
}}

Focus on creating working, production-ready code that follows best practices.
""",

    "fastapi_main": """
You are an expert Python developer creating a FastAPI application.

Create a complete main.py file for a FastAPI application with the following requirements:

API Endpoints:
{api_endpoints}

Architecture:
{architecture}

The application should include:
1. FastAPI app initialization with CORS middleware
2. All required API endpoints for agent management
3. Server-Sent Events endpoint for real-time updates
4. File upload/download endpoints
5. Static file serving for React frontend
6. Proper error handling and logging
7. Database connection management
8. Agent workflow integration

Create a complete, working FastAPI application file that follows best practices.
Include proper imports, error handling, and documentation.
""",

    "database_module": """
You are an expert Python developer creating a database module for SQLite operations.

Create a complete database.py file with the following schema:
{schema}

The module should include:
1. SQLite database connection and initialization
2. All table creation with proper indexes
3. CRUD operations for all entities (projects, messages, agents, conflicts, files)
4. Database migration support
5. Connection pooling and error handling
6. Async/await support for operations
7. Proper logging and transaction management
8. Backup and recovery functions

Create a complete, working database module that follows best practices.
Include proper error handling, logging, and async support.
""",

    "react_component": """
You are an expert React developer creating a component for the BotArmy application.

Create a complete React component for: {component_name}

Component Requirements:
{component_specs}

The component should include:
1. Proper React hooks for state management
2. Responsive design with Tailwind CSS
3. Real-time data updates
4. Error handling and loading states
5. Accessibility features (ARIA labels, keyboard navigation)
6. Professional UI/UX design
7. Integration with AppContext for global state

Create a complete, working React component that follows best practices.
Include proper imports, state management, and styling.
""",

    "generate_requirements": """
Create a complete requirements.txt file for a Python FastAPI application with the following features:
- FastAPI with async support
- SQLite database operations
- OpenAI API integration
- CORS middleware
- File upload handling
- Logging and configuration
- Development tools

Include specific version numbers for stability and list all necessary dependencies.
""",

    "generate_package_json": """
Create a complete package.json file for a React application with the following requirements:

Technology Stack:
{tech_stack}

The package.json should include:
1. React 18+ with modern hooks
2. Tailwind CSS for styling
3. Vite for build tooling
4. Development dependencies
5. Build and development scripts
6. ESLint and Prettier configuration
7. Testing frameworks

Include proper version numbers and all necessary dependencies for a production-ready React application.
""",

    "generate_dockerfile": """
Create a complete Dockerfile for a Python FastAPI application with React frontend.

The Dockerfile should:
1. Use official Python 3.9+ base image
2. Install system dependencies
3. Copy and install Python requirements
4. Install Node.js for React build
5. Copy and build React frontend
6. Expose appropriate ports
7. Set up proper working directory
8. Include health checks
9. Run with proper user permissions

Create a production-ready Dockerfile that follows best practices.
""",

    "generate_readme": """
Create a comprehensive README.md file for the BotArmy POC project.

Project Details:
Architecture: {architecture}
Technology Stack: {tech_stack}
Generation Plan: {plan}

The README should include:
1. Project overview and purpose
2. Features and capabilities
3. Technology stack and requirements
4. Installation and setup instructions
5. Usage guide with examples
6. API documentation overview
7. Development workflow
8. Deployment instructions
9. Troubleshooting guide
10. Contributing guidelines

Create a professional, comprehensive README that makes it easy for developers to understand and use the project.
""",

    "generate_api_docs": """
Create comprehensive API documentation in Markdown format.

Analyze the following backend files to extract API endpoints:
{backend_files}

Create documentation that includes:
1. API overview and base URL
2. Authentication requirements
3. All endpoints with HTTP methods
4. Request/response formats with examples
5. Error codes and messages
6. Rate limiting information
7. WebSocket/SSE endpoints
8. Integration examples

Format as a professional API documentation that developers can easily follow.
""",

    "code_quality_check": """
You are an expert code reviewer performing quality analysis on generated code files.

Analyze the following code files for:
1. Syntax correctness
2. Security vulnerabilities
3. Performance issues
4. Best practices compliance
5. Documentation completeness
6. Error handling adequacy
7. Code organization and structure

Files to analyze:
{code_files}

Return a detailed quality report with:
- Critical issues that must be fixed
- Warnings and recommendations
- Security concerns
- Performance suggestions
- Overall quality score (0-1)
- Specific file-by-file feedback

Provide actionable feedback for improving code quality.
""",

    "generate_tests": """
Create comprehensive test files for the following code:

Code Files:
{code_files}

Testing Strategy:
{testing_strategy}

Generate test files that include:
1. Unit tests for all functions and classes
2. Integration tests for API endpoints
3. Frontend component tests
4. Database operation tests
5. Error handling tests
6. Mock configurations
7. Test data fixtures
8. Coverage configuration

Create complete, working test suites that ensure code quality and reliability.
""",

    "deployment_optimization": """
Optimize the generated code for deployment on the specified platform.

Platform: {platform}
Code Files: {code_files}

Provide optimizations for:
1. Performance improvements
2. Memory usage reduction
3. Database query optimization
4. Frontend bundle size reduction
5. Caching strategies
6. Error handling improvements
7. Logging and monitoring setup
8. Security hardening

Return optimized code versions and deployment recommendations.
"""
}

# Specialized prompts for specific file types
FASTAPI_TEMPLATES = {
    "main_app": """
Create a FastAPI main.py with:
- CORS middleware configuration
- Static file serving for React
- All API routes properly organized
- Error handling middleware
- Logging configuration
- Database connection lifecycle
- Real-time SSE endpoint
""",

    "api_router": """
Create an API router module with:
- RESTful endpoint design
- Proper request/response models
- Async operation support
- Error handling
- Input validation
- Documentation strings
""",

    "database_operations": """
Create database operations with:
- SQLite async operations
- Connection pooling
- Transaction management
- Error handling
- Index optimization
- Migration support
"""
}

REACT_TEMPLATES = {
    "component_structure": """
Create React component with:
- Functional component with hooks
- TypeScript-like prop validation
- Responsive Tailwind CSS design
- Accessibility features
- Error boundaries
- Loading states
- Real-time data integration
""",

    "context_provider": """
Create React context with:
- Global state management
- Local storage persistence
- SSE integration
- Action creators
- State validation
- Performance optimization
""",

    "utility_functions": """
Create utility modules with:
- API client functions
- Data formatting helpers
- Error handling utilities
- Validation functions
- Common constants
- Type definitions
"""
}

# Quality check templates
QUALITY_TEMPLATES = {
    "security_check": """
Perform security analysis for:
- SQL injection vulnerabilities
- XSS prevention
- CSRF protection
- Input validation
- Authentication/authorization
- Secrets management
- HTTPS enforcement
""",

    "performance_check": """
Analyze performance aspects:
- Database query optimization
- API response times
- Frontend bundle size
- Memory usage patterns
- Caching opportunities
- Load balancing considerations
""",

    "best_practices": """
Verify best practices compliance:
- Code organization
- Error handling patterns
- Logging standards
- Documentation quality
- Testing coverage
- Configuration management
"""
}
