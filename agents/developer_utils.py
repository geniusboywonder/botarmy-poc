"""
Utility functions for the developer agent.
"""

import re
import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import ast
import os

def extract_project_requirements(architect_output: Dict[str, Any]) -> Dict[str, Any]:
    """Extract development-relevant requirements from architect output."""
    
    requirements = {
        "technology_stack": architect_output.get("technology_stack", {}),
        "architecture_patterns": architect_output.get("architecture_patterns", []),
        "database_schema": architect_output.get("database_schema", {}),
        "api_endpoints": architect_output.get("api_endpoints", []),
        "ui_components": architect_output.get("ui_components", []),
        "security_requirements": architect_output.get("security_requirements", []),
        "performance_requirements": architect_output.get("performance_requirements", {}),
        "deployment_requirements": architect_output.get("deployment_requirements", {})
    }
    
    return requirements

def generate_file_structure(requirements: Dict[str, Any]) -> Dict[str, List[str]]:
    """Generate file structure based on requirements."""
    
    structure = {
        "backend": [],
        "frontend": [],
        "database": [],
        "config": [],
        "docs": []
    }
    
    # Backend files
    tech_stack = requirements.get("technology_stack", {})
    if tech_stack.get("backend") == "FastAPI":
        structure["backend"].extend([
            "main.py",
            "config.py", 
            "database.py",
            "llm_client.py"
        ])
        
        # Add agent files
        structure["backend"].extend([
            "agents/base_agent.py",
            "agents/analyst_agent.py",
            "agents/architect_agent.py", 
            "agents/developer_agent.py",
            "agents/tester_agent.py"
        ])
        
        # Add workflow files
        structure["backend"].extend([
            "workflow/pipeline.py",
            "workflow/state_manager.py"
        ])
    
    # Frontend files
    if tech_stack.get("frontend") == "React":
        structure["frontend"].extend([
            "src/App.jsx",
            "src/main.jsx",
            "src/index.css",
            "index.html",
            "package.json",
            "vite.config.js",
            "tailwind.config.js"
        ])
        
        # Add component files
        ui_components = requirements.get("ui_components", [])
        for component in ui_components:
            structure["frontend"].append(f"src/components/{component}.jsx")
        
        # Add context and utilities
        structure["frontend"].extend([
            "src/context/AppContext.js",
            "src/utils/api.js",
            "src/utils/formatting.js"
        ])
    
    # Database files
    database_schema = requirements.get("database_schema", {})
    if database_schema:
        structure["database"].extend([
            "schema.sql",
            "migrations/001_initial.sql"
        ])
    
    # Configuration files
    structure["config"].extend([
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "README.md"
    ])
    
    return structure

def calculate_code_complexity(code: str, language: str = "python") -> int:
    """Calculate cyclomatic complexity of code."""
    
    if language.lower() == "python":
        return _calculate_python_complexity(code)
    elif language.lower() in ["javascript", "jsx"]:
        return _calculate_js_complexity(code)
    else:
        return 1  # Default complexity

def _calculate_python_complexity(code: str) -> int:
    """Calculate Python code complexity."""
    
    complexity = 1  # Base complexity
    
    # Count decision points
    decision_points = [
        r'\bif\b', r'\belif\b', r'\bfor\b', r'\bwhile\b',
        r'\btry\b', r'\bexcept\b', r'\band\b', r'\bor\b',
        r'\?\s*:', r'lambda'
    ]
    
    for pattern in decision_points:
        complexity += len(re.findall(pattern, code))
    
    return complexity

def _calculate_js_complexity(code: str) -> int:
    """Calculate JavaScript code complexity."""
    
    complexity = 1  # Base complexity
    
    # Count decision points
    decision_points = [
        r'\bif\b', r'\bfor\b', r'\bwhile\b', r'\bdo\b',
        r'\btry\b', r'\bcatch\b', r'&&', r'\|\|',
        r'\?\s*:', r'=>'
    ]
    
    for pattern in decision_points:
        complexity += len(re.findall(pattern, code))
    
    return complexity

