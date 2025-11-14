"""
DS (Diseases-Symptoms) retrieval tool.
"""

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from .base_tool import BaseRetrievalTool


class DSRetrievalTool(BaseRetrievalTool):
    """Tool for retrieving disease-symptom information."""

    def __init__(self, faiss_path: str = "diseases_symptoms_faiss", k: int = 1):
        super().__init__(
            name="ds",
            description="For questions on symptoms or treatments"
        )
        self.k = k
        self.vector_store = FAISS.load_local(
            faiss_path,
            OpenAIEmbeddings(model='text-embedding-ada-002'),
            allow_dangerous_deserialization=True
        )

    def retrieve(self, query: str) -> str:
        """
        Retrieve disease-symptom information.

        Args:
            query: The query about diseases or symptoms

        Returns:
            Retrieved information as string
        """
        results = self.vector_store.similarity_search(query, k=self.k)
        if results:
            return results[0].page_content
        return "No reference found"


def create_ds_tool(faiss_path: str = "diseases_symptoms_faiss", k: int = 1) -> DSRetrievalTool:
    """Factory function to create DS retrieval tool."""
    return DSRetrievalTool(faiss_path=faiss_path, k=k)
