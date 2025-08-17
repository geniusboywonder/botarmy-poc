"""
LLM Client Generator
Generates comprehensive OpenAI API client with retry logic and monitoring.
"""

from typing import Dict, Any
from ..base import BaseGenerator


class LLMClientGenerator(BaseGenerator):
    """
    Generator for LLM client module.
    Creates comprehensive OpenAI API client with advanced features.
    """

    async def generate(self, specifications: Dict) -> str:
        """Generate LLM client module code."""
        
        try:
            # Attempt LLM generation
            prompt = self._create_llm_client_prompt(specifications)
            content = await self._try_llm_generation(prompt, max_tokens=3000, temperature=0.1)
            
            self._update_generation_stats()
            return content
            
        except Exception as e:
            self.logger.warning(f"LLM Client LLM generation failed: {str(e)}, using fallback")
            content = self._use_fallback()
            self._update_generation_stats()
            return content

    def _create_llm_client_prompt(self, specifications: Dict) -> str:
        """Create prompt for LLM client generation."""
        
        return """Generate a comprehensive OpenAI API client for a BotArmy FastAPI application.

Requirements:
1. Use AsyncOpenAI for async API calls
2. Include comprehensive retry logic with exponential backoff
3. Add token tracking and cost calculation
4. Include response caching with TTL
5. Add rate limiting with semaphore
6. Include comprehensive error handling for different API errors
7. Add metrics tracking (requests, success rate, response time, costs)
8. Include batch generation capabilities
9. Add health check and status monitoring
10. Include configuration integration
11. Add proper logging and debugging
12. Include cache management and cleanup

Generate clean, production-ready async Python code with comprehensive error handling.
"""

    def _generate_fallback(self) -> str:
        """Generate fallback LLM client module."""
        
        return '''"""
OpenAI API client with advanced retry logic, token tracking, and error handling.
Provides robust LLM integration with comprehensive monitoring and optimization.
"""

import asyncio
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import logging
from datetime import datetime

from openai import AsyncOpenAI, APIError, RateLimitError, APITimeoutError
from config import get_settings

logger = logging.getLogger(__name__)

@dataclass
class LLMMetrics:
    """Metrics tracking for LLM usage"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    average_response_time: float = 0.0
    last_request_time: Optional[datetime] = None

class LLMClient:
    """
    Advanced OpenAI API client with comprehensive error handling and monitoring.
    Features: retry logic, token tracking, cost calculation, rate limiting, caching.
    """

    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenAI(
            api_key=self.settings.openai_api_key,
            timeout=self.settings.openai_timeout
        )
        
        self.metrics = LLMMetrics()
        self._response_cache = {}
        self._rate_limiter = asyncio.Semaphore(10)  # Max 10 concurrent requests
        
        # Token costs per 1K tokens (GPT-4o-mini pricing)
        self.token_costs = {
            "gpt-4o-mini": {
                "input": 0.00015,
                "output": 0.0006
            }
        }

    async def generate(self, prompt: str, max_tokens: int = None, 
                      temperature: float = None, max_retries: int = None,
                      system_message: str = None, use_cache: bool = True) -> str:
        """Generate completion from OpenAI API with comprehensive error handling."""
        
        max_tokens = max_tokens or self.settings.openai_max_tokens
        temperature = temperature or self.settings.openai_temperature
        max_retries = max_retries or self.settings.max_retries

        # Check cache first
        if use_cache:
            cache_key = self._generate_cache_key(prompt, max_tokens, temperature, system_message)
            if cache_key in self._response_cache:
                cached_response = self._response_cache[cache_key]
                if self._is_cache_valid(cached_response):
                    return cached_response["content"]

        # Rate limiting
        async with self._rate_limiter:
            return await self._generate_with_retry(
                prompt, max_tokens, temperature, max_retries, system_message, use_cache
            )

    async def _generate_with_retry(self, prompt: str, max_tokens: int, 
                                  temperature: float, max_retries: int,
                                  system_message: str, use_cache: bool) -> str:
        """Internal method with retry logic"""
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                
                messages = []
                if system_message:
                    messages.append({"role": "system", "content": system_message})
                messages.append({"role": "user", "content": prompt})

                response = await self.client.chat.completions.create(
                    model=self.settings.openai_model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )

                processing_time = time.time() - start_time
                self._track_successful_request(response.usage, processing_time)

                completion = response.choices[0].message.content

                if use_cache:
                    cache_key = self._generate_cache_key(prompt, max_tokens, temperature, system_message)
                    self._cache_response(cache_key, completion)

                return completion

            except RateLimitError as e:
                logger.warning(f"Rate limit hit on attempt {attempt + 1}")
                last_exception = e
                if attempt < max_retries:
                    wait_time = (2 ** attempt) + (time.time() % 1)
                    await asyncio.sleep(wait_time)
                    continue

            except Exception as e:
                logger.error(f"API error on attempt {attempt + 1}: {str(e)}")
                last_exception = e
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue

        self._track_failed_request()
        raise Exception(f"LLM API failed after {max_retries + 1} attempts")

    def _track_successful_request(self, usage, processing_time: float):
        """Track successful request metrics"""
        if usage:
            self.metrics.total_requests += 1
            self.metrics.successful_requests += 1
            self.metrics.total_tokens += usage.total_tokens
            self.metrics.last_request_time = datetime.now()

    def _track_failed_request(self):
        """Track failed request metrics"""
        self.metrics.total_requests += 1
        self.metrics.failed_requests += 1

    def _generate_cache_key(self, prompt: str, max_tokens: int, 
                           temperature: float, system_message: str) -> str:
        """Generate cache key for request parameters"""
        import hashlib
        key_data = f"{prompt}:{max_tokens}:{temperature}:{system_message or ''}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _cache_response(self, cache_key: str, content: str):
        """Cache response with timestamp"""
        self._response_cache[cache_key] = {
            "content": content,
            "timestamp": datetime.now(),
            "ttl": 300
        }

    def _is_cache_valid(self, cached_response: Dict) -> bool:
        """Check if cached response is still valid"""
        if not cached_response:
            return False
        cache_age = datetime.now() - cached_response["timestamp"]
        return cache_age.total_seconds() < cached_response["ttl"]

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get comprehensive usage statistics"""
        success_rate = (
            (self.metrics.successful_requests / self.metrics.total_requests * 100)
            if self.metrics.total_requests > 0 else 0
        )
        
        return {
            "total_requests": self.metrics.total_requests,
            "successful_requests": self.metrics.successful_requests,
            "failed_requests": self.metrics.failed_requests,
            "success_rate": round(success_rate, 2),
            "total_tokens": self.metrics.total_tokens,
            "total_cost": round(self.metrics.total_cost, 4),
            "model": self.settings.openai_model
        }

    def clear_cache(self):
        """Clear response cache"""
        self._response_cache.clear()
'''
