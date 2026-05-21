import json
import unittest
from unittest.mock import Mock, patch

from agentic_learning.schemas.task_decomposer_result import (
    ImplementationTask,
    RiskItem,
    TaskDecomposerDraft,
    TaskDecomposerResult,
    TestIdea,
    UnknownItem,
)
from agentic_learning.task_decomposer_workflow.helpers.build_task_decomposer_graph_state import (
    build_task_decomposer_graph_state,
)
from agentic_learning.task_decomposer_workflow.nodes import (
    build_fallback,
    review_output,
    run_approval_decision,
    run_decomposer_draft,
    run_risk_analysis,
)
from agentic_learning.task_decomposer_workflow.policy import (
    build_review_summary,
    need_for_approval,
)
from agentic_learning.task_decomposer_workflow.routes import (
    route_after_approval_decision,
    route_after_draft,
    route_after_risk_analysis,
)


def build_implementation_task() -> ImplementationTask:
    return ImplementationTask(
        title="Define endpoint contract",
        description="Define the endpoint contract before implementation starts.",
        done_criteria=[
            "Document the request and response shape clearly.",
        ],
    )


def build_test_idea() -> TestIdea:
    return TestIdea(
        test_type="integration",
        scenario="Send a valid request to the portfolio endpoint.",
        expected_behavior="The endpoint returns the expected success payload.",
    )


def build_unknown_item() -> UnknownItem:
    return UnknownItem(
        question="What authorization rule applies here?",
        why_it_matters="Authorization changes the workflow and test coverage.",
    )


def build_risk_item(impact: str = "medium") -> RiskItem:
    return RiskItem(
        risk="Insufficient validation",
        impact=impact,
        mitigation="Validate inputs before business logic executes fully.",
    )


def build_draft() -> TaskDecomposerDraft:
    return TaskDecomposerDraft(
        original_task="Add a new portfolio endpoint with validation and tests.",
        plan_summary="Implement a narrow endpoint slice with validation and tests.",
        implementation_tasks=[build_implementation_task()],
        test_ideas=[build_test_idea()],
        unknowns=[],
    )


def build_result(
    *,
    unknowns: list[UnknownItem] | None = None,
    risks: list[RiskItem] | None = None,
) -> TaskDecomposerResult:
    return TaskDecomposerResult(
        original_task="Add a new portfolio endpoint with validation and tests.",
        plan_summary="Implement a narrow endpoint slice with validation and tests.",
        implementation_tasks=[build_implementation_task()],
        risks=risks if risks is not None else [build_risk_item("medium")],
        test_ideas=[build_test_idea()],
        unknowns=unknowns if unknowns is not None else [],
    )


