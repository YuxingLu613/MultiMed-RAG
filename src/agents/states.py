"""
State definitions for the agent system.
"""

from typing import List, Dict
from langgraph.graph import MessagesState


class QState(MessagesState):
    """State for Query Agent."""
    next: str
    planner_executed: bool = False


class KnowledgeState(MessagesState):
    """State for Knowledge Agent."""
    next: str
    original_question: str = ""
    references: Dict = {}
    completed_agents: List = []
    excluded_agents: List = []
