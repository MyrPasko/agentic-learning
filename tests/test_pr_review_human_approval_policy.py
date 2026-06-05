import unittest

from agentic_learning.pr_review_human_approval_policy import (
    build_human_review_summary,
    need_human_approval,
)
from agentic_learning.schemas.pr_review_consolidation_result import (
    PrConsolidationResult,
)
from agentic_learning.schemas.pr_review_intake_result import PrReviewIntakeResult


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


class PrReviewHumanApprovalPolicyTests(unittest.TestCase):
    def test_need_human_approval_requires_review_for_high_risk(self) -> None:
        approval_status, review_reason = need_human_approval(
            build_intake_result(needs_human_review=False),
            build_consolidation_result("high_risk"),
        )

        self.assertEqual(approval_status, "review_required")
        self.assertEqual(review_reason, "Consolidation marked the PR as high_risk.")

    def test_need_human_approval_requires_review_for_review_needed(self) -> None:
        approval_status, review_reason = need_human_approval(
            build_intake_result(needs_human_review=False),
            build_consolidation_result("review_needed"),
        )

        self.assertEqual(approval_status, "review_required")
        self.assertEqual(
            review_reason,
            "Consolidation marked the PR as review_needed.",
        )

    def test_need_human_approval_requires_review_for_intake_flag(self) -> None:
        approval_status, review_reason = need_human_approval(
            build_intake_result(needs_human_review=True),
            build_consolidation_result("clear"),
        )

        self.assertEqual(approval_status, "review_required")
        self.assertEqual(
            review_reason,
            "The intake contract marked the PR as requiring human review.",
        )

    def test_need_human_approval_approves_clear_non_human_review_case(self) -> None:
        approval_status, review_reason = need_human_approval(
            build_intake_result(needs_human_review=False),
            build_consolidation_result("clear"),
        )

        self.assertEqual(approval_status, "approved")
        self.assertIsNone(review_reason)

    def test_build_human_review_summary_includes_reason_and_action(self) -> None:
        summary = build_human_review_summary(
            build_intake_result(needs_human_review=True),
            build_consolidation_result("review_needed"),
            "The intake contract marked the PR as requiring human review.",
        )

        self.assertIn("Human review required", summary)
        self.assertIn("requiring human review", summary)
        self.assertIn("Recommended next action", summary)
