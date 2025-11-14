"""
Supervisor node for coordinating agent selection.
"""

from typing import List, Dict, TypedDict
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.types import Command
from langgraph.graph import END

from .states import KnowledgeState


class Router(TypedDict):
    """Router output schema."""
    next: str


class SupervisorNode:
    """
    Supervisor that routes between agents for reference retrieval.
    """

    def __init__(
        self,
        llm: BaseChatModel,
        members: List[str],
        max_agents: int = 2,
        agent_scopes: Dict[str, str] = None
    ):
        self.llm = llm
        self.members = members
        self.max_agents = max_agents

        if agent_scopes is None:
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
        else:
            self.agent_scopes = agent_scopes

    def create_node(self):
        """Creates the supervisor node function."""

        def supervisor_node(state: KnowledgeState) -> Command:
            """Routes to agents for reference retrieval only."""
            # Get the original question
            if not state.get("original_question"):
                original_question = next(
                    msg.content for msg in state["messages"]
                    if msg.type == "human"
                )
            else:
                original_question = state["original_question"]

            completed_agents = state.get("completed_agents", [])
            references = state.get("references", {})
            excluded_agents = state.get("excluded_agents", [])

            # Fallback replacement logic
            if "llmself" not in completed_agents and "llmself" in self.members:
                for agent in completed_agents:
                    ref = references.get(agent, "")
                    is_no_info = ref == "No information retrieved"
                    is_empty_cypher = (
                        isinstance(ref, dict)
                        and "generated_cypher" in ref
                        and (
                            not ref.get("retrieved_result")
                            or (isinstance(ref.get("retrieved_result"), list)
                                and not any(str(r).strip() for r in ref["retrieved_result"]))
                        )
                    )
                    if is_no_info or is_empty_cypher:
                        print(f"⚠️ Replacing low-quality agent '{agent}' with fallback agent 'llmself'.")

                        completed_agents.remove(agent)
                        references.pop(agent, None)
                        excluded_agents.append(agent)

                        return Command(goto="llmself", update={
                            "next": "llmself",
                            "original_question": original_question,
                            "completed_agents": completed_agents,
                            "excluded_agents": excluded_agents
                        })

            # Check if we have enough references
            if len(completed_agents) >= self.max_agents:
                return Command(goto=END, update={
                    "next": "FINISH",
                    "original_question": original_question
                })

            available_agents = [agent for agent in self.members]
            remaining_agents = [
                agent for agent in available_agents
                if agent not in completed_agents and agent not in excluded_agents
            ]

            # Check if all agents have been completed
            if not remaining_agents:
                return Command(goto=END, update={
                    "next": "FINISH",
                    "original_question": original_question
                })

            # Create agent scope descriptions for remaining agents
            remaining_agent_scopes = {
                agent: self.agent_scopes.get(agent, "General purpose agent")
                for agent in remaining_agents
            }

            options = ["FINISH"] + remaining_agents

            # System prompt for agent selection
            system_prompt = self._build_system_prompt(
                completed_agents,
                remaining_agents,
                remaining_agent_scopes,
                options
            )

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Question: {original_question}\n\nSelect the most relevant agent:"}
            ]

            response = self.llm.with_structured_output(Router).invoke(messages)
            goto = response["next"]

            print(f"Question: {original_question}")
            print(f"Remaining agents: {remaining_agents}")
            print(f"LLM selected: {goto}")
            print(f"Valid options: {options}")

            # Validate response
            if goto not in options:
                print(f"Warning: Invalid selection '{goto}'. Defaulting to FINISH.")
                goto = "FINISH"

            if goto == "FINISH":
                goto = END

            return Command(goto=goto, update={
                "next": goto,
                "original_question": original_question
            })

        return supervisor_node

    def _build_system_prompt(
        self,
        completed_agents: List[str],
        remaining_agents: List[str],
        remaining_agent_scopes: Dict[str, str],
        options: List[str]
    ) -> str:
        """Builds the system prompt for agent selection."""
        prompt = (
            f"You are a supervisor selecting the top {self.max_agents} agents for medical reference retrieval. "
            f"Choose one agent at a time based on query relevance.\n\n"
            f"Agent options and specialties:\n"
        )

        for agent, scope in remaining_agent_scopes.items():
            prompt += f"- {agent}: {scope}\n"

        prompt += (
            f"\nCompleted agents: {completed_agents} (Target: {self.max_agents} agents)\n"
            f"Available agents: {remaining_agents}\n\n"
            f"GOAL: Select the {self.max_agents} MOST RELEVANT agents.\n"
            f"Progress: {len(completed_agents)}/{self.max_agents} done\n\n"
            f"Instructions:\n"
            f"1. If {self.max_agents} agents are done, select FINISH\n"
            f"2. Choose the most relevant agent from remaining\n"
            f"3. Prioritize by question type:\n"
            f"   - Symptoms: hkg > ds > mayoclinic\n"
            f"   - Causes: mayoclinic > wiki\n"
            f"   - Diagnosis: mayoclinic > ds\n"
            f"   - Medications: drugreviews > primekg > lmkg\n"
            f"   - Treatments: ds > mayoclinic\n"
            f"   - Complications: lmkg > mayoclinic\n"
            f"   - Examinations/tests: lmkg > ds\n"
            f"   - Definition/overview: wiki > mayoclinic\n"
            f"   - Fallback (only if others unsuitable): llmself\n"
            f"4. Pick the next best from: {remaining_agents}\n\n"
            f"DO NOT select any agents not listed in 'Valid responses' below.\n\n"
            f"Valid responses: {options}\n"
            f"Use {self.max_agents} best agents, then FINISH."
        )

        return prompt
