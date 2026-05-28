# Goal-Oriented Autonomous Research Agent

> A modular, multi-agent AI research system that mimics a human research assistant — breaking complex goals into structured subtasks, retrieving real-world evidence, storing findings in persistent memory, and synthesizing a professional final report.

---

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Core Modules](#core-modules)
- [API Reference](#api-reference)
- [Frontend](#frontend)
- [Tech Stack](#tech-stack)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [Roadmap](#roadmap)
- [Author](#author)

---

## Overview

Traditional LLM-based tools answer questions in a single shot. This project takes a fundamentally different approach — it acts as an **autonomous research pipeline** that:

- Decomposes a high-level research goal into structured, actionable subtasks using LLM-driven planning
- Retrieves real-world evidence from live web sources (Tavily) and scientific databases (ArXiv)
- Synthesizes professional findings for each subtask using a dedicated Executor Agent
- Stores all findings in a persistent vector memory (ChromaDB) with auto-generated semantic tags
- Produces a structured 6-section final research report via a Synthesizer Agent
- Exposes everything through a clean FastAPI REST backend with a real-time HTML/CSS/JS frontend

---

## System Architecture

```
User (Frontend)
       │
       ▼
  FastAPI Backend (main.py)
       │
       ▼
  Planner Agent
  (LLM decomposes goal → JSON subtasks)
       │
       ▼
  Executor Agent (per subtask)
       ├──► Retriever Agent
       │         ├── Tavily Web Search (live results)
       │         └── ArXiv API (scientific papers)
       │
       ├──► LLM Synthesis (findings from retrieved context)
       │
       └──► Memory Tagger (LLM generates semantic tags)
                  │
                  ▼
           ResearchMemory (ChromaDB)
           (persisted to disk with HuggingFace embeddings)
                  │
                  ▼
       Synthesizer Agent
       (builds final 6-section report from all findings)
                  │
                  ▼
       Frontend (real-time task visualization + PDF export)
```

---

## Project Structure

```
Goal-Oriented-Research-Agent/
│
├── Frontend/
│   ├── index.html              # Main UI layout
│   ├── style.css               # Styling and responsive design
│   └── script.js               # Frontend logic, API calls, task rendering
│
├── backend/
│   ├── main.py                 # FastAPI app entry point, all REST endpoints
│   │
│   ├── agents/
│   │   ├── planner_agent.py    # Goal → structured JSON subtask plan
│   │   ├── retriever_agent.py  # Tavily web search + ArXiv paper retrieval
│   │   ├── executor_agent.py   # Per-task: retrieval + synthesis + memory tagging
│   │   └── synthesizer_agent.py# Final 6-section research report generation
│   │
│   ├── memory/
│   │   └── vector_db.py        # ChromaDB wrapper (add, search, persist)
│   │
│   ├── utils/
│   │   ├── llm_factory.py      # Groq API + LLaMA 3.1 initialization
│   │   └── prompts.py          # All system prompts (Planner, Executor, Tagger, Report)
│   │
│   └── data/
│       └── chroma_store/       # ChromaDB persistent vector storage (auto-created)
│
├── .env                        # API keys (not committed)
├── requirements.txt            # Python dependencies
└── README.md
```

---

## Core Modules

### 1. Planner Agent — `backend/agents/planner_agent.py`

Takes a high-level research goal and uses the LLM to produce a structured JSON plan of subtasks.

Each subtask contains:
- `id` — unique identifier (task-1, task-2, ...)
- `title` — short headline of the subtask
- `description` — what the researcher must find
- `search_query` — keyword query for retrieval

The planner uses a safety parser that extracts only the valid JSON section from the LLM response, preventing malformed output from crashing the pipeline.

---

### 2. Retriever Agent — `backend/agents/retriever_agent.py`

Fetches real-world evidence from two external sources per subtask:

**Tavily Web Search**
- Live internet search returning top 6 results
- Each result includes URL, title, and content snippet

**ArXiv Scientific Papers**
- Queries ArXiv's public API for up to 4 academic papers
- Parses RSS feed via `feedparser`
- Provides peer-reviewed evidence for research-heavy topics

**Fallback**
- If both sources fail, the agent generates a knowledge-based fallback so the pipeline never halts

---

### 3. Executor Agent — `backend/agents/executor_agent.py`

Orchestrates the full execution of a single subtask in three steps:

**Step 1 — Retrieve**
Calls the Retriever Agent to fetch live web + ArXiv content for the task's search query.

**Step 2 — Synthesize**
Passes the retrieved context to the LLM with the `RESEARCH_SYNTHESIS_PROMPT` to generate structured findings with sections: Introduction, Key Insights, Evidence Summary, and Conclusion.

**Step 3 — Memory Tagging**
Sends the findings to the LLM with the `MEMORY_TAGGING_PROMPT` to extract 3–6 short semantic tags (e.g. "transformer architecture", "RAG pipeline"). Tags are parsed from JSON safely.

Returns: `{ findings, sources, tags }`

---

### 4. Synthesizer Agent — `backend/agents/synthesizer_agent.py`

After all subtasks are executed, the Synthesizer Agent takes the original goal and all task findings and produces a final structured report with six sections:

1. Executive Summary
2. Methodology
3. Key Findings
4. Detailed Analysis
5. Limitations
6. Conclusion

The report uses only verified findings — no fabrication. Tone is academic and objective.

---

### 5. Research Memory — `backend/memory/vector_db.py`

A persistent vector memory layer built on ChromaDB and HuggingFace embeddings.

**Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2`

**Capabilities:**
- `add_memory(content, metadata)` — embeds and stores a finding with task metadata and tags
- `search_memory(query, k)` — semantic similarity search returning top-k relevant past findings
- `all_memory(k)` — retrieves recent memory entries
- Auto-persists to `backend/data/chroma_store/` on disk

Every task execution automatically saves findings to memory via the `/execute_task` endpoint. Memory is also queryable from the frontend through the memory search panel.

---

### 6. LLM Factory — `backend/utils/llm_factory.py`

Centralised LLM initialization using the Groq API.

- **Model:** `llama-3.1-8b-instant` (configurable via `DEFAULT_MODEL` env variable)
- **Temperature:** 0.3 (focused, low-creativity responses suitable for research)
- **Max Tokens:** 2000
- Loads API key from `.env` via `python-dotenv`

---

### 7. Prompts — `backend/utils/prompts.py`

All system prompts are centralized here for easy maintenance and tuning:

| Prompt | Purpose |
|---|---|
| `PLANNER_PROMPT` | Instructs LLM to return a valid JSON subtask plan |
| `RESEARCH_SYNTHESIS_PROMPT` | Generates structured findings from retrieved context |
| `MEMORY_TAGGING_PROMPT` | Extracts 3–6 semantic tags as a JSON list |
| `FINAL_REPORT_PROMPT` | Builds the 6-section final research report |

---

## API Reference

Base URL: `http://localhost:8000`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Backend health check |
| `POST` | `/plan` | Generate subtask plan from a research goal |
| `POST` | `/execute_task` | Execute a single subtask (retrieve + synthesize + tag + store) |
| `POST` | `/synthesize` | Generate final report from all completed task findings |
| `POST` | `/memory/add` | Manually add content to vector memory |
| `POST` | `/memory/search` | Semantic search over stored memory |

### Example — `/plan`
```json
Request:
{ "goal": "What are the latest advancements in transformer architectures?" }

Response:
[
  {
    "id": "task-1",
    "title": "Origins of Transformer Architecture",
    "description": "Research the original attention mechanism paper and its impact",
    "search_query": "transformer attention mechanism Vaswani 2017"
  },
  ...
]
```

### Example — `/execute_task`
```json
Request:
{
  "task": {
    "id": "task-1",
    "title": "Origins of Transformer Architecture",
    "description": "...",
    "search_query": "transformer attention mechanism"
  }
}

Response:
{
  "findings": "Introduction\n...\nKey Insights\n...",
  "sources": [{ "url": "...", "title": "...", "snippet": "..." }],
  "tags": ["attention mechanism", "self-attention", "encoder decoder"]
}
```

---

## Frontend

Built with vanilla HTML, CSS, and JavaScript. No frameworks — clean and lightweight.

**Features:**
- Backend health status indicator (online/unreachable) on load
- Research goal input with plan generation
- Task list panel with real-time status (PENDING → IN_PROGRESS → COMPLETED)
- Active task detail view showing title, description, findings, and cited sources
- Single task execution or full Auto Run mode (executes all tasks sequentially)
- Final report card displayed automatically when all tasks complete
- Memory search panel — query past findings by semantic similarity
- PDF export of the final report via browser print

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | LLaMA 3.1 8B Instant via Groq API |
| Agent Framework | LangChain Core (ChatPromptTemplate, LLM, Chain) |
| Vector Database | ChromaDB (local persistent store) |
| Embeddings | HuggingFace `sentence-transformers/all-MiniLM-L6-v2` |
| Web Retrieval | Tavily Search API |
| Scientific Retrieval | ArXiv Public API + feedparser |
| Backend Framework | FastAPI + Uvicorn |
| Data Validation | Pydantic v2 |
| Frontend | HTML5 / CSS3 / Vanilla JavaScript |
| Environment Config | python-dotenv |

---

## Setup & Installation

### Prerequisites
- Python 3.9+
- A [Groq API key](https://console.groq.com/) (free)
- A [Tavily API key](https://tavily.com/) (free tier available)

### Step 1 — Clone the Repository

```bash
git clone https://github.com/Fauzdarnikhil/Goal-Oriented-Research-Agent.git
cd Goal-Oriented-Research-Agent
```

### Step 2 — Create Virtual Environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure Environment Variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
DEFAULT_MODEL=llama-3.1-8b-instant
```

---

## Running the Application

### Start the Backend Server

```bash
uvicorn backend.main:app --reload
```

The API will be live at `http://localhost:8000`

API documentation (auto-generated by FastAPI) available at `http://localhost:8000/docs`

### Open the Frontend

Open `Frontend/index.html` directly in your browser, or serve it with a simple HTTP server:

```bash
# Python built-in server
cd Frontend
python -m http.server 5500
```

Then visit `http://localhost:5500` in your browser.

---

## Roadmap

The current version covers the core research pipeline. Planned improvements:

- **Feedback Loops** — LLM self-evaluates its own findings and flags low-confidence sections for re-retrieval
- **LangGraph Orchestration** — Replace linear execution with graph-based workflow control for conditional branching
- **Persistent Multi-User Memory** — User-level memory isolation instead of a shared global store
- **Iterative Refinement** — Agent re-runs subtasks if findings are below a quality threshold
- **Self-Correction** — Detects contradictions between subtask findings and resolves them before final report
- **Hybrid Retrieval Optimization** — MMR (Maximal Marginal Relevance) ranking to reduce redundant retrieved content

---

## Author

**Nikhil Singh**
B.Tech Computer Science (Hons) — GLA University, Mathura (2023–2027)

- GitHub: [@Fauzdarnikhil](https://github.com/Fauzdarnikhil)
- Email: nikhilsingh1477@gmail.com

---

> Developed as a semester project exploring modular AI agent design, autonomous research pipelines, and production-style backend architecture.
