from typing import Literal

from agentic_learning.schemas.pr_review_consolidation_result import (
    PrConsolidationResult,
)
from agentic_learning.schemas.pr_review_intake_result import PrReviewIntakeResult

ApprovalStatus = Literal["approved", "review_required"]
ReviewReason = str | None


def need_human_approval(
    intake_result: PrReviewIntakeResult,
    consolidation_result: PrConsolidationResult,
) -> tuple[ApprovalStatus, ReviewReason]:
    if consolidation_result.decision == "high_risk":
        return "review_required", "Consolidation marked the PR as high_risk."

    if consolidation_result.decision == "review_needed":
        return "review_required", "Consolidation marked the PR as review_needed."

    if intake_result.needs_human_review:
        return (
            "review_required",
            "The intake contract marked the PR as requiring human review.",
        )

    return "approved", None


def build_human_review_summary(
    intake_result: PrReviewIntakeResult,
    consolidation_result: PrConsolidationResult,
    review_reason: str,
) -> str:
    return (
        f"Human review required for '{intake_result.pr_title}'. "
        f"Reason: {review_reason} "
        f"Recommended next action: {consolidation_result.recommended_next_action}"
    )
