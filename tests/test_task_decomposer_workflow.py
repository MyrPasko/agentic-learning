import json
import os
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
from agentic_learning.task_decomposer_graph import task_decomposer_graph
from agentic_learning.task_decomposer_workflow.helpers.build_task_decomposer_graph_state import (
    build_task_decomposer_graph_state,
)
from agentic_learning.task_decomposer_workflow.nodes import (
    build_fallback,
    review_output,
    run_approval_decision,
    run_decomposer_draft,
    run_risk_analysis,
    run_unknown_analysis,
)
from agentic_learning.task_decomposer_workflow.policy import (
    build_review_summary,
    need_for_approval,
)
from agentic_learning.task_decomposer_workflow.routes import (
    route_after_approval_decision,
    route_after_draft,
    route_after_risk_analysis,
    route_after_unknown_analysis,
)
from agentic_learning.tools.analyze_task_unknowns import _analyze_task_unknowns


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


def build_unknown_item(
    question: str = "What authorization rule applies to this task?",
) -> UnknownItem:
    why_it_matters = {
        "What authorization rule applies to this task?": (
            "Authorization changes the workflow and test coverage."
        ),
        "What validation rules and payload constraints are required?": (
            "Missing validation details can break the contract and runtime behavior."
        ),
        "What external dependency or persistence constraint exists here?": (
            "Dependencies can change implementation design and failure handling."
        ),
    }[question]
    return UnknownItem(question=question, why_it_matters=why_it_matters)


def build_risk_item(impact: str = "medium") -> RiskItem:
    return RiskItem(
        risk="Insufficient validation",
        impact=impact,
        mitigation="Validate inputs before business logic executes fully.",
    )


