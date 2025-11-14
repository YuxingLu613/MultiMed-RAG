"""
Base class for retrieval tools.
"""

from abc import ABC, abstractmethod
from typing import Any, Union, Dict


class BaseRetrievalTool(ABC):
    """Abstract base class for all retrieval tools."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def retrieve(self, query: str) -> Union[str, Dict[str, Any]]:
        """
        Retrieve information for the given query.

        Args:
            query: The search query

        Returns:
            Retrieved information as string or dictionary
        """
        pass

    def __call__(self, query: str) -> Union[str, Dict[str, Any]]:
        """Make the tool callable."""
        return self.retrieve(query)
