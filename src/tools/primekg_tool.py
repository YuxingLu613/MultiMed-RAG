"""
PrimeKG retrieval tool - for drug indications.
"""

from .base_tool import BaseRetrievalTool


class PrimeKGRetrievalTool(BaseRetrievalTool):
    """Tool for retrieving drugs indicated for diseases from PrimeKG."""

    def __init__(self):
        super().__init__(
            name="primekg",
            description="To retrieve drugs indicated for diseases from PrimeKG"
        )

    def retrieve(self, query: str) -> str:
        """
        Retrieve drug indications from PrimeKG.

        Note: Full implementation requires FAISS vector store.
        See notebooks for complete implementation.

        Args:
            query: The medical query

        Returns:
            Drug indication information
        """
        return "PrimeKG retrieval - requires FAISS vector store setup"


def create_primekg_tool() -> PrimeKGRetrievalTool:
    """Factory function to create PrimeKG retrieval tool."""
    return PrimeKGRetrievalTool()
