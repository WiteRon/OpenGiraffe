"""
Base RAG interface for Ragflow integration (future extension).

When ready to add Ragflow RAG:
1. Add ragflow client to requirements.txt
2. Implement RagflowRetriever class in this module
3. Create a RAGAugmentedChatProvider that wraps a ChatProvider
4. Update container.py to use the augmented provider
"""

from abc import ABC, abstractmethod
from typing import list


class BaseRetriever(ABC):
    """
    Abstract base class for document retrievers.

    Retrievers fetch relevant documents from a knowledge base
    to augment LLM prompts with external context.
    """

    @abstractmethod
    async def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: The user query
            top_k: Number of documents to retrieve

        Returns:
            List of relevant document chunks
        """
        pass
