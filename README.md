# 🧠 Goal-Oriented Autonomous Research Agent

> A modular AI research system that mimics a human research assistant by planning tasks, retrieving information from internal and external sources, and forming the foundation for structured autonomous research workflows.

---

## 📌 Overview

This project implements a goal-driven research agent capable of:

- Breaking complex research questions into actionable subtasks
- Retrieving knowledge from an internal vector database
- Expanding research using external web sources
- Structuring research workflows for future autonomous execution

Unlike traditional chat-based systems, this project focuses on **planning, retrieval, modular architecture, and extensibility toward autonomous reasoning systems.**

---

## 🏗 System Architecture

The application follows a clear frontend-backend separation.

### 🔄 High-Level Flow

```
User (Frontend)
        │
        ▼
Backend API
        │
        ▼
Planner (LLM)
        │
        ▼
Subtasks
        │
        ├──────────► Internal Retriever (Vector Store)
        │
        └──────────► External Web Retriever
                           │
                           ▼
                     Retrieved Context
                           │
                           ▼
                 (Future: Executor & Evaluator)
```

---

## 📂 Project Structure

```
project-root/
│
├── frontend/
│   ├── index.html        # Main UI layout
│   ├── style.css         # Styling
│   └── script.js         # Frontend logic & API calls
│
├── backend/
│   ├── llm_factory/      # LLM initialization and configuration
│   ├── planner/          # Task decomposition logic
│   ├── retriever/        # Internal & external retrieval modules
│   ├── vector_store/     # Chroma integration
│   ├── memory/           # (Planned) memory handling
│   └── main.py           # Backend entry point / API server
│
├── .env                  # Environment variables (not committed)
├── requirements.txt
└── README.md
```

---

## 🧩 Core Backend Modules

### 1️⃣ LLM Factory
Centralized configuration of language models.
- Model selection
- Temperature control
- API key management

### 2️⃣ Planner
- Converts research goals into structured subtasks
- Determines task granularity dynamically
- Forms the backbone of the research workflow

### 3️⃣ Retriever
- Internal Retrieval: Chroma vector store
- External Retrieval: Web-based search integration
- Supports MMR and similarity-based search

### 4️⃣ Vector Store
- Embeds documents
- Stores and indexes content
- Enables semantic search over research materials

---

## 🖥 Frontend

- Built with HTML, CSS, and JavaScript
- Sends research queries to backend API
- Displays generated subtasks
- Designed for future integration of research outputs and progress tracking

---

## ⚙️ Tech Stack

- Python 3.9+
- LangChain
- Chroma (Vector Database)
- OpenAI / LLM APIs
- HTML / CSS / JavaScript
- dotenv

---

## 🚀 Current Capabilities

- Subtask generation using LLM
- Document ingestion and embedding
- Vector-based retrieval (Chroma)
- Web retrieval integration
- Clean frontend-backend separation

---

## 🔮 Roadmap

Planned upgrades include:

- Autonomous subtask execution
- Feedback & evaluation loop
- Persistent memory layer
- Multi-step research iteration
- LangGraph-based workflow orchestration
- Hybrid retrieval optimization

---

## 🛠 Setup & Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Create a `.env` file in the root directory:

```
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=your_api_base_here
```

### 5️⃣ Run Backend Server

```bash
python backend/main.py
```

### 6️⃣ Open Frontend

Open `frontend/index.html` in your browser  
or serve it using a simple HTTP server.

---

## 🎯 Vision

The long-term objective is to evolve this system into a fully autonomous research agent capable of:

- Planning research tasks
- Retrieving evidence
- Evaluating findings
- Storing structured knowledge
- Iteratively improving outputs

This project represents a foundational step toward structured, deterministic AI research automation.

---

## 📄 License

MIT License

---

## 👨‍💻 Author

Developed as a semester project exploring autonomous AI research systems.
