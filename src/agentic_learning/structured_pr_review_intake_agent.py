from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from agentic_learning.schemas.pr_review_intake_result import (
    PrReviewIntakeResult,
)

load_dotenv()


MODEL_NAME = "claude-haiku-4-5-20251001"

system_prompt = """You are a structured PR review intake agent.

Return the final result as structured output matching the required schema.

Follow these rules:
- Keep the classification concise and practical.
- Extract the PR title and summarize the change clearly.
- Use only these `change_type` values: `api`, `frontend`, `data`, `infra`, `mixed`, `unclear`.
- `changed_files` must be a list of file paths taken from the input.
- `review_focus` must be one short practical phrase describing the first review priority.
- `needs_human_review` should be `true` when the PR changes API contracts, validation behavior, data handling, deployment behavior, or leaves important ambiguity.
- Prefer a small number of strong signals over broad speculative commentary.
"""

_pr_review_intake_agent = None


def get_pr_review_intake_agent():
    global _pr_review_intake_agent

    if _pr_review_intake_agent is None:
        model = init_chat_model(MODEL_NAME, temperature=0)
        _pr_review_intake_agent = create_agent(
            model=model,
            system_prompt=system_prompt,
            response_format=PrReviewIntakeResult,
        )

    return _pr_review_intake_agent