class TaskDecomposerWorkflowTests(unittest.TestCase):
    def test_build_task_decomposer_graph_state_sets_default_step_outcomes(self) -> None:
        state = build_task_decomposer_graph_state(prompt="test prompt")

        self.assertEqual(state["prompt"], "test prompt")
        self.assertEqual(
            state["step_outcomes"],
            {
                "draft": "skipped",
                "risk_analysis": "skipped",
                "approval_decision": "skipped",
                "review": "skipped",
            },
        )

    def test_route_after_draft_covers_success_retry_and_fallback(self) -> None:
        self.assertEqual(route_after_draft({"failure_reason": None}), "run_risk_analysis")
        self.assertEqual(
            route_after_draft({"failure_reason": "boom", "retry_count": 1}), "retry"
        )
        self.assertEqual(
            route_after_draft({"failure_reason": "boom", "retry_count": 2}),
            "fallback",
        )

    def test_route_after_risk_analysis_covers_success_retry_and_fallback(self) -> None:
        self.assertEqual(
            route_after_risk_analysis({"failure_reason": None}),
            "approval_decision",
        )
        self.assertEqual(
            route_after_risk_analysis({"failure_reason": "boom", "retry_count": 1}),
            "retry",
        )
        self.assertEqual(
            route_after_risk_analysis({"failure_reason": "boom", "retry_count": 2}),
            "fallback",
        )

    def test_route_after_approval_decision_covers_done_review_retry_and_fallback(
        self,
    ) -> None:
        self.assertEqual(
            route_after_approval_decision(
                {"approval_status": "approved", "failure_reason": None}
            ),
            "done",
        )
        self.assertEqual(
            route_after_approval_decision({"approval_status": "review_required"}),
            "review",
        )
        self.assertEqual(
            route_after_approval_decision(
                {"approval_status": None, "failure_reason": "boom", "retry_count": 1}
            ),
            "retry",
        )
        self.assertEqual(
            route_after_approval_decision(
                {"approval_status": None, "failure_reason": "boom", "retry_count": 2}
            ),
            "fallback",
        )

    def test_need_for_approval_requires_review_for_unknowns(self) -> None:
        approval_status, review_reason = need_for_approval(
            build_result(unknowns=[build_unknown_item()])
        )

        self.assertEqual(approval_status, "review_required")
        self.assertEqual(review_reason, "Unknown items detected.")

    def test_need_for_approval_requires_review_for_high_risk(self) -> None:
        approval_status, review_reason = need_for_approval(
            build_result(risks=[build_risk_item("high")])
        )

        self.assertEqual(approval_status, "review_required")
        self.assertEqual(review_reason, "At least one risk item is high.")

    def test_need_for_approval_approves_low_risk_without_unknowns(self) -> None:
        approval_status, review_reason = need_for_approval(build_result())

        self.assertEqual(approval_status, "approved")
        self.assertIsNone(review_reason)

    def test_build_review_summary_counts_unknowns_and_risks(self) -> None:
        summary = build_review_summary(
            build_result(
                unknowns=[build_unknown_item()],
                risks=[build_risk_item("high"), build_risk_item("medium")],
            )
        )

        self.assertEqual(summary, "Unknown items: 1, Risks: 2")

    def test_run_decomposer_draft_uses_lazy_agent_and_sets_step_outcomes(self) -> None:
        agent = Mock()
        agent.invoke.return_value = {"structured_response": build_draft()}

        with patch(
            "agentic_learning.task_decomposer_workflow.nodes.get_task_decomposer_draft_agent",
            return_value=agent,
        ):
            result = run_decomposer_draft({"prompt": "Build the endpoint."})

        self.assertIsNone(result["failure_reason"])
        self.assertEqual(result["step_outcomes"]["draft"], "ok")
        self.assertEqual(result["step_outcomes"]["risk_analysis"], "skipped")
        agent.invoke.assert_called_once()

    def test_run_risk_analysis_without_draft_marks_failure(self) -> None:
        result = run_risk_analysis({"prompt": "Build the endpoint.", "retry_count": 0})

        self.assertEqual(result["failure_reason"], "Draft response is missing.")
        self.assertEqual(result["retry_count"], 1)
        self.assertEqual(result["step_outcomes"]["risk_analysis"], "failed")

    def test_run_risk_analysis_success_sets_ok_step_outcome(self) -> None:
        draft = build_draft()
        raw_risks = json.dumps(
            [
                {
                    "risk": "Insufficient validation",
                    "impact": "high",
                    "mitigation": (
                        "Validate identifiers and malformed payloads before business"
                        " logic executes."
                    ),
                }
            ]
        )

        tool = Mock()
        tool.invoke.return_value = raw_risks

        with patch(
            "agentic_learning.task_decomposer_workflow.nodes.analyze_task_risks",
            tool,
        ):
            result = run_risk_analysis(
                {
                    "prompt": "Build the endpoint.",
                    "draft_response": draft,
                    "step_outcomes": {
                        "draft": "ok",
                        "risk_analysis": "skipped",
                        "approval_decision": "skipped",
                        "review": "skipped",
                    },
                }
            )

        self.assertIsNone(result["failure_reason"])
        self.assertEqual(result["tool_name"], "analyze_task_risks")
        self.assertEqual(result["step_outcomes"]["risk_analysis"], "ok")
        self.assertEqual(result["step_outcomes"]["approval_decision"], "skipped")

    def test_run_approval_decision_records_review_required(self) -> None:
        result = run_approval_decision(
            {
                "prompt": "Build the endpoint.",
                "draft_response": build_draft(),
                "structured_response": build_result(unknowns=[build_unknown_item()]),
                "step_outcomes": {
                    "draft": "ok",
                    "risk_analysis": "ok",
                    "approval_decision": "skipped",
                    "review": "skipped",
                },
            }
        )

        self.assertEqual(result["approval_status"], "review_required")
        self.assertEqual(result["review_reason"], "Unknown items detected.")
        self.assertEqual(result["step_outcomes"]["approval_decision"], "ok")
        self.assertEqual(result["step_outcomes"]["review"], "skipped")

    def test_build_fallback_marks_used_fallback_and_preserves_step_outcomes(self) -> None:
        result = build_fallback(
            {
                "prompt": "Build the endpoint.",
                "tool_name": "analyze_task_risks",
                "failure_reason": "boom",
                "retry_count": 2,
                "step_outcomes": {
                    "draft": "ok",
                    "risk_analysis": "failed",
                    "approval_decision": "skipped",
                    "review": "skipped",
                },
            }
        )

        self.assertTrue(result["used_fallback"])
        self.assertEqual(result["tool_name"], "analyze_task_risks")
        self.assertEqual(result["step_outcomes"]["risk_analysis"], "failed")

    def test_review_output_sets_summary_and_review_step(self) -> None:
        result = review_output(
            {
                "structured_response": build_result(unknowns=[build_unknown_item()]),
                "step_outcomes": {
                    "draft": "ok",
                    "risk_analysis": "ok",
                    "approval_decision": "ok",
                    "review": "skipped",
                },
            }
        )

        self.assertEqual(result["review_summary"], "Unknown items: 1, Risks: 1")
        self.assertEqual(result["step_outcomes"]["review"], "ok")


if __name__ == "__main__":
    unittest.main()
