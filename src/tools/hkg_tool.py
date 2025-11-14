"""
HKG (HealthKnowledgeGraph) retrieval tool.
"""

from typing import Union, Dict, Any
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from .base_tool import BaseRetrievalTool


class HKGRetrievalTool(BaseRetrievalTool):
    """Tool for retrieving symptom information from Health Knowledge Graph."""

    def __init__(self, faiss_path: str = "faiss_hkg", k: int = 1):
        super().__init__(
            name="hkg",
            description="For questions on symptoms using Health Knowledge Graph"
        )
        self.k = k
        self.vector_store = FAISS.load_local(
            faiss_path,
            OpenAIEmbeddings(model='text-embedding-ada-002'),
            allow_dangerous_deserialization=True
        )

    def retrieve(self, query: str) -> str:
        """
        Retrieve symptom information from HKG vector store.

        Args:
            query: The symptom-related query

        Returns:
            Retrieved symptom information as string
        """
        results = self.vector_store.similarity_search(query, k=self.k)
        if results:
            return results[0].page_content
        return "No reference found"


# Convenience function
def create_hkg_tool(faiss_path: str = "faiss_hkg", k: int = 1) -> HKGRetrievalTool:
    """Factory function to create HKG retrieval tool."""
    return HKGRetrievalTool(faiss_path=faiss_path, k=k)
