"""
OpenAI-compatible chat provider.
Works with any OpenAI-compatible API (OpenAI, Volces/Minimax, etc.).
"""

from typing import AsyncGenerator
from openai import OpenAI
from ..config.settings import Settings
from ..domain.message import Message
from ..domain.chat import ChatProvider
from ..common.exceptions import LLMServiceError, ConfigurationError


class OpenAICompatProvider(ChatProvider):
    """
    Chat provider for OpenAI-compatible APIs.

    Supports:
    - Official OpenAI API
    - Volces/Minimax API
    - Any other OpenAI-compatible endpoint
    """

    def __init__(self, settings: Settings):
        """
        Initialize the OpenAI-compatible provider.

        Args:
            settings: Application settings containing API configuration
        """
        if not settings.api_key:
            raise ConfigurationError("API_KEY is required for OpenAICompatProvider")

        self.client = OpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url,
        )
        self.model = settings.model
        self.default_temperature = settings.default_temperature
        self.default_max_tokens = settings.default_max_tokens

    async def chat_completion(
        self,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Non-streaming chat completion.

        Args:
            messages: Conversation history
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Complete generated text

        Raises:
            LLMServiceError: If the API call fails
        """
        try:
            messages_dict = [
                {"role": msg.role, "content": msg.content} for msg in messages
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages_dict,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
            )

            content = response.choices[0].message.content
            return content or ""
        except Exception as e:
            raise LLMServiceError(f"OpenAI API call failed: {str(e)}") from e

    def stream_completion(
        self,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncGenerator[str, None]:
        """
        Streaming chat completion.

        Args:
            messages: Conversation history
            temperature: sampling temperature
            max_tokens: maximum tokens to generate

        Yields:
            Chunks of generated text as they become available

        Raises:
            LLMServiceError: If the API call fails
        """
        try:
            messages_dict = [
                {"role": msg.role, "content": msg.content} for msg in messages
            ]

            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages_dict,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise LLMServiceError(f"OpenAI API streaming failed: {str(e)}") from e
