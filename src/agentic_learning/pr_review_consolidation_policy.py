from agentic_learning.schemas.pr_review_architecture_result import (
    PrReviewArchitectureResult,
)
from agentic_learning.schemas.pr_review_consolidation_result import (
    PrConsolidationResult,
    ReviewDecision,
)
from agentic_learning.schemas.pr_review_risk_result import PrReviewRiskResult
from agentic_learning.schemas.pr_review_testing_result import PrReviewTestingResult

UpstreamReviewResult = (
    PrReviewArchitectureResult | PrReviewTestingResult | PrReviewRiskResult
)


def compute_expected_consolidation_decision(
    *review_results: UpstreamReviewResult,
) -> ReviewDecision:
    decisions = {result.decision for result in review_results}

    if "high_risk" in decisions:
        return "high_risk"
    if "review_needed" in decisions:
        return "review_needed"
    return "clear"


def validate_consolidation_policy(
    consolidation_result: PrConsolidationResult,
    *review_results: UpstreamReviewResult,
) -> None:
    expected_decision = compute_expected_consolidation_decision(*review_results)

    if consolidation_result.decision != expected_decision:
        raise ValueError(
            "Consolidation decision does not match the deterministic upstream policy. "
            f"Expected {expected_decision!r}, got {consolidation_result.decision!r}."
        )
