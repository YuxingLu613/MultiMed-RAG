"""
MultiMed-RAG: Multi-Agent Medical Retrieval-Augmented Generation System
A comprehensive medical question-answering system using multiple knowledge sources.
"""

__version__ = "1.0.0"
__author__ = "MultiMed-RAG Team"

from .agents import QueryAgent, KnowledgeAgent
from .tools import (
    LMKGRetrievalTool,
    HKGRetrievalTool,
    DSRetrievalTool,
    PrimeKGRetrievalTool,
    DrugReviewsRetrievalTool,
    WikiRetrievalTool,
    MayoClinicRetrievalTool,
    LLMSelfTool
)

__all__ = [
    "QueryAgent",
    "KnowledgeAgent",
    "LMKGRetrievalTool",
    "HKGRetrievalTool",
    "DSRetrievalTool",
    "PrimeKGRetrievalTool",
    "DrugReviewsRetrievalTool",
    "WikiRetrievalTool",
    "MayoClinicRetrievalTool",
    "LLMSelfTool"
]
