"""
Message domain models.
Shared across all modules for chat communication.
"""

from pydantic import BaseModel
from typing import Literal


Role = Literal["user", "assistant", "system"]


class Message(BaseModel):
    """
    A single chat message.

    Attributes:
        role: Who sent the message (user, assistant, system)
        content: The text content of the message
    """
    role: Role
    content: str


class ChatRequest(BaseModel):
    """
    Request for chat completion.

    Attributes:
        messages: Conversation history
        temperature: Sampling temperature (0.0 - 2.0)
        max_tokens: Maximum tokens to generate
        stream: Whether to stream the response
    """
    messages: list[Message]
    temperature: float = 0.7
    max_tokens: int = 2000
    stream: bool = True


class ChatResponse(BaseModel):
    """
    Non-streaming chat completion response.

    Attributes:
        role: Role of the responder (always assistant)
        content: The generated text content
    """
    role: Role = "assistant"
    content: str
