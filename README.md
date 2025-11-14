# MultiMed-RAG: Multi-Agent Medical Retrieval-Augmented Generation

A comprehensive multi-agent system for medical question answering that leverages multiple knowledge sources including knowledge graphs, vector databases, and web scraping to provide accurate medical information.

## 🏥 Overview

MultiMed-RAG is an advanced medical question-answering system that:

- **Multi-Agent Architecture**: Coordinates multiple specialized agents for different medical knowledge sources
- **Hybrid Retrieval**: Combines vector search, graph databases (Neo4j), and web scraping
- **Query Planning**: Automatically determines if queries are single-step or multi-step and decomposes complex questions
- **Knowledge Source Integration**: Integrates 8+ medical knowledge sources including:
  - LMKG (Lightweight Medical Knowledge Graph)
  - HKG (Health Knowledge Graph)
  - Disease-Symptom databases
  - PrimeKG (drug indications)
  - Drug Reviews
  - Wikipedia medical articles
  - Mayo Clinic clinical information
  - LLM internal knowledge (fallback)

## 📋 Features

### Query Agent
- Classifies queries as single-step or multi-step
- Decomposes complex medical questions into sub-queries
- Optimizes retrieval strategy based on query complexity

### Knowledge Agent
- Supervisor-based agent coordination
- Selects the most relevant knowledge sources for each query
- Fallback mechanism for low-quality retrievals
- Configurable number of agents (2 for MCQ, 6 for classification tasks)

### Retrieval Tools
- **LMKG**: Knowledge graph queries using Cypher and vector search
- **HKG**: Symptom-focused retrieval
- **DS**: Disease-symptom associations
- **PrimeKG**: Drug-disease relationships
- **Drug Reviews**: Patient reviews and drug information
- **Wikipedia**: Medical entity definitions
- **Mayo Clinic**: Clinical symptoms, causes, treatments
- **LLM Self**: Fallback using LLM's internal knowledge

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd MultiMed-RAG

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# Neo4j Configuration
NEO4J_URL=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

### Basic Usage

```python
from src.config import config
from src.agents import QueryAgent, KnowledgeAgent
from src.tools import create_hkg_tool, create_ds_tool, create_wiki_tool, create_llmself_tool
from langchain_openai import ChatOpenAI

# Initialize LLM
llm = ChatOpenAI(model=config.llm.model_name)

# Create tools
tools = {
    "hkg": create_hkg_tool(),
    "ds": create_ds_tool(),
    "wiki": create_wiki_tool(),
    "llmself": create_llmself_tool(llm)
}

# Initialize agents
query_agent = QueryAgent(llm)
knowledge_agent = KnowledgeAgent(llm, tools, max_agents=2)

# Run query
query = "What are the symptoms of diabetes?"
references = knowledge_agent.run(query)
print(references)
```

## 📁 Project Structure

```
MultiMed-RAG/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── query_agent.py     # Query planning and decomposition
│   │   ├── knowledge_agent.py # Knowledge retrieval coordination
│   │   ├── supervisor.py      # Agent selection supervisor
│   │   └── states.py          # State definitions
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base_tool.py       # Base retrieval tool class
│   │   ├── hkg_tool.py        # Health Knowledge Graph tool
│   │   ├── ds_tool.py         # Disease-Symptom tool
│   │   ├── lmkg_tool.py       # Medical Knowledge Graph tool
│   │   ├── primekg_tool.py    # PrimeKG drug tool
│   │   ├── drugreviews_tool.py
│   │   ├── wiki_tool.py       # Wikipedia crawler tool
│   │   ├── mayoclinic_tool.py # Mayo Clinic scraper tool
│   │   └── llmself_tool.py    # LLM fallback tool
│   └── utils/
│       ├── __init__.py
│       ├── wiki_crawler.py    # Wikipedia web scraper
│       └── mayoclinic_crawler.py  # Mayo Clinic web scraper
├── notebooks/
│   ├── Final_MCQ.ipynb        # MCQ question answering
│   ├── Final_Classification_Context.ipynb
│   └── Final_Classification_Result.ipynb
├── data/                      # Data files (not included)
├── config/                    # Configuration files
├── tests/                     # Unit tests
├── examples/                  # Example scripts
├── requirements.txt
├── .gitignore
└── README.md
```

## 🔬 Evaluation

The system has been evaluated on multiple medical QA datasets:

- **MedQA** (510 questions, 5% sample)
- **MedMCQA** (545 questions)
- **DDXPlus** (400 questions, diagnosis classification)
- **SymptomsDisease** (486 questions)
- **Symptom2Disease** (212 questions)

Results show improved performance using multi-agent retrieval compared to single-source baselines.

## 📊 Use Cases

### 1. Multiple Choice Questions (MCQ)
```python
# Suitable for: MedQA, MedMCQA, NEJM-style questions
query = """
A 55-year-old man presents with chest pain and shortness of breath.
What is the most likely diagnosis?
A. Myocardial infarction
B. Pneumonia
C. GERD
D. Anxiety
"""
# System retrieves from 2 most relevant sources
```

### 2. Disease Diagnosis
```python
# Suitable for: DDXPlus, symptom-based diagnosis
query = "Patient has fever, cough, and fatigue. What could be the diagnosis?"
# System retrieves from up to 6 knowledge sources
```

### 3. Medical Information Lookup
```python
query = "What are the complications of diabetes?"
# System automatically selects best knowledge sources (e.g., LMKG, Mayo Clinic)
```

## 🛠️ Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/
flake8 src/
```

### Type Checking
```bash
mypy src/
```

## 📝 Data Requirements

The system requires several pre-built vector stores and knowledge bases:

1. **FAISS Indexes**: Pre-built vector stores for HKG, DS, PrimeKG, Drug Reviews
2. **Neo4j Database**: LMKG knowledge graph (optional)
3. **Web Access**: For Wikipedia and Mayo Clinic scraping

See the notebooks for detailed instructions on building these resources.

## ⚙️ Configuration

Key configuration options in `src/config.py`:

- `max_agents`: Number of agents to use for retrieval (default: 2 for MCQ, 6 for classification)
- `model_name`: LLM model to use (default: gpt-4o-mini)
- `recursion_limit`: Max graph recursion depth
- `agent_scopes`: Define which agents handle which types of queries

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📚 Citation

If you use this work, please cite:

```bibtex
@software{multimed_rag,
  title={MultiMed-RAG: Multi-Agent Medical Retrieval-Augmented Generation},
  author={MultiMed-RAG Team},
  year={2024},
  url={https://github.com/yourusername/MultiMed-RAG}
}
```

## 🔗 Related Work

- [LangChain](https://github.com/langchain-ai/langchain)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [FAISS](https://github.com/facebookresearch/faiss)
- [Neo4j](https://neo4j.com/)

## 📧 Contact

For questions or issues, please open a GitHub issue or contact the maintainers.

---

**Note**: This system is for research and educational purposes only. Always consult qualified healthcare professionals for medical advice.
