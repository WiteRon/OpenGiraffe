"""
Chat domain abstractions.
Defines the contract that all chat providers must implement.
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator
from .message import Message


class ChatProvider(ABC):
    """
    Abstract base class for chat providers.

    Any LLM provider (OpenAI, Anthropic, OpenAI-compatible, etc.)
    must implement this interface to be used by the application.

    This enables:
    - Easy swapping of providers
    - Testing with mocks
    - Composition (e.g., RAG augmentation)
    """

    @abstractmethod
    async def chat_completion(
        self,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Non-streaming chat completion.

        Args:
            messages: The conversation history
            temperature: Sampling temperature
            max_tokens: maximum tokens to generate

        Returns:
            The complete generated text
        """
        pass

    @abstractmethod
    def stream_completion(
        self,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncGenerator[str, None]:
        """
        Streaming chat completion.

        Args:
            messages: The conversation history
            temperature: sampling temperature
            max_tokens: maximum tokens to generate

        Yields:
            Chunks of the generated text as they become available
        """
        pass
