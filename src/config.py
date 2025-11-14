"""
Configuration settings for MultiMed-RAG system.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMConfig:
    """LLM configuration settings."""
    openai_api_key: str = os.getenv('OPENAI_API_KEY', '')
    openai_base_url: Optional[str] = os.getenv('OPENAI_BASE_URL')
    deepseek_api_key: str = os.getenv('DEEPSEEK_API_KEY', '')
    deepseek_base_url: Optional[str] = os.getenv('DEEPSEEK_BASE_URL')
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.0
    max_tokens: Optional[int] = None


@dataclass
class Neo4jConfig:
    """Neo4j database configuration."""
    url: str = "neo4j://43.140.200.9:7687"
    username: str = "neo4j"
    password: str = "20230408"
    refresh_schema: bool = False


@dataclass
class VectorStoreConfig:
    """Vector store configuration."""
    lmkg_path: str = "lmkg_faiss"
    hkg_path: str = "faiss_hkg"
    ds_path: str = "diseases_symptoms_faiss"
    primekg_path: str = "primekg_faiss"
    drugreviews_path: str = "drug_reviews_faiss"
    embedding_model: str = "text-embedding-3-small"
    embedding_model_legacy: str = "text-embedding-ada-002"


@dataclass
class AgentConfig:
    """Agent system configuration."""
    max_agents: int = 2  # For MCQ tasks
    max_agents_classification: int = 6  # For classification tasks
    recursion_limit: int = 100

    # Agent scopes
    agent_scopes: dict = None

    def __post_init__(self):
        if self.agent_scopes is None:
            self.agent_scopes = {
                "lmkg": "General medical queries using knowledge graph: diseases, exams, indicators, symptoms, complications etc.",
                "hkg": "For questions on symptom.",
                "ds": "For questions on symptoms or treatments.",
                "primekg": "To retrieve drugs indicated for diseases.",
                "drugreviews": "To retrieve drugs along with patient reviews.",
                "wiki": "For disease definitions and overviews.",
                "mayoclinic": "For clinical info: causes, treatments, symptoms, complications.",
                "llmself": "Fallback only if others are irrelevant."
            }


class Config:
    """Main configuration class."""

    def __init__(self):
        self.llm = LLMConfig()
        self.neo4j = Neo4jConfig()
        self.vectorstore = VectorStoreConfig()
        self.agent = AgentConfig()

    @classmethod
    def from_env(cls):
        """Create configuration from environment variables."""
        return cls()


# Global config instance
config = Config.from_env()
