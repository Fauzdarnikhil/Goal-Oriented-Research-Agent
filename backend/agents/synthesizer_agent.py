from typing import List, Dict
from ..utils.llm_factory import get_llm
from ..utils.prompts import FINAL_REPORT_PROMPT
from langchain_core.prompts import ChatPromptTemplate


def synthesize_report(goal: str, tasks_with_findings: List[Dict]) -> str:
    """
    Build a final report from the original goal and the list of tasks + findings.

    tasks_with_findings example:
    [
      {
        "id": "task-1",
        "title": "...",
        "description": "...",
        "findings": "..."
      },
      ...
    ]
    """

    llm = get_llm()

    tasks_text_lines = []
    for t in tasks_with_findings:
        tasks_text_lines.append(
            f"Task: {t.get('title','')}\nDescription: {t.get('description','')}\nFindings:\n{t.get('findings','')}\n"
        )
    tasks_block = "\n\n---\n\n".join(tasks_text_lines)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", FINAL_REPORT_PROMPT),
            ("human", f"Original research goal:\n{goal}\n\nSubtasks and findings:\n{tasks_block}")
        ]
    )

    response = llm.invoke(prompt.format_messages())
    return response.content.strip()
