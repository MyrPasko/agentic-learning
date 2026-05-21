from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from agentic_learning.schemas.task_decomposer_result import (
    TaskDecomposerDraft,
)

load_dotenv()


MODEL_NAME = "claude-haiku-4-5-20251001"

system_prompt = """You are an expert at decomposing short engineering tasks into a compact implementation plan.

Return the final result as structured output matching the required schema.

Follow these rules:
- Keep the decomposition concise and practical.
- Return only the most relevant items.
- Do not invent code snippets, file paths, or implementation details that are not justified by the task.
- `implementation_tasks` must be a list of objects with: `title`, `description`, and `done_criteria`.
- `test_ideas` must be a list of objects with: `test_type`, `scenario`, and `expected_behavior`.
- `unknowns` must be a list of objects with: `question` and `why_it_matters`.
- Use only these impact values: `high`, `medium`, `low`.
- Use only these test types: `unit`, `component`, `integration`, `e2e`.
- Keep `unknowns` as an empty list when the task is sufficiently clear.
- Do not include `risks`; risk analysis happens in a separate workflow step after this draft is created.
- Prefer a small number of strong items over many weak or repetitive ones."""

_task_decomposer_draft_agent = None


def get_task_decomposer_draft_agent():
    global _task_decomposer_draft_agent

    if _task_decomposer_draft_agent is None:
        model = init_chat_model(
            MODEL_NAME,
            temperature=0,
        )
        _task_decomposer_draft_agent = create_agent(
            model,
            system_prompt=system_prompt,
            response_format=TaskDecomposerDraft,
        )

    return _task_decomposer_draft_agent
