"""
Code quality checking and validation for generated code.
"""

import re
import ast
import json
from typing import Dict, Any, List, Tuple
import subprocess
import tempfile
import os

class QualityChecker:
    """Validates and checks quality of generated code."""
    
    def __init__(self, logger):
        self.logger = logger
        self.quality_metrics = {}
    
    async def check_python_code(self, code: str, filename: str = "temp.py") -> Dict[str, Any]:
        """Check Python code quality and syntax."""
        
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "metrics": {},
            "security_issues": []
        }
        
        # Syntax check
        try:
            ast.parse(code)
            results["metrics"]["syntax_valid"] = True
        except SyntaxError as e:
            results["valid"] = False
            results["errors"].append({
                "type": "syntax_error",
                "message": str(e),
                "line": getattr(e, 'lineno', None)
            })
            results["metrics"]["syntax_valid"] = False
        
        # Security checks
        security_issues = self._check_python_security(code)
        results["security_issues"].extend(security_issues)
        
        # Code metrics
        results["metrics"].update(self._calculate_python_metrics(code))
        
        # Style checks
        style_warnings = self._check_python_style(code)
        results["warnings"].extend(style_warnings)
        
        return results
    
    async def check_javascript_code(self, code: str, filename: str = "temp.js") -> Dict[str, Any]:
        """Check JavaScript/React code quality."""
        
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "metrics": {},
            "security_issues": []
        }
        
        # Basic syntax validation (simplified)
        try:
            # Check for common syntax errors
            if self._has_js_syntax_errors(code):
                results["valid"] = False
                results["errors"].append({
                    "type": "syntax_error",
                    "message": "JavaScript syntax errors detected"
                })
        except Exception as e:
            results["errors"].append({
                "type": "validation_error",
                "message": str(e)
            })
        
        # Security checks
        security_issues = self._check_js_security(code)
        results["security_issues"].extend(security_issues)
        
        # Code metrics
        results["metrics"].update(self._calculate_js_metrics(code))
        
        # React-specific checks
        if self._is_react_component(code):
            react_warnings = self._check_react_patterns(code)
            results["warnings"].extend(react_warnings)
        
        return results
    
    def _check_python_security(self, code: str) -> List[Dict[str, str]]:
        """Check for common Python security issues."""
        
        security_issues = []
        
        # Check for dangerous imports
        dangerous_imports = [
            "os.system", "subprocess.call", "eval(", "exec(", 
            "import pickle", "import subprocess"
        ]
        
        for dangerous in dangerous_imports:
            if dangerous in code:
                security_issues.append({
                    "type": "dangerous_import",
                    "message": f"Potentially dangerous code: {dangerous}",
                    "severity": "high"
                })
        
        # Check for SQL injection patterns
        sql_patterns = [
            r"f\".*SELECT.*{.*}.*\"",
            r"\".*SELECT.*\"\s*\+",
            r"\".*INSERT.*\"\s*\+"
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, code):
                security_issues.append({
                    "type": "sql_injection",
                    "message": "Potential SQL injection vulnerability",
                    "severity": "high"
                })
        
        # Check for hardcoded secrets
        secret_patterns = [
            r"password\s*=\s*[\"'][^\"']+[\"']",
            r"api_key\s*=\s*[\"'][^\"']+[\"']",
            r"secret\s*=\s*[\"'][^\"']+[\"']"
        ]
        
        for pattern in secret_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                security_issues.append({
                    "type": "hardcoded_secret",
                    "message": "Potential hardcoded secret found",
                    "severity": "medium"
                })
        
        return security_issues
    
    def _check_js_security(self, code: str) -> List[Dict[str, str]]:
        """Check for JavaScript security issues."""
        
        security_issues = []
        
        # Check for dangerous functions
        dangerous_functions = ["eval(", "innerHTML =", "document.write(", "setTimeout("]
        
        for func in dangerous_functions:
            if func in code:
                security_issues.append({
                    "type": "dangerous_function",
                    "message": f"Potentially dangerous function: {func}",
                    "severity": "medium"
                })
        
        # Check for XSS vulnerabilities
        xss_patterns = [
            r"dangerouslySetInnerHTML\s*:",
            r"innerHTML\s*=.*\+",
            r"document\.write\("
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, code):
                security_issues.append({
                    "type": "xss_vulnerability",
                    "message": "Potential XSS vulnerability",
                    "severity": "high"
                })
        
        return security_issues
    
    def _calculate_python_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate Python code metrics."""
        
        metrics = {}
        lines = code.split('\n')
        
        metrics["lines_of_code"] = len([line for line in lines if line.strip()])
        metrics["blank_lines"] = len([line for line in lines if not line.strip()])
        metrics["comment_lines"] = len([line for line in lines if line.strip().startswith('#')])
        
        # Function count
        metrics["function_count"] = len(re.findall(r'def\s+\w+', code))
        
        # Class count
        metrics["class_count"] = len(re.findall(r'class\s+\w+', code))
        
        # Complexity estimation (simplified)
        complexity_indicators = ['if ', 'for ', 'while ', 'try:', 'except:', 'elif ']
        metrics["estimated_complexity"] = sum(code.count(indicator) for indicator in complexity_indicators)
        
        return metrics
    
    def _calculate_js_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate JavaScript code metrics."""
        
        metrics = {}
        lines = code.split('\n')
        
        metrics["lines_of_code"] = len([line for line in lines if line.strip()])
        metrics["blank_lines"] = len([line for line in lines if not line.strip()])
        metrics["comment_lines"] = len([line for line in lines if line.strip().startswith('//')])
        
        # Function count
        metrics["function_count"] = len(re.findall(r'function\s+\w+|=>\s*{|\w+\s*=\s*function', code))
        
        # Component count (React)
        metrics["component_count"] = len(re.findall(r'function\s+[A-Z]\w+|const\s+[A-Z]\w+\s*=', code))
        
        # Hook usage (React)
        metrics["hooks_used"] = len(re.findall(r'use[A-Z]\w*\(', code))
        
        return metrics
    
    def _check_python_style(self, code: str) -> List[Dict[str, str]]:
        """Check Python code style."""
        
        warnings = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Line length check
            if len(line) > 120:
                warnings.append({
                    "type": "style_warning",
                    "message": f"Line {i} exceeds 120 characters",
                    "line": i
                })
            
            # Indentation check (simplified)
            if line.startswith('    ') and '        ' in line:
                # Check for inconsistent indentation
                stripped = line.lstrip()
                if stripped and (len(line) - len(stripped)) % 4 != 0:
                    warnings.append({
                        "type": "style_warning",
                        "message": f"Line {i} has inconsistent indentation",
                        "line": i
                    })
        
        return warnings
    
    def _has_js_syntax_errors(self, code: str) -> bool:
        """Check for basic JavaScript syntax errors."""
        
        # Simple checks for common syntax errors
        brackets = {'(': ')', '[': ']', '{': '}'}
        stack = []
        
        in_string = False
        string_char = None
        
        for char in code:
            if char in ['"', "'", '`'] and not in_string:
                in_string = True
                string_char = char
            elif char == string_char and in_string:
                in_string = False
                string_char = None
            elif not in_string:
                if char in brackets:
                    stack.append(char)
                elif char in brackets.values():
                    if not stack:
                        return True
                    if brackets.get(stack.pop()) != char:
                        return True
        
        return len(stack) > 0
    
    def _is_react_component(self, code: str) -> bool:
        """Check if code is a React component."""
        
        react_indicators = [
            'import React',
            'from \'react\'',
            'jsx',
            'className=',
            'useState(',
            'useEffect('
        ]
        
        return any(indicator in code for indicator in react_indicators)
    
    def _check_react_patterns(self, code: str) -> List[Dict[str, str]]:
        """Check React-specific patterns and best practices."""
        
        warnings = []
        
        # Check for missing key props in lists
        if '.map(' in code and 'key=' not in code:
            warnings.append({
                "type": "react_warning",
                "message": "Missing key prop in list rendering"
            })
        
        # Check for direct state mutation
        if 'state.' in code and '.push(' in code:
            warnings.append({
                "type": "react_warning",
                "message": "Potential direct state mutation detected"
            })
        
        # Check for missing dependencies in useEffect
        if 'useEffect(' in code and '[]' not in code:
            warnings.append({
                "type": "react_warning",
                "message": "useEffect may be missing dependency array"
            })
        
        return warnings
    
    async def generate_quality_report(self, checks: Dict[str, Dict]) -> Dict[str, Any]:
        """Generate comprehensive quality report."""
        
        report = {
            "overall_score": 0,
            "total_errors": 0,
            "total_warnings": 0,
            "categories": {},
            "recommendations": []
        }
        
        for category, results in checks.items():
            report["categories"][category] = {
                "valid": results.get("valid", True),
                "errors": len(results.get("errors", [])),
                "warnings": len(results.get("warnings", [])),
                "security_issues": len(results.get("security_issues", [])),
                "metrics": results.get("metrics", {})
            }
            
            report["total_errors"] += len(results.get("errors", []))
            report["total_warnings"] += len(results.get("warnings", []))
        
        # Calculate overall score (0-100)
        total_issues = report["total_errors"] + report["total_warnings"]
        if total_issues == 0:
            report["overall_score"] = 100
        else:
            # Deduct points based on severity
            error_penalty = report["total_errors"] * 10
            warning_penalty = report["total_warnings"] * 5
            report["overall_score"] = max(0, 100 - error_penalty - warning_penalty)
        
        # Generate recommendations
        report["recommendations"] = self._generate_recommendations(checks)
        
        return report
    
    def _generate_recommendations(self, checks: Dict[str, Dict]) -> List[str]:
        """Generate improvement recommendations based on quality checks."""
        
        recommendations = []
        
        for category, results in checks.items():
            errors = results.get("errors", [])
            warnings = results.get("warnings", [])
            security_issues = results.get("security_issues", [])
            
            if errors:
                recommendations.append(f"Fix {len(errors)} critical errors in {category}")
            
            if len(warnings) > 5:
                recommendations.append(f"Address {len(warnings)} warnings in {category} to improve code quality")
            
            if security_issues:
                recommendations.append(f"Address {len(security_issues)} security issues in {category}")
        
        if not recommendations:
            recommendations.append("Code quality is good! Consider adding more comprehensive tests.")
        
        return recommendations
