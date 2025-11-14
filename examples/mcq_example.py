"""
Example for Multiple Choice Question (MCQ) answering.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import config
from src.agents import QueryAgent, KnowledgeAgent
from langchain_openai import ChatOpenAI


def run_mcq_example():
    """
    Example of using MultiMed-RAG for MCQ questions.

    For MCQ tasks, the system:
    1. Uses Query Agent to determine if question is single/multi-step
    2. Uses Knowledge Agent with max_agents=2 to retrieve from 2 best sources
    3. Combines references to answer the question
    """

    print("=" * 70)
    print("MultiMed-RAG - MCQ Example")
    print("=" * 70)

    # Initialize LLM
    llm = ChatOpenAI(model=config.llm.model_name)

    # Example MCQ query
    mcq_query = """
    A 3-day-old male newborn is brought to the physician because of poor feeding
    and irritability. He was born at 36 weeks' gestation and weighed 2466 g
    (5 lb 7 oz). The mother did not adhere to her prenatal care schedule.
    His temperature is 37.2°C (99°F). Physical examination shows scleral icterus
    and jaundice of the skin. The abdomen is mildly distended. The liver is
    palpated 3 cm below the right costal margin and the spleen tip is palpated
    just below the left costal margin. Laboratory studies show:

    Hemoglobin: 11.8 g/dL
    Leukocyte count: 7,300/mm³
    Platelet count: 62,000/mm³
    Prothrombin time: 24 seconds
    Partial thromboplastin time: 44 seconds
    Serum bilirubin (total): 11.3 mg/dL
    Direct: 8.1 mg/dL

    Which of the following is the most likely causal organism?
    A. Parvovirus B19
    B. Rubella virus
    C. Herpes simplex virus
    D. Cytomegalovirus
    E. Toxoplasma gondii
    """

    print(f"\nQuery:\n{mcq_query}")
    print("\n" + "=" * 70)

    # Step 1: Query Agent - determine if single/multi-step
    print("\nStep 1: Query Planning...")
    query_graph = query_agent.build_graph()

    message_contents = []
    for s in query_graph.stream(
        {"messages": [("user", mcq_query)]},
        {"recursion_limit": 100}
    ):
        if 'messages' in str(s):
            for key, value in s.items():
                if isinstance(value, dict) and 'messages' in value:
                    for msg in value['messages']:
                        message_contents.append(msg.content)

    if message_contents:
        print(f"Query type: {message_contents[0]}")

    # Step 2: Knowledge Agent - retrieve from best sources
    print("\nStep 2: Retrieving knowledge from relevant sources...")
    print("Note: This example uses llmself tool. For full functionality,")
    print("      set up FAISS indexes for other knowledge sources.")

    # In production, you would:
    # 1. Get references from knowledge_agent.run(mcq_query)
    # 2. Pass references to a Verifier agent (filters low-quality refs)
    # 3. Pass verified references to a Summarizer agent (generates final answer)

    print("\n" + "=" * 70)
    print("For complete MCQ pipeline, see notebooks/Final_MCQ.ipynb")
    print("=" * 70)


if __name__ == "__main__":
    run_mcq_example()
