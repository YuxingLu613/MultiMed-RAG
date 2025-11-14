"""
Knowledge Agent for coordinating multiple knowledge sources.
"""

from typing import Dict, Any, List
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

from .states import KnowledgeState
from .supervisor import SupervisorNode


class KnowledgeAgent:
    """
    Knowledge Agent that coordinates multiple specialized knowledge retrieval agents
    to gather relevant medical information.
    """

    def __init__(self, llm, tools: Dict, max_agents: int = 2):
        """
        Initialize Knowledge Agent.

        Args:
            llm: Language model instance
            tools: Dictionary of retrieval tools {agent_name: tool_function}
            max_agents: Maximum number of agents to use for retrieval
        """
        self.llm = llm
        self.tools = tools
        self.max_agents = max_agents
        self.available_agents = list(tools.keys())

        # Create supervisor
        self.supervisor = SupervisorNode(
            llm=llm,
            members=self.available_agents,
            max_agents=max_agents
        )

    def create_agent_node(self, agent_name: str):
        """Creates a node function for a specific agent."""

        def agent_node(state: KnowledgeState) -> Dict[str, Any]:
            question = state.get("original_question") or next(
                msg.content for msg in state["messages"]
                if msg.type == "human"
            )

            # Retrieve reference using the tool
            tool = self.tools[agent_name]
            reference = tool(question)

            # Update references and completed agents
            references = state.get("references", {})
            references[agent_name] = reference

            completed_agents = state.get("completed_agents", [])
            if agent_name not in completed_agents:
                completed_agents.append(agent_name)

            return {
                "messages": [
                    HumanMessage(content=f"{agent_name} reference retrieved", name=agent_name)
                ],
                "completed_agents": completed_agents,
                "references": references
            }

        return agent_node

    def build_graph(self) -> StateGraph:
        """Builds the knowledge agent graph with supervisor and workers."""
        builder = StateGraph(KnowledgeState)

        # Add supervisor node
        builder.add_node("supervisor", self.supervisor.create_node())

        # Add worker nodes for each agent
        for agent_name in self.available_agents:
            builder.add_node(agent_name, self.create_agent_node(agent_name))

        # Start with supervisor
        builder.add_edge(START, "supervisor")

        # Conditional edges from supervisor to workers
        routing_dict = {agent: agent for agent in self.available_agents}
        routing_dict["FINISH"] = END
        routing_dict[END] = END

        builder.add_conditional_edges(
            "supervisor",
            lambda state: state["next"],
            routing_dict
        )

        # All workers return to supervisor
        for agent_name in self.available_agents:
            builder.add_edge(agent_name, "supervisor")

        return builder.compile()

    def run(self, query: str, recursion_limit: int = 100) -> Dict[str, Any]:
        """
        Run the knowledge agent to retrieve references.

        Args:
            query: The medical question
            recursion_limit: Maximum graph recursion depth

        Returns:
            Dictionary containing retrieved references from multiple agents
        """
        graph = self.build_graph()

        final_state = None
        for s in graph.stream(
            {"messages": [("user", query)]},
            {"recursion_limit": recursion_limit}
        ):
            for key, value in s.items():
                if isinstance(value, dict) and 'references' in value:
                    if final_state is None:
                        final_state = {}
                    final_state.update(value)

        return final_state.get('references', {}) if final_state else {}
