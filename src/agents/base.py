"""
Base agent interface for CrewAI integration (future extension).

When ready to add CrewAI agents:
1. Add 'crewai' to requirements.txt
2. Implement concrete agent classes in this module
3. Add to dependency container in src/container.py
"""

from abc import ABC, abstractmethod
from typing import Any
from ..domain.message import Message


class BaseAgent(ABC):
    """
    Abstract base class for AI agents.

    Agents can:
    - Perform specialized tasks
    - Collaborate with other agents (CrewAI)
    - Use tools to accomplish tasks
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent name."""
        pass

    @abstractmethod
    async def run(self, input: str, context: list[Message] | None = None) -> str:
        """
        Run the agent.

        Args:
            input: The input prompt/request
            context: Optional conversation history context

        Returns:
            The agent's response
        """
        pass
