"""
Config Generator
Generates comprehensive configuration management with Pydantic settings.
"""

from typing import Dict, Any
from ..base import BaseGenerator


class ConfigGenerator(BaseGenerator):
    """
    Generator for configuration management module.
    Creates Pydantic-based configuration with environment variable support.
    """

    async def generate(self, specifications: Dict) -> str:
        """Generate configuration module code."""
        
        try:
            # Attempt LLM generation
            prompt = self._create_config_prompt(specifications)
            content = await self._try_llm_generation(prompt, max_tokens=2500, temperature=0.1)
            
            self._update_generation_stats()
            return content
            
        except Exception as e:
            self.logger.warning(f"Config LLM generation failed: {str(e)}, using fallback")
            content = self._use_fallback()
            self._update_generation_stats()
            return content

    def _create_config_prompt(self, specifications: Dict) -> str:
        """Create prompt for config generation."""
        
        return """Generate a comprehensive Pydantic-based configuration module for a FastAPI BotArmy application.

Requirements:
1. Use Pydantic BaseSettings for environment variable loading
2. Include OpenAI API configuration (key, model, tokens, temperature, timeout)
3. Include database configuration (URL, pool size, timeout)
4. Include server configuration (host, port, workers, debug mode)
5. Include security settings (secret key, CORS origins, rate limiting)
6. Include logging configuration (level, file path, rotation)
7. Include file storage settings (upload directory, max file size, allowed types)
8. Include agent and workflow timeouts and retry settings
9. Include performance settings (caching, compression, metrics)
10. Add proper validation with Pydantic validators
11. Include methods for creating directories and setting up logging
12. Add utility methods for getting specific config groups

Generate clean, well-documented Python code with proper type hints and validation.
"""

    def _generate_fallback(self) -> str:
        """Generate fallback configuration module."""
        
        return '''"""
Configuration management for BotArmy application.
Handles environment variables, settings validation, and application configuration.
"""

import os
from typing import Optional, List
from pydantic import BaseSettings, Field, validator
import logging

class Settings(BaseSettings):
    """Application settings loaded from environment variables with validation."""

    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o-mini", description="OpenAI model to use")
    openai_max_tokens: int = Field(default=2000, ge=1, le=8000, description="Maximum tokens per request")
    openai_temperature: float = Field(default=0.2, ge=0.0, le=2.0, description="Generation temperature")
    openai_timeout: int = Field(default=60, ge=10, le=300, description="Request timeout in seconds")

    # Database Configuration
    database_url: str = Field(default="sqlite:///./data/botarmy.db", description="Database connection URL")
    database_pool_size: int = Field(default=5, ge=1, le=20, description="Database connection pool size")

    # Application Configuration
    app_name: str = Field(default="BotArmy", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    max_concurrent_projects: int = Field(default=10, ge=1, le=100, description="Maximum concurrent projects")

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, ge=1, le=65535, description="Server port")
    workers: int = Field(default=1, ge=1, le=8, description="Number of worker processes")

    # Security Configuration
    secret_key: str = Field(default="your-secret-key-change-in-production", min_length=32, description="Secret key for sessions")
    cors_origins: List[str] = Field(default=["*"], description="CORS allowed origins")
    rate_limit_requests: int = Field(default=100, ge=1, description="Rate limit requests per minute")

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="./data/logs/app.log", description="Log file path")
    log_rotation: str = Field(default="1 day", description="Log rotation period")
    log_retention: str = Field(default="30 days", description="Log retention period")

    # File Storage Configuration
    upload_dir: str = Field(default="./data/uploads", description="File upload directory")
    max_file_size: int = Field(default=10485760, ge=1024, description="Maximum file size in bytes (10MB)")
    allowed_file_types: List[str] = Field(default=[".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".md", ".txt"], description="Allowed file extensions")

    # Agent Configuration
    agent_timeout: int = Field(default=300, ge=30, le=1800, description="Agent processing timeout in seconds")
    max_retries: int = Field(default=3, ge=1, le=10, description="Maximum retry attempts")
    retry_delay: float = Field(default=1.0, ge=0.1, le=10.0, description="Retry delay in seconds")

    # Workflow Configuration
    pipeline_timeout: int = Field(default=1800, ge=60, le=7200, description="Pipeline timeout in seconds")
    conflict_resolution_timeout: int = Field(default=3600, ge=60, description="Conflict resolution timeout")

    # Performance Configuration
    enable_caching: bool = Field(default=True, description="Enable response caching")
    cache_ttl: int = Field(default=300, ge=60, le=3600, description="Cache TTL in seconds")
    enable_compression: bool = Field(default=True, description="Enable response compression")

    # Monitoring Configuration
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    metrics_port: int = Field(default=8001, ge=1, le=65535, description="Metrics server port")

    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'log_level must be one of {valid_levels}')
        return v.upper()

    @validator('openai_api_key')
    def validate_api_key(cls, v):
        if not v or v == 'your_openai_api_key_here':
            raise ValueError('OpenAI API key must be provided')
        return v

    @validator('secret_key')
    def validate_secret_key(cls, v):
        if v == 'your-secret-key-change-in-production':
            import secrets
            return secrets.token_urlsafe(32)
        return v

    @validator('database_url')
    def validate_database_url(cls, v):
        if not v.startswith(('sqlite:///', 'postgresql://', 'mysql://')):
            raise ValueError('Invalid database URL format')
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        validate_assignment = True

    def create_directories(self):
        """Create necessary directories for the application"""
        directories = [
            os.path.dirname(self.database_url.replace("sqlite:///", "")),
            os.path.dirname(self.log_file),
            self.upload_dir,
            "./data/projects",
            "./data/backups",
            "./data/cache"
        ]
        
        for directory in directories:
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

    def setup_logging(self):
        """Setup application logging based on configuration"""
        
        # Ensure log directory exists
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )

        # Set specific logger levels
        logging.getLogger("uvicorn").setLevel(logging.INFO)
        logging.getLogger("fastapi").setLevel(logging.INFO)

    def get_database_config(self) -> dict:
        """Get database-specific configuration"""
        return {
            "url": self.database_url,
            "pool_size": self.database_pool_size,
            "timeout": 30,
            "echo": self.debug
        }

    def get_llm_config(self) -> dict:
        """Get LLM client configuration"""
        return {
            "api_key": self.openai_api_key,
            "model": self.openai_model,
            "max_tokens": self.openai_max_tokens,
            "temperature": self.openai_temperature,
            "timeout": self.openai_timeout,
            "max_retries": self.max_retries
        }

    def get_server_config(self) -> dict:
        """Get server configuration for uvicorn"""
        return {
            "host": self.host,
            "port": self.port,
            "workers": self.workers if not self.debug else 1,
            "reload": self.debug,
            "log_level": self.log_level.lower(),
            "access_log": True
        }

# Global settings instance
settings = Settings()

# Initialize directories and logging on import
settings.create_directories()
settings.setup_logging()

def get_settings() -> Settings:
    """Get application settings instance"""
    return settings

def reload_settings():
    """Reload settings from environment/config files"""
    global settings
    settings = Settings()
    settings.create_directories()
    settings.setup_logging()
    return settings
'''
