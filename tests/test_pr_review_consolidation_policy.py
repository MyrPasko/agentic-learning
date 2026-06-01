import unittest

from agentic_learning.pr_review_consolidation_policy import (
    compute_expected_consolidation_decision,
    validate_consolidation_policy,
)
from agentic_learning.schemas.pr_review_architecture_result import (
    PrReviewArchitectureResult,
)
from agentic_learning.schemas.pr_review_consolidation_result import (
    PrConsolidationResult,
)
from agentic_learning.schemas.pr_review_risk_result import PrReviewRiskResult
from agentic_learning.schemas.pr_review_testing_result import PrReviewTestingResult


def build_architecture_result(
    decision: str = "clear",
) -> PrReviewArchitectureResult:
    payload = {
        "reviewer": "architecture",
        "focus_area": "Service boundary clarity",
        "architecture_concerns": [],
        "recommended_checks": [],
        "decision": decision,
    }
    if decision != "clear":
        payload["architecture_concerns"] = [
            "The API contract boundary needs explicit follow-up review."
        ]
        payload["recommended_checks"] = [
            "Inspect the boundary and error-handling behavior before merge."
        ]
    return PrReviewArchitectureResult.model_validate(payload)


def build_testing_result(
    decision: str = "clear",
) -> PrReviewTestingResult:
    payload = {
        "reviewer": "testing",
        "focus_area": "Regression coverage depth",
        "test_gaps": [],
        "recommended_test_cases": [],
        "decision": decision,
    }
    if decision != "clear":
        payload["test_gaps"] = [
            "Regression coverage for invalid inputs and error paths is incomplete."
        ]
        payload["recommended_test_cases"] = [
            "Add regression tests for invalid input handling and error responses."
        ]
    return PrReviewTestingResult.model_validate(payload)


def build_risk_result(
    decision: str = "clear",
) -> PrReviewRiskResult:
    payload = {
        "reviewer": "risk",
        "focus_area": "Release safety and rollback confidence",
        "risk_signals": [],
        "recommended_mitigations": [],
        "decision": decision,
    }
    if decision != "clear":
        payload["risk_signals"] = [
            "The change has unresolved release-safety signals that need follow-up."
        ]
        payload["recommended_mitigations"] = [
            "Verify rollback safety and confirm release checks before merge."
        ]
    return PrReviewRiskResult.model_validate(payload)


class PrReviewConsolidationPolicyTests(unittest.TestCase):
    def test_compute_expected_consolidation_decision_returns_clear_for_all_clear(self) -> None:
        decision = compute_expected_consolidation_decision(
            build_architecture_result("clear"),
            build_testing_result("clear"),
            build_risk_result("clear"),
        )

        self.assertEqual(decision, "clear")

    def test_compute_expected_consolidation_decision_returns_review_needed(self) -> None:
        decision = compute_expected_consolidation_decision(
            build_architecture_result("clear"),
            build_testing_result("review_needed"),
            build_risk_result("clear"),
        )

        self.assertEqual(decision, "review_needed")

    def test_compute_expected_consolidation_decision_returns_high_risk(self) -> None:
        decision = compute_expected_consolidation_decision(
            build_architecture_result("clear"),
            build_testing_result("review_needed"),
            build_risk_result("high_risk"),
        )

        self.assertEqual(decision, "high_risk")

    def test_validate_consolidation_policy_rejects_mismatched_decision(self) -> None:
        consolidation_result = PrConsolidationResult.model_validate(
            {
                "summary": "Reviewer outputs indicate follow-up is still needed.",
                "priority_concerns": [],
                "recommended_next_action": "Address the reviewer follow-up items before merge.",
                "decision": "clear",
            }
        )

        with self.assertRaisesRegex(
            ValueError,
            "Consolidation decision does not match the deterministic upstream policy",
        ):
            validate_consolidation_policy(
                consolidation_result,
                build_architecture_result("clear"),
                build_testing_result("review_needed"),
                build_risk_result("clear"),
            )
