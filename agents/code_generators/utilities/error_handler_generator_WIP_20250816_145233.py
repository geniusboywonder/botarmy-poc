"""
Error Handler Generator
Generates comprehensive error handling utilities for FastAPI application.
"""

from typing import Dict, Any
from ..base import BaseGenerator


class ErrorHandlerGenerator(BaseGenerator):
    """
    Generator for error handling utilities.
    Creates comprehensive error handling and recovery mechanisms.
    """

    async def generate(self, specifications: Dict) -> str:
        """Generate error handler module code."""
        
        try:
            # Attempt LLM generation
            prompt = self._create_error_handler_prompt(specifications)
            content = await self._try_llm_generation(prompt, max_tokens=2500, temperature=0.1)
            
            self._update_generation_stats()
            return content
            
        except Exception as e:
            self.logger.warning(f"Error Handler LLM generation failed: {str(e)}, using fallback")
            content = self._use_fallback()
            self._update_generation_stats()
            return content

    def _create_error_handler_prompt(self, specifications: Dict) -> str:
        """Create prompt for error handler generation."""
        
        return """Generate a comprehensive error handling module for a FastAPI BotArmy application.

Requirements:
1. Create custom exception classes for different error types
2. Include FastAPI exception handlers for different HTTP status codes
3. Add error logging and monitoring integration
4. Include error recovery and retry mechanisms
5. Add API error response formatting with consistent structure
6. Include validation error handling
7. Add database error handling
8. Include LLM API error handling
9. Add system error monitoring and alerting
10. Include error escalation mechanisms
11. Add proper error context and tracing
12. Include development vs production error handling

Generate clean, well-documented Python code with comprehensive error handling patterns.
"""

    def _generate_fallback(self) -> str:
        """Generate fallback error handler module."""
        
        return '''"""
Comprehensive error handling utilities for BotArmy FastAPI application.
Provides custom exceptions, error handlers, and recovery mechanisms.
"""

import traceback
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger(__name__)

# Custom Exception Classes

class BotArmyError(Exception):
    """Base exception for BotArmy application"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        self.message = message
        self.error_code = error_code or "BOTARMY_ERROR"
        self.details = details or {}
        self.timestamp = datetime.now()
        super().__init__(self.message)

class AgentError(BotArmyError):
    """Exception for agent-related errors"""
    
    def __init__(self, agent_type: str, message: str, **kwargs):
        self.agent_type = agent_type
        super().__init__(message, error_code="AGENT_ERROR", **kwargs)

class WorkflowError(BotArmyError):
    """Exception for workflow-related errors"""
    
    def __init__(self, workflow_stage: str, message: str, **kwargs):
        self.workflow_stage = workflow_stage
        super().__init__(message, error_code="WORKFLOW_ERROR", **kwargs)

class ErrorHandler:
    """Comprehensive error handler for the BotArmy application."""

    def __init__(self, logger_instance=None):
        self.logger = logger_instance or logger
        self.error_counts = {}
        self.error_history = []

    def log_error(self, error: Exception, context: Dict = None):
        """Log error with context and tracking"""
        
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.now().isoformat(),
            "context": context or {},
            "traceback": traceback.format_exc()
        }
        
        # Track error counts
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Store in error history (keep last 100)
        self.error_history.append(error_info)
        if len(self.error_history) > 100:
            self.error_history.pop(0)
        
        # Log the error
        self.logger.error(f"Error occurred: {error_info}")
        
        return error_info

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        
        total_errors = sum(self.error_counts.values())
        
        return {
            "total_errors": total_errors,
            "error_counts": self.error_counts.copy(),
            "recent_errors": len(self.error_history)
        }

# Global error handler instance
error_handler = ErrorHandler()

# FastAPI Error Handlers

async def handle_api_error(request: Request, exc: Exception, logger_instance=None) -> JSONResponse:
    """Global API error handler for FastAPI"""
    
    logger_to_use = logger_instance or logger
    
    # Log the error with context
    context = {
        "url": str(request.url),
        "method": request.method,
        "client_ip": request.client.host if request.client else None
    }
    
    error_info = error_handler.log_error(exc, context)
    
    # Handle different exception types
    if isinstance(exc, BotArmyError):
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                    "timestamp": exc.timestamp.isoformat()
                }
            }
        )
    
    elif isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "HTTP_ERROR",
                    "message": exc.detail,
                    "status_code": exc.status_code
                }
            }
        )
    
    elif isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": exc.errors()
                }
            }
        )
    
    else:
        # Generic server error
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An internal error occurred",
                    "error_id": error_info.get("timestamp")
                }
            }
        )

def create_error_response(error_code: str, message: str, status_code: int = 400, 
                         details: Dict = None) -> JSONResponse:
    """Create standardized error response"""
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": error_code,
                "message": message,
                "details": details or {},
                "timestamp": datetime.now().isoformat()
            }
        }
    )

# Export main functions and classes
__all__ = [
    'BotArmyError', 'AgentError', 'WorkflowError', 'ErrorHandler', 
    'handle_api_error', 'create_error_response'
]
'''
