"""
Basic usage example for MultiMed-RAG system.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import config
from src.agents import QueryAgent, KnowledgeAgent
from src.tools import (
    create_hkg_tool,
    create_ds_tool,
    create_wiki_tool,
    create_llmself_tool
)
from langchain_openai import ChatOpenAI


def main():
    """Run a basic example of MultiMed-RAG."""

    print("=" * 60)
    print("MultiMed-RAG - Basic Usage Example")
    print("=" * 60)

    # Initialize LLM
    print("\n1. Initializing LLM...")
    llm = ChatOpenAI(
        model=config.llm.model_name,
        temperature=config.llm.temperature
    )
    print(f"   Using model: {config.llm.model_name}")

    # Create retrieval tools
    # Note: Some tools require pre-built FAISS indexes
    print("\n2. Creating retrieval tools...")
    tools = {
        # "hkg": create_hkg_tool(),  # Requires faiss_hkg index
        # "ds": create_ds_tool(),    # Requires diseases_symptoms_faiss index
        "wiki": create_wiki_tool(),
        "llmself": create_llmself_tool(llm)
    }
    print(f"   Available tools: {list(tools.keys())}")

    # Initialize agents
    print("\n3. Initializing agents...")
    query_agent = QueryAgent(llm)
    knowledge_agent = KnowledgeAgent(llm, tools, max_agents=2)
    print("   Query Agent and Knowledge Agent ready")

    # Example queries
    queries = [
        "What is diabetes?",
        "What are the symptoms of influenza?",
        "What medications are used to treat hypertension?"
    ]

    print("\n4. Running example queries...")
    print("=" * 60)

    for i, query in enumerate(queries, 1):
        print(f"\nQuery {i}: {query}")
        print("-" * 60)

        try:
            # Run knowledge agent
            references = knowledge_agent.run(query, recursion_limit=100)

            print("\nRetrieved References:")
            for agent_name, content in references.items():
                print(f"\n[{agent_name.upper()}]:")
                if isinstance(content, str):
                    # Truncate long outputs
                    content_preview = content[:300] + "..." if len(content) > 300 else content
                    print(content_preview)
                else:
                    print(content)

        except Exception as e:
            print(f"Error processing query: {e}")

        print("=" * 60)

    print("\nExample completed!")
    print("\nNote: Some tools require pre-built FAISS indexes.")
    print("See notebooks for complete setup instructions.")


if __name__ == "__main__":
    main()
