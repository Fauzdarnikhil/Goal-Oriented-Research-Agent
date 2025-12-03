# backend/main.py

from typing import List, Dict, Any, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .agents.planner_agent import generate_plan
from .agents.executor_agent import execute_task
from .agents.synthesizer_agent import synthesize_report
from .memory.vector_db import global_memory


app = FastAPI(title="Autonomous Research Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Pydantic models ----------

class PlanRequest(BaseModel):
    goal: str


class Task(BaseModel):
    id: str
    title: str
    description: str
    search_query: str = ""


class ExecuteTaskRequest(BaseModel):
    task: Task


class ExecuteTaskResponse(BaseModel):
    findings: str
    sources: List[Dict[str, Any]]
    tags: List[str]


class SynthesizeRequest(BaseModel):
    goal: str
    tasks_with_findings: List[Dict[str, Any]]


class MemoryAddRequest(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None


class MemorySearchRequest(BaseModel):
    query: str
    k: int = 5


# ---------- Endpoints ----------

@app.post("/plan")
def plan(request: PlanRequest) -> List[Task]:
    tasks_raw = generate_plan(request.goal)
    return [Task(**t) for t in tasks_raw]


@app.post("/execute_task", response_model=ExecuteTaskResponse)
def execute_task_endpoint(req: ExecuteTaskRequest):
    result = execute_task(req.task.dict())

    # Save to memory
    global_memory.add_memory(
        content=result["findings"],
        metadata={
            "task_id": req.task.id,
            "task_title": req.task.title,
            "tags": result.get("tags", []),
        },
    )

    return ExecuteTaskResponse(
        findings=result["findings"],
        sources=result["sources"],
        tags=result.get("tags", []),
    )


@app.post("/synthesize")
def synthesize(req: SynthesizeRequest) -> Dict[str, str]:
    report = synthesize_report(req.goal, req.tasks_with_findings)
    return {"report": report}


@app.post("/memory/add")
def add_memory(req: MemoryAddRequest) -> Dict[str, str]:
    global_memory.add_memory(req.content, req.metadata)
    return {"status": "ok"}


@app.post("/memory/search")
def search_memory(req: MemorySearchRequest) -> Dict[str, Any]:
    results = global_memory.search_memory(req.query, k=req.k)
    return {"results": results}


@app.get("/health")
def health():
    return {"status": "ok"}
