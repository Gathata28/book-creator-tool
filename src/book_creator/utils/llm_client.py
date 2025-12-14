"""
LLM configuration and client management
"""

import os
from typing import Optional, Dict, Any
from enum import Enum


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class LLMConfig:
    """Configuration for LLM integration"""
    
    def __init__(
        self,
        provider: LLMProvider = LLMProvider.OPENAI,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        self.provider = provider
        self.api_key = api_key or self._get_api_key()
        self.model = model or self._get_default_model()
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _get_api_key(self) -> str:
        """Get API key from environment"""
        if self.provider == LLMProvider.OPENAI:
            return os.getenv("OPENAI_API_KEY", "")
        elif self.provider == LLMProvider.ANTHROPIC:
            return os.getenv("ANTHROPIC_API_KEY", "")
        return ""

    def _get_default_model(self) -> str:
        """Get default model for provider"""
        if self.provider == LLMProvider.OPENAI:
            return "gpt-4"
        elif self.provider == LLMProvider.ANTHROPIC:
            return "claude-3-sonnet-20240229"
        return ""


class LLMClient:
    """Client for interacting with LLM providers"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = self._initialize_client()

    def _initialize_client(self):
        """Initialize the appropriate client based on provider"""
        if self.config.provider == LLMProvider.OPENAI:
            try:
                from openai import OpenAI
                return OpenAI(api_key=self.config.api_key)
            except ImportError:
                raise ImportError("OpenAI package not installed. Run: pip install openai")
        elif self.config.provider == LLMProvider.ANTHROPIC:
            try:
                from anthropic import Anthropic
                return Anthropic(api_key=self.config.api_key)
            except ImportError:
                raise ImportError("Anthropic package not installed. Run: pip install anthropic")
        return None

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using the configured LLM"""
        if self.config.provider == LLMProvider.OPENAI:
            return self._generate_openai(prompt, system_prompt)
        elif self.config.provider == LLMProvider.ANTHROPIC:
            return self._generate_anthropic(prompt, system_prompt)
        return ""

    def _generate_openai(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using OpenAI"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self._client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating text with OpenAI: {e}")
            return ""

    def _generate_anthropic(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using Anthropic"""
        try:
            response = self._client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Error generating text with Anthropic: {e}")
            return ""

    async def generate_text_async(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text asynchronously"""
        # For now, call synchronous version
        # In production, use async clients
        return self.generate_text(prompt, system_prompt)
