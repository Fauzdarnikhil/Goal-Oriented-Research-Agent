from typing import Dict, Any
from ..utils.llm_factory import get_llm
from ..utils.prompts import RESEARCH_SYNTHESIS_PROMPT, MEMORY_TAGGING_PROMPT
from .retriever_agent import retrieve_sources
from langchain_core.prompts import ChatPromptTemplate
import json


def execute_task(task: Dict) -> Dict[str, Any]:
    """Executes one research step and generates findings + memory tags."""

    llm = get_llm()

    # --- Step 1: Retrieve real data from web ---
    retrieval = retrieve_sources(task.get("search_query", ""))
    docs = retrieval["documents"]
    sources = retrieval["sources"]

    context = "\n\n".join(docs)

    # --- Step 2: Synthesize findings ---
    prompt = ChatPromptTemplate.from_messages([
        ("system", RESEARCH_SYNTHESIS_PROMPT),
        ("human", f"Task: {task['title']}\n\nContext:\n{context}")
    ])
    response = llm.invoke(prompt.format_messages())
    findings = response.content.strip()

    # --- Step 3: Memory Tag generation ---
    tag_prompt = ChatPromptTemplate.from_messages([
        ("system", MEMORY_TAGGING_PROMPT),
        ("human", findings)
    ])
    tag_result = llm.invoke(tag_prompt.format_messages()).content.strip()

    # Extract tags even if wrapped in text
    try:
        start = tag_result.find("[")
        end = tag_result.rfind("]")
        tags = json.loads(tag_result[start:end + 1])
    except Exception:
        tags = []

    return {"findings": findings, "sources": sources, "tags": tags}
