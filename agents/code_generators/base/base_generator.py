"""
Base Generator Interface
Provides consistent interface for all specialized generators within managers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime


class BaseGenerator(ABC):
    """
    Base class for all code generators.
    Provides common functionality and ensures consistent interfaces.
    """

    def __init__(self, llm_client, logger):
        self.llm_client = llm_client
        self.logger = logger
        
        # Generator statistics
        self.generation_stats = {
            "files_generated": 0,
            "llm_calls": 0,
            "fallback_used": 0,
            "errors": [],
            "last_generation": None
        }

    @abstractmethod
    async def generate(self, specifications: Dict) -> str:
        """
        Generate specific file content.
        
        Args:
            specifications: Generation specifications
            
        Returns:
            Generated file content as string
        """
        pass

    @abstractmethod
    def _generate_fallback(self) -> str:
        """
        Fallback generation when LLM fails.
        Must be implemented by each generator.
        
        Returns:
            Static fallback content
        """
        pass

    async def _try_llm_generation(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.1) -> str:
        """
        Attempt LLM generation with error handling.
        
        Args:
            prompt: Generation prompt
            max_tokens: Maximum tokens for generation
            temperature: LLM temperature setting
            
        Returns:
            Generated content or raises exception
        """
        try:
            self.generation_stats["llm_calls"] += 1
            
            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.strip()
            
        except Exception as e:
            error_msg = f"LLM generation failed: {str(e)}"
            self.generation_stats["errors"].append({
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            })
            raise

    def _use_fallback(self) -> str:
        """Use fallback generation and update stats."""
        self.generation_stats["fallback_used"] += 1
        self.logger.warning(f"{self.__class__.__name__} using fallback generation")
        return self._generate_fallback()

    def _update_generation_stats(self):
        """Update generation statistics."""
        self.generation_stats["files_generated"] += 1
        self.generation_stats["last_generation"] = datetime.now()

    def get_generator_stats(self) -> Dict[str, Any]:
        """Get generator statistics."""
        return {
            **self.generation_stats,
            "success_rate": self._calculate_success_rate()
        }

    def _calculate_success_rate(self) -> float:
        """Calculate success rate based on LLM vs fallback usage."""
        total_attempts = self.generation_stats["llm_calls"]
        if total_attempts == 0:
            return 0.0
            
        successful_llm = total_attempts - len(self.generation_stats["errors"])
        return (successful_llm / total_attempts) * 100

    def reset_stats(self):
        """Reset generator statistics."""
        self.generation_stats = {
            "files_generated": 0,
            "llm_calls": 0,
            "fallback_used": 0,
            "errors": [],
            "last_generation": None
        }
