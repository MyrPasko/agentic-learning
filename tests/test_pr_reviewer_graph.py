import unittest
from unittest.mock import patch

from agentic_learning.pr_reviewer_graph import pr_reviewer_graph
from agentic_learning.schemas.pr_review_architecture_result import (
    PrReviewArchitectureResult,
)
from agentic_learning.schemas.pr_review_consolidation_result import (
    PrConsolidationResult,
)
from agentic_learning.schemas.pr_review_intake_result import PrReviewIntakeResult
from agentic_learning.schemas.pr_review_risk_result import PrReviewRiskResult
from agentic_learning.schemas.pr_review_testing_result import PrReviewTestingResult


def build_intake_result(
    *,
    needs_human_review: bool = False,
) -> PrReviewIntakeResult:
    return PrReviewIntakeResult.model_validate(
        {
            "pr_title": "Add portfolio summary endpoint",
            "pr_summary": "Introduce a GET endpoint with validation and response-shape updates.",
            "changed_files": [
                "src/routes/portfolio.ts",
                "src/validators/portfolioValidator.ts",
            ],
            "change_type": "api",
            "review_focus": "API contract safety and validation behavior",
            "needs_human_review": needs_human_review,
        }
    )


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


def build_consolidation_result(
    decision: str = "clear",
) -> PrConsolidationResult:
    payload = {
        "summary": "Reviewer outputs are aligned for the current PR slice.",
        "priority_concerns": [],
        "recommended_next_action": "Ship after the deterministic checks stay green.",
        "decision": decision,
    }
    if decision != "clear":
        payload["priority_concerns"] = [
            "The reviewer chain still reports issues that need follow-up before merge."
        ]
        payload["recommended_next_action"] = (
            "Address the flagged review issues before requesting final approval."
        )
    return PrConsolidationResult.model_validate(payload)


class PrReviewerGraphTests(unittest.TestCase):
    @patch("agentic_learning.pr_reviewer_graph.run_structured_pr_consolidation_review_from_artifacts")
    @patch("agentic_learning.pr_reviewer_graph.run_structured_pr_risk_review_agent")
    @patch("agentic_learning.pr_reviewer_graph.run_structured_pr_testing_review_agent")
    @patch("agentic_learning.pr_reviewer_graph.run_structured_pr_architecture_review_agent")
    @patch("agentic_learning.pr_reviewer_graph.run_structured_pr_review_intake_agent")
    def test_pr_reviewer_graph_skips_review_summary_for_approved_path(
        self,
        intake_mock,
        architecture_mock,
        testing_mock,
        risk_mock,
        consolidation_mock,
    ) -> None:
        intake_mock.return_value = build_intake_result(needs_human_review=False)
        architecture_mock.return_value = build_architecture_result("clear")
        testing_mock.return_value = build_testing_result("clear")
        risk_mock.return_value = build_risk_result("clear")
        consolidation_mock.return_value = build_consolidation_result("clear")

        result = pr_reviewer_graph.invoke({})

        self.assertEqual(result["approval_status"], "approved")
        self.assertIsNone(result.get("review_summary"))
        self.assertEqual(result["step_outcomes"]["approval_decision"], "ok")
        self.assertEqual(result["step_outcomes"]["review"], "skipped")
        intake_mock.assert_called_once()
        architecture_mock.assert_called_once()
        testing_mock.assert_called_once()
        risk_mock.assert_called_once()
        consolidation_mock.assert_called_once()

    @patch("agentic_learning.pr_reviewer_graph.run_structured_pr_consolidation_review_from_artifacts")
    @patch("agentic_learning.pr_reviewer_graph.run_structured_pr_risk_review_agent")
    @patch("agentic_learning.pr_reviewer_graph.run_structured_pr_testing_review_agent")
    @patch("agentic_learning.pr_reviewer_graph.run_structured_pr_architecture_review_agent")
    @patch("agentic_learning.pr_reviewer_graph.run_structured_pr_review_intake_agent")
    def test_pr_reviewer_graph_builds_review_summary_when_human_review_is_required(
        self,
        intake_mock,
        architecture_mock,
        testing_mock,
        risk_mock,
        consolidation_mock,
    ) -> None:
        intake_mock.return_value = build_intake_result(needs_human_review=True)
        architecture_mock.return_value = build_architecture_result("clear")
        testing_mock.return_value = build_testing_result("clear")
        risk_mock.return_value = build_risk_result("clear")
        consolidation_mock.return_value = build_consolidation_result("clear")

        result = pr_reviewer_graph.invoke({})

        self.assertEqual(result["approval_status"], "review_required")
        self.assertEqual(
            result["review_reason"],
            "The intake contract marked the PR as requiring human review.",
        )
        self.assertIn("Human review required", result["review_summary"])
        self.assertEqual(result["step_outcomes"]["approval_decision"], "ok")
        self.assertEqual(result["step_outcomes"]["review"], "ok")
