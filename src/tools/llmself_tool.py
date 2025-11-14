"""
LLM Self tool - uses the LLM's internal knowledge.
"""

from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate

from .base_tool import BaseRetrievalTool


class LLMSelfTool(BaseRetrievalTool):
    """Fallback tool that uses LLM's internal knowledge."""

    def __init__(self, llm):
        super().__init__(
            name="llmself",
            description="Fallback agent using LLM internal knowledge"
        )
        self.llm = llm

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a knowledgeable AI. Answer concisely and precisely using only your internal knowledge. No external context."),
            ("human", "{input}")
        ])
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def retrieve(self, query: str) -> str:
        """
        Generate answer using LLM's internal knowledge.

        Args:
            query: The medical question

        Returns:
            LLM-generated answer
        """
        return self.chain.invoke({"input": query})['text']


def create_llmself_tool(llm) -> LLMSelfTool:
    """Factory function to create LLMSelf tool."""
    return LLMSelfTool(llm=llm)
