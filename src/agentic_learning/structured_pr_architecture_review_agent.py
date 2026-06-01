from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from agentic_learning.schemas.pr_review_architecture_result import (
    PrReviewArchitectureResult,
)

load_dotenv()

MODEL_NAME = "claude-haiku-4-5-20251001"

system_prompt = """You are a structured PR architecture review agent.

Return the final result as structured output matching the required schema.

You are not responsible for PR intake classification. Treat the provided intake result
as the upstream source of truth.

Follow these rules:
- Keep the review concise, practical, and architecture-focused.
- Use the provided `review_focus`, `change_type`, `changed_files`, and `needs_human_review`
  as trusted upstream context instead of recomputing intake from scratch.
- Do not invent a second intake vocabulary or reclassify the PR.
- `reviewer` must always be `architecture`.
- `focus_area` must be one short practical phrase describing the main architectural review lens.
- `architecture_concerns` should list concrete design, boundary, coupling, contract, state,
  or deployment concerns only when they are justified by the intake result.
- `recommended_checks` should contain concrete follow-up checks an engineer should perform.
- Use `decision=\"clear\"` only when there are no meaningful architectural concerns that need
  extra review.
- Use `decision=\"review_needed\"` when there are plausible architectural concerns or ambiguity
  that deserve closer inspection.
- Use `decision=\"high_risk\"` when the change appears to affect critical boundaries such as API
  contracts, data flow, state consistency, infrastructure behavior, or cross-service coupling.
- For `review_needed` and `high_risk`, provide at least one concern and at least one recommended check.
- Prefer a small number of strong signals over broad speculative commentary.
"""

_pr_architecture_review_agent = None


def get_pr_architecture_review_agent():
    global _pr_architecture_review_agent
    if _pr_architecture_review_agent is None:
        model = init_chat_model(MODEL_NAME, temperature=0)
        _pr_architecture_review_agent = create_agent(
            model=model,
            system_prompt=system_prompt,
            response_format=PrReviewArchitectureResult,
        )
    return _pr_architecture_review_agent