def validate_imports(code: str, language: str = "python") -> List[str]:
    """Validate that all imports are used."""
    
    if language.lower() == "python":
        return _validate_python_imports(code)
    elif language.lower() in ["javascript", "jsx"]:
        return _validate_js_imports(code)
    else:
        return []

def _validate_python_imports(code: str) -> List[str]:
    """Check for unused Python imports."""
    
    unused_imports = []
    
    # Extract imports
    import_pattern = r'(?:from\s+(\w+)\s+import\s+([^#\n]+)|import\s+([^#\n]+))'
    imports = re.findall(import_pattern, code)
    
    for match in imports:
        if match[0]:  # from ... import ...
            module = match[0]
            items = [item.strip() for item in match[1].split(',')]
        else:  # import ...
            items = [item.strip() for item in match[2].split(',')]
            module = None
        
        for item in items:
            item = item.split(' as ')[0].strip()  # Handle 'as' aliases
            if not re.search(rf'\b{re.escape(item)}\b', code.replace(match[0] or match[2], '')):
                unused_imports.append(item)
    
    return unused_imports

def _validate_js_imports(code: str) -> List[str]:
    """Check for unused JavaScript imports."""
    
    unused_imports = []
    
    # Extract ES6 imports
    import_patterns = [
        r'import\s+(\w+)\s+from',  # default import
        r'import\s*{\s*([^}]+)\s*}\s*from',  # named imports
        r'import\s*\*\s*as\s*(\w+)\s*from'  # namespace import
    ]
    
    for pattern in import_patterns:
        matches = re.findall(pattern, code)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            
            if ',' in match:  # Multiple named imports
                items = [item.strip() for item in match.split(',')]
            else:
                items = [match.strip()]
            
            for item in items:
                item = item.split(' as ')[0].strip()
                if not re.search(rf'\b{re.escape(item)}\b', code):
                    unused_imports.append(item)
    
    return unused_imports

def generate_code_hash(code: str) -> str:
    """Generate hash for code content for version tracking."""
    
    return hashlib.sha256(code.encode('utf-8')).hexdigest()[:16]

def extract_functions(code: str, language: str = "python") -> List[Dict[str, Any]]:
    """Extract function definitions from code."""
    
    if language.lower() == "python":
        return _extract_python_functions(code)
    elif language.lower() in ["javascript", "jsx"]:
        return _extract_js_functions(code)
    else:
        return []

def _extract_python_functions(code: str) -> List[Dict[str, Any]]:
    """Extract Python function definitions."""
    
    functions = []
    
    # Function definition pattern
    func_pattern = r'def\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*([^:]+))?:'
    matches = re.finditer(func_pattern, code)
    
    for match in matches:
        func_name = match.group(1)
        params = match.group(2).strip()
        return_type = match.group(3).strip() if match.group(3) else None
        
        # Extract docstring
        lines = code[match.end():].split('\n')
        docstring = None
        if lines and '"""' in lines[0]:
            # Try to extract docstring
            docstring_lines = []
            in_docstring = False
            for line in lines[1:]:
                if '"""' in line and not in_docstring:
                    in_docstring = True
                    if line.strip() != '"""':
                        docstring_lines.append(line.strip('"""').strip())
                elif '"""' in line and in_docstring:
                    docstring_lines.append(line.strip('"""').strip())
                    break
                elif in_docstring:
                    docstring_lines.append(line.strip())
            
            if docstring_lines:
                docstring = '\n'.join(docstring_lines).strip()
        
        functions.append({
            "name": func_name,
            "parameters": params,
            "return_type": return_type,
            "docstring": docstring,
            "line": code[:match.start()].count('\n') + 1
        })
    
    return functions

def _extract_js_functions(code: str) -> List[Dict[str, Any]]:
    """Extract JavaScript function definitions."""
    
    functions = []
    
    # Function patterns
    patterns = [
        r'function\s+(\w+)\s*\(([^)]*)\)\s*{',  # function declaration
        r'const\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>\s*{',  # arrow function
        r'(\w+)\s*:\s*function\s*\(([^)]*)\)\s*{'  # method definition
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, code)
        for match in matches:
            func_name = match.group(1)
            params = match.group(2).strip() if len(match.groups()) > 1 else ""
            
            functions.append({
                "name": func_name,
                "parameters": params,
                "type": "function",
                "line": code[:match.start()].count('\n') + 1
            })
    
    return functions

