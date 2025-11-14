"""
Query Agent for planning and decomposing medical queries.
"""

from typing import Dict, Any
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

from .states import QState


class QueryAgent:
    """
    Query Agent that determines whether a question is single-step or multi-step
    and decomposes complex queries into sub-queries.
    """

    def __init__(self, llm):
        self.llm = llm
        self.planner_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a query planning agent for a medical knowledge system.
            Determine if the user's question is:

            1. "single-step" - Direct factual questions
               e.g., "What is diabetes?", "What are symptoms of flu?", "Which drug treats malaria?"

            2. "multi-step" - Complex questions needing multiple facts or reasoning
               e.g., "Compare treatment options for diabetes vs hypertension",
               "What's the best treatment for hypertension in a diabetic patient with renal impairment?"

            Respond with either "single-step" or "multi-step"."""),
            ("human", "{input}")
        ])
        self.planner_chain = LLMChain(llm=self.llm, prompt=self.planner_prompt)

    def planner_node(self, state: QState) -> Dict[str, Any]:
        """Determines if query is single-step or multi-step."""
        question = next(
            (msg.content for msg in reversed(state["messages"])
             if msg.type == "human" and not hasattr(msg, 'name')),
            None
        )

        if question is None:
            question = next(
                (msg.content for msg in state["messages"] if msg.type == "human"),
                "No question found"
            )

        result = self.planner_chain.invoke({"input": question})['text']

        # Check if it's single-step and preserve the original question
        if "single-step" in result.lower():
            return {
                "messages": [
                    HumanMessage(content=result, name="planner"),
                    HumanMessage(content=question, name="single_step")
                ],
                "planner_executed": True
            }
        else:
            return {
                "messages": [
                    HumanMessage(content=result, name="planner")
                ],
                "planner_executed": True
            }

    def multi_step_node(self, state: QState) -> Dict[str, Any]:
        """Decomposes multi-step queries into sub-queries."""
        original_question = None
        for msg in state["messages"]:
            if msg.type == "human" and not hasattr(msg, 'name'):
                original_question = msg.content
                break

        if not original_question:
            for msg in state["messages"]:
                if msg.type == "human":
                    original_question = msg.content
                    break

        if not original_question:
            original_question = "No question found"

        subquery_prompt = f"""
        Original query: {original_question}

        Break the medical query into exactly two sub-queries.
        Each sub-query should:
        Be SIMPLE and SPECIFIC;
        Focus on a different, narrow aspect of the original query;
        Avoid long or reasoning-based formulations.

        Format your response as:
        1. [sub-query 1]
        2. [sub-query 2]
        """

        result = self.llm.invoke(subquery_prompt)

        return {
            "messages": [
                HumanMessage(content=result.content, name="subquery")
            ]
        }

    def build_graph(self) -> StateGraph:
        """Builds the query agent graph."""
        builder = StateGraph(QState)
        builder.add_node("planner", self.planner_node)
        builder.add_node("multi_step", self.multi_step_node)

        builder.add_edge(START, "planner")

        builder.add_conditional_edges(
            "planner",
            lambda state: self._determine_planner_decision(state),
            {
                "single_step": END,
                "multi_step": "multi_step"
            }
        )

        builder.add_edge("multi_step", END)

        return builder.compile()

    @staticmethod
    def _determine_planner_decision(state: QState) -> str:
        """Determines the planner's decision from state."""
        planner_message = None
        for msg in reversed(state["messages"]):
            if hasattr(msg, 'name') and msg.name == "planner":
                planner_message = msg
                break

        if planner_message:
            planner_decision = planner_message.content.strip().lower()

            if "single-step" in planner_decision:
                return "single_step"
            elif "multi-step" in planner_decision:
                return "multi_step"

        return "single_step"
