Autonomous AI Research Agent

The Autonomous AI Research Agent is an end-to-end automated research system.
It takes a user-defined research goal, decomposes it into subtasks, performs autonomous web and scientific research using Tavily Search API and Arxiv, stores knowledge in a vector memory, and finally generates a professional final research report automatically.

Features
Capability	Status
Automatic task planning	✔
Autonomous execution of research subtasks	✔
Web research via Tavily API	✔
Scientific paper retrieval via Arxiv	✔
Vector memory storage + semantic search	✔
FastAPI backend	✔
LangChain LLM orchestration	✔
Browser-based frontend	✔
Automatic final report generation	✔
How It Works

User enters a research goal in the frontend.

The Planning Agent generates subtasks required to achieve the goal.

Each subtask executes automatically:

Queries Tavily for real-time web research

Queries Arxiv for scientific research papers

Extracts findings and relevant sources

Stores insights in vector memory

When all subtasks are completed, a professional final report is synthesized from all findings.

Tech Stack
Layer	Technology
Backend	FastAPI
LLM Framework	LangChain
Web Search	Tavily API
Scientific Papers	Arxiv
Vector Memory	FAISS / Chroma / Pinecone (configurable)
Frontend	HTML + CSS + JavaScript
LLM	Plug-and-play through llm_factory.py (Groq / OpenAI / DeepSeek / Local etc.)
Project Structure
/backend
  main.py
  /agents
    planner_agent.py
    executor_agent.py
    retriever_agent.py
  /memory
    vector_memory.py
  /utils
    llm_factory.py
    prompts.py

/frontend
  index.html
  style.css
  script.js

Installation
git clone https://github.com/<your-username>/<your-repository>.git
cd <your-repository>

Create virtual environment
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows

Install dependencies
pip install -r requirements.txt

Configure API keys

Create a .env file inside the backend/ directory:

TAVILY_API_KEY=your_key
ARXIV_ENABLED=1
LLM_PROVIDER=groq/openai/deepseek/etc
GROQ_API_KEY=your_key_here (if using groq)

Run the App
Backend
uvicorn backend.main:app --reload --port 8000

Frontend

Open frontend/index.html in a browser
(or use VSCode Live Server for auto-reload).

Usage

Enter a research goal

Click Generate Plan

Click Run All Tasks (Auto) or run subtasks individually

When complete, the Final Report panel appears

Export the report as PDF if needed

Example Prompts

Good prompts:

Recent progress in cancer immunotherapy since 2022 with clinical outcomes.
Economic effect of AI automation in manufacturing from 2021–2024.
Advancements in lithium-ion battery recycling technologies and CO₂ reduction.


Bad prompts:

Tell me about cancer.
Explain AI.
Electric car info.

Future Roadmap
Feature	Status
PDF export	✔
Session-based multi-user support	⏳
Full research citations	⏳
Auto memory visualization UI	⏳
Contributing

Pull requests are welcome.

Fork → Create branch → Commit → Open PR

License

This project is open-source.
Use and modify for research and educational purposes.

If this project is helpful, starring the repository is appreciated.
