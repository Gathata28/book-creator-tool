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
    GOOGLE = "google"
    COHERE = "cohere"
    MISTRAL = "mistral"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"


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
        elif self.provider == LLMProvider.GOOGLE:
            return os.getenv("GOOGLE_API_KEY", "")
        elif self.provider == LLMProvider.COHERE:
            return os.getenv("COHERE_API_KEY", "")
        elif self.provider == LLMProvider.MISTRAL:
            return os.getenv("MISTRAL_API_KEY", "")
        elif self.provider == LLMProvider.HUGGINGFACE:
            return os.getenv("HUGGINGFACE_API_KEY", "")
        elif self.provider == LLMProvider.OLLAMA:
            return ""  # Ollama runs locally, no API key needed
        return ""

    def _get_default_model(self) -> str:
        """Get default model for provider"""
        if self.provider == LLMProvider.OPENAI:
            return "gpt-4"
        elif self.provider == LLMProvider.ANTHROPIC:
            return "claude-3-sonnet-20240229"
        elif self.provider == LLMProvider.GOOGLE:
            return "gemini-pro"
        elif self.provider == LLMProvider.COHERE:
            return "command"
        elif self.provider == LLMProvider.MISTRAL:
            return "mistral-medium"
        elif self.provider == LLMProvider.HUGGINGFACE:
            return "meta-llama/Llama-2-70b-chat-hf"
        elif self.provider == LLMProvider.OLLAMA:
            return "llama2"
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
        elif self.config.provider == LLMProvider.GOOGLE:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.config.api_key)
                return genai
            except ImportError:
                raise ImportError("Google Generative AI package not installed. Run: pip install google-generativeai")
        elif self.config.provider == LLMProvider.COHERE:
            try:
                import cohere
                return cohere.Client(api_key=self.config.api_key)
            except ImportError:
                raise ImportError("Cohere package not installed. Run: pip install cohere")
        elif self.config.provider == LLMProvider.MISTRAL:
            try:
                from mistralai.client import MistralClient
                return MistralClient(api_key=self.config.api_key)
            except ImportError:
                raise ImportError("Mistral AI package not installed. Run: pip install mistralai")
        elif self.config.provider == LLMProvider.HUGGINGFACE:
            try:
                from huggingface_hub import InferenceClient
                return InferenceClient(token=self.config.api_key)
            except ImportError:
                raise ImportError("HuggingFace Hub package not installed. Run: pip install huggingface-hub")
        elif self.config.provider == LLMProvider.OLLAMA:
            try:
                import ollama
                return ollama
            except ImportError:
                raise ImportError("Ollama package not installed. Run: pip install ollama")
        return None

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using the configured LLM"""
        if self.config.provider == LLMProvider.OPENAI:
            return self._generate_openai(prompt, system_prompt)
        elif self.config.provider == LLMProvider.ANTHROPIC:
            return self._generate_anthropic(prompt, system_prompt)
        elif self.config.provider == LLMProvider.GOOGLE:
            return self._generate_google(prompt, system_prompt)
        elif self.config.provider == LLMProvider.COHERE:
            return self._generate_cohere(prompt, system_prompt)
        elif self.config.provider == LLMProvider.MISTRAL:
            return self._generate_mistral(prompt, system_prompt)
        elif self.config.provider == LLMProvider.HUGGINGFACE:
            return self._generate_huggingface(prompt, system_prompt)
        elif self.config.provider == LLMProvider.OLLAMA:
            return self._generate_ollama(prompt, system_prompt)
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

    def _generate_google(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using Google Gemini"""
        try:
            model = self._client.GenerativeModel(self.config.model)
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = model.generate_content(
                full_prompt,
                generation_config={
                    'temperature': self.config.temperature,
                    'max_output_tokens': self.config.max_tokens,
                }
            )
            return response.text
        except Exception as e:
            print(f"Error generating text with Google: {e}")
            return ""

    def _generate_cohere(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using Cohere"""
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = self._client.generate(
                model=self.config.model,
                prompt=full_prompt,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            return response.generations[0].text
        except Exception as e:
            print(f"Error generating text with Cohere: {e}")
            return ""

    def _generate_mistral(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using Mistral AI"""
        try:
            from mistralai.models.chat_completion import ChatMessage
            messages = []
            if system_prompt:
                messages.append(ChatMessage(role="system", content=system_prompt))
            messages.append(ChatMessage(role="user", content=prompt))
            
            response = self._client.chat(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating text with Mistral: {e}")
            return ""

    def _generate_huggingface(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using HuggingFace"""
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = self._client.text_generation(
                full_prompt,
                model=self.config.model,
                max_new_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            return response
        except Exception as e:
            print(f"Error generating text with HuggingFace: {e}")
            return ""

    def _generate_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using Ollama (local models)"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self._client.chat(
                model=self.config.model,
                messages=messages,
                options={
                    'temperature': self.config.temperature,
                    'num_predict': self.config.max_tokens
                }
            )
            return response['message']['content']
        except Exception as e:
            print(f"Error generating text with Ollama: {e}")
            return ""

    async def generate_text_async(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text asynchronously"""
        # For now, call synchronous version
        # In production, use async clients
        return self.generate_text(prompt, system_prompt)
