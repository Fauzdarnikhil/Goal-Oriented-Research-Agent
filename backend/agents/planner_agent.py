import json
from typing import List, Dict
from ..utils.llm_factory import get_llm
from ..utils.prompts import PLANNER_PROMPT
from langchain_core.prompts import ChatPromptTemplate


def generate_plan(goal: str) -> List[Dict]:
    """
    Uses the LLM to break a research goal into structured subtasks.
    Returns a list of task objects:
    [
        {
            "id": "task-1",
            "title": "...",
            "description": "...",
            "search_query": "..."
        },
        ...
    ]
    """

    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", PLANNER_PROMPT),
            ("human", "Research goal: " + goal),
        ]
    )

    response = llm.invoke(prompt.format_messages())
    raw = response.content.strip()

    # Safety: extract only the JSON section
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("LLM did not return JSON.")

    json_str = raw[start : end + 1]

    try:
        data = json.loads(json_str)
    except Exception as e:
        raise ValueError(f"Failed to parse JSON: {e}\nRaw response:\n{raw}")

    tasks = data.get("tasks", [])
    structured = []

    for idx, t in enumerate(tasks):
        structured.append(
            {
                "id": f"task-{idx+1}",
                "title": t.get("title", "").strip(),
                "description": t.get("description", "").strip(),
                "search_query": t.get("search_query", "").strip(),
            }
        )

    return structured
