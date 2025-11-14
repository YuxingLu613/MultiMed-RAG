"""
Wikipedia retrieval tool.
"""

import os
from openai import OpenAI
from ..utils.wiki_crawler import crawl_wikipedia_entity
from .base_tool import BaseRetrievalTool


class WikiRetrievalTool(BaseRetrievalTool):
    """Tool for retrieving disease definitions and overviews from Wikipedia."""

    def __init__(self, articles_limit: int = 1, max_chars: int = 1500):
        super().__init__(
            name="wiki",
            description="For disease definitions and overviews from Wikipedia"
        )
        self.articles_limit = articles_limit
        self.max_chars = max_chars

        # Initialize DeepSeek client for entity extraction
        self.client = OpenAI(
            api_key=os.environ.get("DEEPSEEK_API_KEY"),
            base_url=os.environ.get("DEEPSEEK_BASE_URL")
        )

    def extract_entity(self, query: str) -> str:
        """Extract the main entity from the query."""
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{
                "role": "user",
                "content": f"What is the main entity or concept in this query: '{query}'? "
                          f"Extract only the core term (e.g., 'hyponatremia', not 'causes of hyponatremia'). "
                          f"Return only the entity name in one line."
            }]
        )
        entity = response.choices[0].message.content.strip()
        print(f'Extracted entity: {entity}')
        return entity.replace(" ", "_")

    def retrieve(self, query: str) -> str:
        """
        Retrieve Wikipedia information.

        Args:
            query: The medical query

        Returns:
            Retrieved Wikipedia text (truncated to max_chars)
        """
        entity = self.extract_entity(query)
        wiki_text = crawl_wikipedia_entity(entity, articles_limit=self.articles_limit)
        return wiki_text[:self.max_chars] if wiki_text else "No information found"


def create_wiki_tool(articles_limit: int = 1, max_chars: int = 1500) -> WikiRetrievalTool:
    """Factory function to create Wiki retrieval tool."""
    return WikiRetrievalTool(articles_limit=articles_limit, max_chars=max_chars)
