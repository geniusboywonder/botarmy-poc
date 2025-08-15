import asyncio
import json
from typing import Dict, Optional
from openai import AsyncOpenAI
import logging

logger = logging.getLogger(__name__)


class LLMClient:

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
        self.max_retries = 3
        self.base_delay = 1.0

    async def generate_response(self,
                                prompt: str,
                                system_prompt: str = None,
                                temperature: float = 0.3,
                                max_tokens: int = 2000) -> Dict:
        """Generate response from LLM with retry logic"""

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        for attempt in range(self.max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens)

                content = response.choices[0].message.content
                usage = response.usage

                return {
                    "content": content,
                    "tokens_used": usage.total_tokens,
                    "success": True
                }

            except Exception as e:
                logger.warning(
                    f"LLM API attempt {attempt + 1} failed: {str(e)}")

                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2**attempt
                                               )  # Exponential backoff
                    await asyncio.sleep(delay)
                else:
                    return {
                        "content":
                        f"LLM API failed after {self.max_retries} attempts: {str(e)}",
                        "tokens_used": 0,
                        "success": False,
                        "error": str(e)
                    }

    async def extract_json(self, text: str, schema_description: str) -> Dict:
        """Extract structured JSON from text response"""
        prompt = f"""
        Extract the following information from the text and return as valid JSON:
        Schema: {schema_description}

        Text: {text}

        Return only valid JSON, no other text:
        """

        response = await self.generate_response(prompt, temperature=0.1)

        if not response["success"]:
            return {"error": response["error"]}

        try:
            return json.loads(response["content"])
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON response: {str(e)}"}