def format_code_output(files: Dict[str, str], quality_results: Dict[str, Any]) -> Dict[str, Any]:
    """Format the developer agent output."""
    
    output = {
        "generated_files": [],
        "file_structure": {},
        "quality_summary": {
            "overall_score": quality_results.get("overall_score", 0),
            "total_errors": quality_results.get("total_errors", 0),
            "total_warnings": quality_results.get("total_warnings", 0),
            "recommendations": quality_results.get("recommendations", [])
        },
        "metrics": {
            "total_files": len(files),
            "total_lines": 0,
            "total_functions": 0,
            "languages_used": []
        },
        "deployment_ready": quality_results.get("overall_score", 0) > 70
    }
    
    # Process each file
    for filepath, content in files.items():
        file_info = {
            "path": filepath,
            "size": len(content),
            "lines": len(content.split('\n')),
            "hash": generate_code_hash(content),
            "language": _detect_language(filepath),
            "functions": []
        }
        
        # Extract functions
        language = _detect_language(filepath)
        if language in ["python", "javascript", "jsx"]:
            file_info["functions"] = extract_functions(content, language)
            output["metrics"]["total_functions"] += len(file_info["functions"])
        
        output["generated_files"].append(file_info)
        output["metrics"]["total_lines"] += file_info["lines"]
        
        if language not in output["metrics"]["languages_used"]:
            output["metrics"]["languages_used"].append(language)
    
    # Build file structure
    for filepath in files.keys():
        parts = filepath.split('/')
        current = output["file_structure"]
        
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        current[parts[-1]] = "file"
    
    return output

def _detect_language(filepath: str) -> str:
    """Detect programming language from file extension."""
    
    extension = filepath.split('.')[-1].lower()
    
    language_map = {
        'py': 'python',
        'js': 'javascript',
        'jsx': 'jsx',
        'ts': 'typescript',
        'tsx': 'tsx',
        'html': 'html',
        'css': 'css',
        'json': 'json',
        'md': 'markdown',
        'sql': 'sql',
        'yaml': 'yaml',
        'yml': 'yaml'
    }
    
    return language_map.get(extension, 'text')

def create_deployment_manifest(files: Dict[str, str], requirements: Dict[str, Any]) -> Dict[str, Any]:
    """Create deployment manifest for generated project."""
    
    manifest = {
        "project_info": {
            "name": "botarmy-generated-project",
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat(),
            "technology_stack": requirements.get("technology_stack", {})
        },
        "deployment": {
            "platform": "replit",
            "entry_point": "main.py",
            "build_command": "pip install -r requirements.txt && npm install && npm run build",
            "start_command": "python main.py"
        },
        "dependencies": {
            "python": _extract_python_dependencies(files),
            "node": _extract_node_dependencies(files)
        },
        "environment": {
            "required_vars": [
                "OPENAI_API_KEY",
                "DATABASE_URL"
            ],
            "optional_vars": [
                "LOG_LEVEL",
                "DEBUG"
            ]
        },
        "files": {
            "total_count": len(files),
            "by_type": {}
        }
    }
    
    # Count files by type
    for filepath in files.keys():
        file_type = _detect_language(filepath)
        manifest["files"]["by_type"][file_type] = manifest["files"]["by_type"].get(file_type, 0) + 1
    
    return manifest

