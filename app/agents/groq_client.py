"""
Groq LLM Client — wraps the Groq API for chat completions.
"""

from typing import List, Dict, Optional
from loguru import logger
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential


class GroqClient:
    def __init__(self, api_key: str, model: str, temperature: float = 0.7, max_tokens: int = 2048):
        self.client = Groq(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        logger.info(f"GroqClient initialized | model={model}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Send chat messages and return the assistant reply."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
        )
        content = response.choices[0].message.content
        logger.debug(f"Groq response ({len(content)} chars)")
        return content

    def simple_prompt(self, system: str, user: str) -> str:
        """Convenience method for single-turn prompts."""
        return self.chat([
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ])
