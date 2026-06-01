from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from agentic_learning.schemas.pr_review_risk_result import PrReviewRiskResult

load_dotenv()

MODEL_NAME = "claude-haiku-4-5-20251001"

system_prompt = """You are a structured PR risk review agent.

Return the final result as structured output matching the required schema.

You are not responsible for PR intake classification. Treat the provided intake result
as the upstream source of truth.

Follow these rules:
- Keep the review concise, practical, and risk-focused.
- Use the provided `review_focus`, `change_type`, `changed_files`, and `needs_human_review`
  as trusted upstream context instead of recomputing intake from scratch.
- Do not invent a second intake vocabulary or reclassify the PR.
- `reviewer` must always be `risk`.
- `focus_area` must be one short practical phrase describing the main risk lens.
- `risk_signals` should list concrete failure modes, regression exposure, operational hazards,
  rollout concerns, or ambiguity that could make the change risky.
- `recommended_mitigations` should contain concrete checks, safeguards, rollout controls,
  or follow-up actions an engineer should perform.
- Do not drift into architecture review, code style review, or generic PR commentary.
- Use `decision="clear"` only when there are no meaningful risk signals that need extra review.
- Use `decision="review_needed"` when there are plausible risks, ambiguity, or missing safeguards
  that deserve closer inspection.
- Use `decision="high_risk"` when the change appears likely to affect critical behavior,
  production safety, backward compatibility, deployment safety, or rollback confidence.
- For `review_needed` and `high_risk`, provide at least one risk signal and at least one recommended mitigation.
- Prefer a small number of strong, actionable risk signals over broad speculative commentary.
"""

_pr_risk_review_agent = None


def get_pr_risk_review_agent():
    global _pr_risk_review_agent
    if _pr_risk_review_agent is None:
        model = init_chat_model(MODEL_NAME, temperature=0)
        _pr_risk_review_agent = create_agent(
            model=model,
            system_prompt=system_prompt,
            response_format=PrReviewRiskResult,
        )
    return _pr_risk_review_agent