def _extract_python_dependencies(files: Dict[str, str]) -> List[str]:
    """Extract Python dependencies from code."""
    
    dependencies = set()
    
    for filepath, content in files.items():
        if filepath.endswith('.py'):
            # Extract imports
            import_pattern = r'(?:from\s+(\w+)|import\s+(\w+))'
            matches = re.findall(import_pattern, content)
            
            for match in matches:
                module = match[0] or match[1]
                if module and not module.startswith('.'):
                    # Map common modules to package names
                    package_map = {
                        'fastapi': 'fastapi',
                        'pydantic': 'pydantic',
                        'openai': 'openai',
                        'sqlite3': '',  # Built-in
                        'asyncio': '',  # Built-in
                        'json': '',     # Built-in
                        'os': '',       # Built-in
                        'sys': '',      # Built-in
                        'datetime': '', # Built-in
                        'typing': '',   # Built-in
                        'pathlib': '',  # Built-in
                        'logging': ''   # Built-in
                    }
                    
                    package = package_map.get(module, module)
                    if package:
                        dependencies.add(package)
    
    return sorted(list(dependencies))

def _extract_node_dependencies(files: Dict[str, str]) -> List[str]:
    """Extract Node.js dependencies from code."""
    
    dependencies = set()
    
    for filepath, content in files.items():
        if filepath.endswith(('.js', '.jsx')):
            # Extract imports
            import_pattern = r'import.*?from\s+[\'"]([^\'"]+)[\'"]'
            matches = re.findall(import_pattern, content)
            
            for module in matches:
                if not module.startswith('.'):
                    dependencies.add(module)
    
    return sorted(list(dependencies))

def estimate_development_time(files: Dict[str, str]) -> Dict[str, Any]:
    """Estimate development time for generated code."""
    
    time_estimates = {
        "total_hours": 0,
        "by_file_type": {},
        "complexity_factors": [],
        "confidence": "medium"
    }
    
    # Base time estimates per line of code (in minutes)
    time_per_loc = {
        'python': 2,
        'javascript': 2,
        'jsx': 3,
        'html': 1,
        'css': 1.5,
        'sql': 1
    }
    
    for filepath, content in files.items():
        language = _detect_language(filepath)
        lines = len([line for line in content.split('\n') if line.strip()])
        
        base_time = (lines * time_per_loc.get(language, 2)) / 60  # Convert to hours
        
        # Complexity multiplier
        complexity = calculate_code_complexity(content, language)
        complexity_multiplier = 1 + (complexity / 100)  # Scale complexity impact
        
        estimated_time = base_time * complexity_multiplier
        
        time_estimates["by_file_type"][language] = time_estimates["by_file_type"].get(language, 0) + estimated_time
        time_estimates["total_hours"] += estimated_time
    
    # Round to reasonable precision
    time_estimates["total_hours"] = round(time_estimates["total_hours"], 1)
    for lang in time_estimates["by_file_type"]:
        time_estimates["by_file_type"][lang] = round(time_estimates["by_file_type"][lang], 1)
    
    return time_estimates

def validate_generated_project(files: Dict[str, str], requirements: Dict[str, Any]) -> Dict[str, Any]:
    """Validate that generated project meets requirements."""
    
    validation = {
        "valid": True,
        "score": 0,
        "issues": [],
        "checks": {
            "structure": False,
            "dependencies": False,
            "entry_points": False,
            "configuration": False
        }
    }
    
    required_files = []
    tech_stack = requirements.get("technology_stack", {})
    
    # Check for required backend files
    if tech_stack.get("backend") == "FastAPI":
        required_files.extend(["main.py", "requirements.txt"])
        
        if "main.py" in files:
            validation["checks"]["entry_points"] = True
    
    # Check for required frontend files  
    if tech_stack.get("frontend") == "React":
        required_files.extend(["package.json", "src/App.jsx"])
        
        if "package.json" in files:
            validation["checks"]["dependencies"] = True
    
    # Check file structure
    missing_files = [f for f in required_files if f not in files]
    if not missing_files:
        validation["checks"]["structure"] = True
    else:
        validation["issues"].extend([f"Missing required file: {f}" for f in missing_files])
        validation["valid"] = False
    
    # Check for configuration
    config_files = [".env.example", "config.py", "vite.config.js"]
    if any(f in files for f in config_files):
        validation["checks"]["configuration"] = True
    
    # Calculate score
    passed_checks = sum(validation["checks"].values())
    validation["score"] = (passed_checks / len(validation["checks"])) * 100
    
    return validation
