"""
Mayo Clinic retrieval tool.
"""

from .base_tool import BaseRetrievalTool


class MayoClinicRetrievalTool(BaseRetrievalTool):
    """Tool for retrieving clinical information from Mayo Clinic."""

    def __init__(self):
        super().__init__(
            name="mayoclinic",
            description="For clinical info: causes, treatments, symptoms, complications from Mayo Clinic"
        )

    def retrieve(self, query: str) -> str:
        """
        Retrieve from Mayo Clinic.

        Note: Full implementation in notebooks using mayoclinic_crawler.

        Args:
            query: The medical query

        Returns:
            Retrieved clinical information
        """
        # Placeholder - see utils/mayoclinic_crawler.py and notebooks for full implementation
        return "Mayo Clinic retrieval - see utils/mayoclinic_crawler.py for implementation"


def create_mayoclinic_tool() -> MayoClinicRetrievalTool:
    """Factory function to create Mayo Clinic retrieval tool."""
    return MayoClinicRetrievalTool()