def build_draft(
    *, unknowns: list[UnknownItem] | None = None
) -> TaskDecomposerDraft:
    return TaskDecomposerDraft(
        original_task="Add a new portfolio endpoint with validation and tests.",
        plan_summary="Implement a narrow endpoint slice with validation and tests.",
        implementation_tasks=[build_implementation_task()],
        test_ideas=[build_test_idea()],
        unknowns=unknowns if unknowns is not None else [],
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


def build_step_outcomes() -> dict[str, str]:
    return {
        "draft": "skipped",
        "unknown_analysis": "skipped",
        "risk_analysis": "skipped",
        "approval_decision": "skipped",
        "review": "skipped",
    }


class TaskDecomposerWorkflowTests(unittest.TestCase):
    def test_build_task_decomposer_graph_state_sets_default_step_outcomes(self) -> None:
        state = build_task_decomposer_graph_state(prompt="test prompt")

        self.assertEqual(state["prompt"], "test prompt")
        self.assertEqual(state["unknowns"], [])
        self.assertEqual(
            state["step_outcomes"],
            {
                "draft": "skipped",
                "unknown_analysis": "skipped",
                "risk_analysis": "skipped",
                "approval_decision": "skipped",
                "review": "skipped",
            },
        )

    def test_route_after_draft_covers_success_retry_and_fallback(self) -> None:
        self.assertEqual(
            route_after_draft({"failure_reason": None}),
            "run_unknown_analysis",
        )
        self.assertEqual(
            route_after_draft({"failure_reason": "boom", "retry_count": 1}),
            "retry",
        )
        self.assertEqual(
            route_after_draft({"failure_reason": "boom", "retry_count": 2}),
            "fallback",
        )

    def test_route_after_unknown_analysis_covers_success_retry_and_fallback(
        self,
    ) -> None:
        self.assertEqual(
            route_after_unknown_analysis({"failure_reason": None}),
            "run_risk_analysis",
        )
        self.assertEqual(
            route_after_unknown_analysis({"failure_reason": "boom", "retry_count": 1}),
            "retry",
        )
        self.assertEqual(
            route_after_unknown_analysis({"failure_reason": "boom", "retry_count": 2}),
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
        self.assertEqual(result["unknowns"], [])
        self.assertEqual(result["step_outcomes"]["draft"], "ok")
        self.assertEqual(result["step_outcomes"]["unknown_analysis"], "skipped")
        self.assertEqual(result["step_outcomes"]["risk_analysis"], "skipped")
        agent.invoke.assert_called_once()

    def test_analyze_task_unknowns_returns_empty_list_without_signal_match(self) -> None:
        result = json.loads(_analyze_task_unknowns("Polish the README introduction text."))

        self.assertEqual(result, [])

    def test_analyze_task_unknowns_returns_auth_unknown_for_auth_signal(self) -> None:
        result = json.loads(
            _analyze_task_unknowns("Add auth checks for role-based access control.")
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["question"], "What authorization rule applies to this task?")

    def test_analyze_task_unknowns_returns_validation_unknown_for_validation_signal(
        self,
    ) -> None:
        result = json.loads(
            _analyze_task_unknowns("Define validation and payload schema for the API.")
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0]["question"],
            "What validation rules and payload constraints are required?",
        )

    def test_analyze_task_unknowns_limits_results_to_two_signal_groups(self) -> None:
        result = json.loads(
            _analyze_task_unknowns(
                "Add auth, validation, and database queue handling for the API."
            )
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(
            [item["question"] for item in result],
            [
                "What authorization rule applies to this task?",
                "What validation rules and payload constraints are required?",
            ],
        )

    def test_analyze_task_unknowns_supports_forced_failure(self) -> None:
        with patch.dict(os.environ, {"FORCE_UNKNOWN_TOOL_FAILURE": "1"}):
            with self.assertRaises(RuntimeError):
                _analyze_task_unknowns("Add auth checks to the endpoint.")

    def test_run_unknown_analysis_sets_authoritative_unknowns_and_correct_tool_name(
        self,
    ) -> None:
        tool = Mock()
        tool.invoke.return_value = json.dumps(
            [
                {
                    "question": "What authorization rule applies to this task?",
                    "why_it_matters": (
                        "Authorization changes the workflow and test coverage."
                    ),
                }
            ]
        )

        with patch(
            "agentic_learning.task_decomposer_workflow.nodes.analyze_task_unknowns",
            tool,
        ):
            result = run_unknown_analysis(
                {
                    "prompt": "Build the endpoint.",
                    "draft_response": build_draft(),
                    "step_outcomes": {
                        **build_step_outcomes(),
                        "draft": "ok",
                    },
                }
            )

        self.assertIsNone(result["failure_reason"])
        self.assertEqual(result["tool_name"], "analyze_task_unknowns")
        self.assertEqual(len(result["unknowns"]), 1)
        self.assertIsNone(result["structured_response"])
        self.assertEqual(result["step_outcomes"]["unknown_analysis"], "ok")
        self.assertEqual(result["step_outcomes"]["risk_analysis"], "skipped")

    def test_run_unknown_analysis_failure_marks_step_and_increments_retry(self) -> None:
        tool = Mock()
        tool.invoke.side_effect = RuntimeError("boom")

        with patch(
            "agentic_learning.task_decomposer_workflow.nodes.analyze_task_unknowns",
            tool,
        ):
            result = run_unknown_analysis(
                {
                    "prompt": "Build the endpoint.",
                    "draft_response": build_draft(),
                    "retry_count": 0,
                    "step_outcomes": {
                        **build_step_outcomes(),
                        "draft": "ok",
                    },
                }
            )

        self.assertEqual(result["failure_reason"], "boom")
        self.assertEqual(result["retry_count"], 1)
        self.assertEqual(result["tool_name"], "analyze_task_unknowns")
        self.assertEqual(result["step_outcomes"]["unknown_analysis"], "failed")

    def test_run_risk_analysis_without_draft_marks_failure(self) -> None:
        result = run_risk_analysis({"prompt": "Build the endpoint.", "retry_count": 0})

        self.assertEqual(result["failure_reason"], "Draft response is missing.")
        self.assertEqual(result["retry_count"], 1)
        self.assertEqual(result["step_outcomes"]["risk_analysis"], "failed")

    def test_run_risk_analysis_uses_authoritative_unknowns_from_state(self) -> None:
        draft = build_draft(unknowns=[build_unknown_item()])
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
        authoritative_unknowns = [
            build_unknown_item("What validation rules and payload constraints are required?")
        ]

        with patch(
            "agentic_learning.task_decomposer_workflow.nodes.analyze_task_risks",
            tool,
        ):
            result = run_risk_analysis(
                {
                    "prompt": "Build the endpoint.",
                    "draft_response": draft,
                    "unknowns": authoritative_unknowns,
                    "step_outcomes": {
                        **build_step_outcomes(),
                        "draft": "ok",
                        "unknown_analysis": "ok",
                    },
                }
            )

        self.assertIsNone(result["failure_reason"])
        self.assertEqual(result["tool_name"], "analyze_task_risks")
        self.assertEqual(result["unknowns"], authoritative_unknowns)
        self.assertEqual(result["structured_response"].unknowns, authoritative_unknowns)
        self.assertEqual(result["step_outcomes"]["risk_analysis"], "ok")
        self.assertEqual(result["step_outcomes"]["approval_decision"], "skipped")

    def test_run_approval_decision_records_review_required(self) -> None:
        result = run_approval_decision(
            {
                "prompt": "Build the endpoint.",
                "draft_response": build_draft(),
                "structured_response": build_result(unknowns=[build_unknown_item()]),
                "step_outcomes": {
                    **build_step_outcomes(),
                    "draft": "ok",
                    "unknown_analysis": "ok",
                    "risk_analysis": "ok",
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
                    **build_step_outcomes(),
                    "draft": "ok",
                    "unknown_analysis": "ok",
                    "risk_analysis": "failed",
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
                    **build_step_outcomes(),
                    "draft": "ok",
                    "unknown_analysis": "ok",
                    "risk_analysis": "ok",
                    "approval_decision": "ok",
                },
            }
        )

        self.assertEqual(result["review_summary"], "Unknown items: 1, Risks: 1")
        self.assertEqual(result["step_outcomes"]["review"], "ok")

    def test_compiled_graph_review_path_reaches_expected_final_state(self) -> None:
        agent = Mock()
        agent.invoke.return_value = {"structured_response": build_draft()}
        unknown_tool = Mock()
        unknown_tool.invoke.return_value = json.dumps(
            [
                {
                    "question": "What authorization rule applies to this task?",
                    "why_it_matters": (
                        "Authorization changes the workflow and test coverage."
                    ),
                }
            ]
        )
        risk_tool = Mock()
        risk_tool.invoke.return_value = json.dumps(
            [
                {
                    "risk": "Insufficient validation",
                    "impact": "medium",
                    "mitigation": (
                        "Validate identifiers and malformed payloads before business"
                        " logic executes."
                    ),
                }
            ]
        )

        input_file = Mock()
        input_file.read_text.return_value = "Build the endpoint."

        with patch(
            "agentic_learning.task_decomposer_workflow.nodes.INPUT_FILE_PATH",
            input_file,
        ), patch(
            "agentic_learning.task_decomposer_workflow.nodes.get_task_decomposer_draft_agent",
            return_value=agent,
        ), patch(
            "agentic_learning.task_decomposer_workflow.nodes.analyze_task_unknowns",
            unknown_tool,
        ), patch(
            "agentic_learning.task_decomposer_workflow.nodes.analyze_task_risks",
            risk_tool,
        ):
            result = task_decomposer_graph.invoke({})

        self.assertFalse(result["used_fallback"])
        self.assertEqual(result["prompt"], "Build the endpoint.")
        self.assertEqual(result["tool_name"], "analyze_task_risks")
        self.assertEqual(result["approval_status"], "review_required")
        self.assertEqual(result["review_reason"], "Unknown items detected.")
        self.assertEqual(result["review_summary"], "Unknown items: 1, Risks: 1")
        self.assertIsNotNone(result["structured_response"])
        self.assertIsNone(result["failure_reason"])
        self.assertEqual(result["step_outcomes"]["draft"], "ok")
        self.assertEqual(result["step_outcomes"]["unknown_analysis"], "ok")
        self.assertEqual(result["step_outcomes"]["risk_analysis"], "ok")
        self.assertEqual(result["step_outcomes"]["approval_decision"], "ok")
        self.assertEqual(result["step_outcomes"]["review"], "ok")
        agent.invoke.assert_called_once()
        unknown_tool.invoke.assert_called_once_with({"task": "Build the endpoint."})
        risk_tool.invoke.assert_called_once_with({"task": "Build the endpoint."})

    def test_compiled_graph_approved_path_reaches_expected_final_state(self) -> None:
        agent = Mock()
        agent.invoke.return_value = {"structured_response": build_draft()}
        unknown_tool = Mock()
        unknown_tool.invoke.return_value = json.dumps([])
        risk_tool = Mock()
        risk_tool.invoke.return_value = json.dumps(
            [
                {
                    "risk": "Insufficient validation",
                    "impact": "medium",
                    "mitigation": (
                        "Validate identifiers and malformed payloads before business"
                        " logic executes."
                    ),
                }
            ]
        )

        input_file = Mock()
        input_file.read_text.return_value = "Build the endpoint."

        with patch(
            "agentic_learning.task_decomposer_workflow.nodes.INPUT_FILE_PATH",
            input_file,
        ), patch(
            "agentic_learning.task_decomposer_workflow.nodes.get_task_decomposer_draft_agent",
            return_value=agent,
        ), patch(
            "agentic_learning.task_decomposer_workflow.nodes.analyze_task_unknowns",
            unknown_tool,
        ), patch(
            "agentic_learning.task_decomposer_workflow.nodes.analyze_task_risks",
            risk_tool,
        ):
            result = task_decomposer_graph.invoke({})

        self.assertFalse(result["used_fallback"])
        self.assertEqual(result["prompt"], "Build the endpoint.")
        self.assertEqual(result["tool_name"], "analyze_task_risks")
        self.assertEqual(result["approval_status"], "approved")
        self.assertIsNone(result["review_reason"])
        self.assertIsNone(result["review_summary"])
        self.assertIsNotNone(result["structured_response"])
        self.assertIsNone(result["failure_reason"])
        self.assertEqual(result["step_outcomes"]["draft"], "ok")
        self.assertEqual(result["step_outcomes"]["unknown_analysis"], "ok")
        self.assertEqual(result["step_outcomes"]["risk_analysis"], "ok")
        self.assertEqual(result["step_outcomes"]["approval_decision"], "ok")
        self.assertEqual(result["step_outcomes"]["review"], "skipped")
        agent.invoke.assert_called_once()
        unknown_tool.invoke.assert_called_once_with({"task": "Build the endpoint."})
        risk_tool.invoke.assert_called_once_with({"task": "Build the endpoint."})

    def test_compiled_graph_fallback_path_reaches_expected_final_state(self) -> None:
        agent = Mock()
        agent.invoke.return_value = {"structured_response": build_draft()}
        unknown_tool = Mock()
        unknown_tool.invoke.return_value = json.dumps([])
        risk_tool = Mock()
        risk_tool.invoke.side_effect = RuntimeError("boom")

        input_file = Mock()
        input_file.read_text.return_value = "Build the endpoint."

        with patch(
            "agentic_learning.task_decomposer_workflow.nodes.INPUT_FILE_PATH",
            input_file,
        ), patch(
            "agentic_learning.task_decomposer_workflow.nodes.get_task_decomposer_draft_agent",
            return_value=agent,
        ), patch(
            "agentic_learning.task_decomposer_workflow.nodes.analyze_task_unknowns",
            unknown_tool,
        ), patch(
            "agentic_learning.task_decomposer_workflow.nodes.analyze_task_risks",
            risk_tool,
        ):
            result = task_decomposer_graph.invoke({})

        self.assertTrue(result["used_fallback"])
        self.assertEqual(result["prompt"], "Build the endpoint.")
        self.assertEqual(result["tool_name"], "analyze_task_risks")
        self.assertEqual(result["failure_reason"], "boom")
        self.assertEqual(result["retry_count"], 2)
        self.assertIsNone(result["structured_response"])
        self.assertIsNone(result["approval_status"])
        self.assertIsNone(result["review_reason"])
        self.assertIsNone(result["review_summary"])
        self.assertEqual(result["step_outcomes"]["draft"], "ok")
        self.assertEqual(result["step_outcomes"]["unknown_analysis"], "ok")
        self.assertEqual(result["step_outcomes"]["risk_analysis"], "failed")
        self.assertEqual(result["step_outcomes"]["approval_decision"], "skipped")
        self.assertEqual(result["step_outcomes"]["review"], "skipped")
        agent.invoke.assert_called_once()
        unknown_tool.invoke.assert_called_once_with({"task": "Build the endpoint."})
        self.assertEqual(risk_tool.invoke.call_count, 2)


if __name__ == "__main__":
    unittest.main()
