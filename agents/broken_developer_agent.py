        
        # Add specific notes based on requirements
        if quality_results.get("total_errors", 0) == 0:
            notes.append("Generated code passes all syntax and basic quality checks")
        
        if quality_results.get("security_issues", 0) == 0:
            notes.append("No security vulnerabilities detected in generated code")
        
        tech_stack = requirements.get("technology_stack", {})
        if tech_stack.get("frontend") == "React":
            notes.append("React components follow modern hooks patterns and best practices")
        
        if tech_stack.get("backend") == "FastAPI":
            notes.append("FastAPI implementation includes async endpoints and proper validation")
        
        return notes

    def _create_next_steps(self, quality_results: Dict, validation_results: Dict) -> List[str]:
        """Create next steps based on quality and validation results."""
        
        steps = []
        
        # Address quality issues first
        if quality_results.get("total_errors", 0) > 0:
            steps.append("Review and fix critical errors identified in quality report")
        
        if quality_results.get("total_warnings", 0) > 5:
            steps.append("Address warnings to improve code maintainability")
        
        # Validation issues
        if not validation_results.get("valid", True):
            steps.append("Complete missing required files and configurations")
        
        # Standard next steps
        steps.extend([
            "Run comprehensive testing with Tester agent",
            "Deploy to development environment for manual testing",
            "Perform security review and penetration testing",
            "Set up monitoring and alerting",
            "Create user documentation and training materials",
            "Deploy to production environment"
        ])
        
        return steps

    # Placeholder methods for templates (these would contain actual template code)
    def _get_fastapi_templates(self) -> Dict:
        return {"main": "", "router": "", "middleware": ""}
    
    def _get_react_templates(self) -> Dict:
        return {"component": "", "hook": "", "context": ""}
    
    def _get_database_templates(self) -> Dict:
        return {"schema": "", "migration": "", "operations": ""}
    
    def _create_default_generation_plan(self) -> Dict:
        """Create a default generation plan when LLM fails to provide one."""
        return {
            "generation_order": ["backend", "frontend", "config", "docs"],
            "dependencies": {},
            "complexity_assessment": "medium",
            "estimated_files": 15,
            "critical_components": ["main.py", "src/App.jsx"],
            "integration_points": ["api_endpoints", "database"],
            "testing_strategy": {"unit": True, "integration": True}
        }
