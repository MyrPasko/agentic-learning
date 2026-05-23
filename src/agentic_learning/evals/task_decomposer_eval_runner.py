import json
from collections import Counter
from pathlib import Path
from unittest.mock import patch

from agentic_learning.evals.task_decomposer_eval_dataset import (
    TaskDecomposerEvalCase,
    load_task_decomposer_eval_dataset,
)
from agentic_learning.schemas.task_decomposer_result import TaskDecomposerDraft
from agentic_learning.task_decomposer_graph import task_decomposer_graph

REPO_ROOT = Path(__file__).resolve().parents[3]
TASK_DECOMPOSER_EVAL_SUMMARY_PATH = (
    REPO_ROOT / "artifacts" / "evals" / "task_decomposer_eval_summary_v1.json"
)


class StubDraftAgent:
    def __init__(self, draft_response: TaskDecomposerDraft) -> None:
        self._draft_response = draft_response

    def invoke(self, _: object) -> dict[str, TaskDecomposerDraft]:
        return {"structured_response": self._draft_response}


class StubTool:
    def __init__(self, payload: str) -> None:
        self._payload = payload

    def invoke(self, _: object) -> str:
        return self._payload


UNKNOWN_REASON_BY_QUESTION = {
    "What authorization rule applies to this task?": (
        "Authorization changes the workflow, failure paths, and required test coverage."
    ),
    "What validation rules and payload constraints are required?": (
        "Missing validation details can break the contract and produce inconsistent runtime behavior."
    ),
    "What external dependency or persistence constraint exists here?": (
        "Database, queue, cache, or third-party behavior can change the implementation plan and risk profile."
    ),
}


def build_done_criteria_are_unique(draft_response: TaskDecomposerDraft) -> bool:
    normalized_done_criteria = [
        criterion.strip().lower()
        for implementation_task in draft_response.implementation_tasks
        for criterion in implementation_task.done_criteria
    ]
    return len(normalized_done_criteria) == len(set(normalized_done_criteria))


def build_check(name: str, expected: object, actual: object) -> dict[str, object]:
    return {
        "name": name,
        "expected": expected,
        "actual": actual,
        "passed": expected == actual,
    }


def build_unknown_tool_payload(case: TaskDecomposerEvalCase) -> str:
    payload = [
        {
            "question": question,
            "why_it_matters": UNKNOWN_REASON_BY_QUESTION[question],
        }
        for question in case.expected_unknown_questions
    ]
    return json.dumps(payload)


def build_risk_tool_payload(case: TaskDecomposerEvalCase) -> str:
    payload = [
        {
            "risk": f"Eval risk candidate {index + 1}",
            "impact": impact,
            "mitigation": (
                f"Use focused contract checks and narrow verification for eval case {case.case_id}."
            ),
        }
        for index, impact in enumerate(case.expected_risk_impacts)
    ]
    return json.dumps(payload)


def run_task_decomposer_eval_case(
    case: TaskDecomposerEvalCase,
) -> dict[str, object]:
    stub_agent = StubDraftAgent(case.draft_response)
    stub_unknown_tool = StubTool(build_unknown_tool_payload(case))
    stub_risk_tool = StubTool(build_risk_tool_payload(case))

    with patch("pathlib.Path.read_text", return_value=case.input_task), patch(
        "agentic_learning.task_decomposer_workflow.nodes.get_task_decomposer_draft_agent",
        return_value=stub_agent,
    ), patch(
        "agentic_learning.task_decomposer_workflow.nodes.analyze_task_unknowns",
        stub_unknown_tool,
    ), patch(
        "agentic_learning.task_decomposer_workflow.nodes.analyze_task_risks",
        stub_risk_tool,
    ):
        result = task_decomposer_graph.invoke({})

    structured_response = result.get("structured_response")
    if structured_response is None:
        raise RuntimeError(f"{case.case_id} did not produce a structured response.")

    actual_unknown_questions = [
        unknown_item.question for unknown_item in structured_response.unknowns
    ]
    actual_risk_impacts = [risk_item.impact for risk_item in structured_response.risks]
    actual_quality = {
        "implementation_task_count": len(structured_response.implementation_tasks),
        "test_idea_count": len(structured_response.test_ideas),
        "unknown_count": len(structured_response.unknowns),
        "risk_count": len(structured_response.risks),
        "done_criteria_are_unique": build_done_criteria_are_unique(
            case.draft_response
        ),
    }
    expected_review_step = (
        "ok" if case.expected_approval_status == "review_required" else "skipped"
    )

    checks = [
        build_check(
            "approval_status",
            case.expected_approval_status,
            result.get("approval_status"),
        ),
        build_check(
            "review_reason",
            case.expected_review_reason,
            result.get("review_reason"),
        ),
        build_check(
            "unknown_questions",
            case.expected_unknown_questions,
            actual_unknown_questions,
        ),
        build_check("risk_impacts", case.expected_risk_impacts, actual_risk_impacts),
        build_check(
            "implementation_task_count",
            case.expected_quality.implementation_task_count,
            actual_quality["implementation_task_count"],
        ),
        build_check(
            "test_idea_count",
            case.expected_quality.test_idea_count,
            actual_quality["test_idea_count"],
        ),
        build_check(
            "unknown_count",
            case.expected_quality.unknown_count,
            actual_quality["unknown_count"],
        ),
        build_check(
            "risk_count",
            case.expected_quality.risk_count,
            actual_quality["risk_count"],
        ),
        build_check(
            "done_criteria_are_unique",
            case.expected_quality.done_criteria_are_unique,
            actual_quality["done_criteria_are_unique"],
        ),
        build_check("used_fallback", False, result.get("used_fallback", False)),
        build_check("draft_step", "ok", result.get("step_outcomes", {}).get("draft")),
        build_check(
            "unknown_analysis_step",
            "ok",
            result.get("step_outcomes", {}).get("unknown_analysis"),
        ),
        build_check(
            "risk_analysis_step",
            "ok",
            result.get("step_outcomes", {}).get("risk_analysis"),
        ),
        build_check(
            "approval_decision_step",
            "ok",
            result.get("step_outcomes", {}).get("approval_decision"),
        ),
        build_check(
            "review_step",
            expected_review_step,
            result.get("step_outcomes", {}).get("review"),
        ),
    ]

    failed_checks = [
        check["name"] for check in checks if not bool(check["passed"])
    ]

    return {
        "case_id": case.case_id,
        "tags": case.tags,
        "passed": not failed_checks,
        "failed_checks": failed_checks,
        "approval_status": result.get("approval_status"),
        "review_reason": result.get("review_reason"),
        "checks": checks,
    }


def run_task_decomposer_eval_suite() -> dict[str, object]:
    dataset = load_task_decomposer_eval_dataset()
    case_results = [
        run_task_decomposer_eval_case(case) for case in dataset.cases
    ]
    passed_cases = sum(1 for case_result in case_results if case_result["passed"])
    failed_case_ids = [
        case_result["case_id"]
        for case_result in case_results
        if not case_result["passed"]
    ]
    approval_breakdown = Counter(
        str(case_result["approval_status"]) for case_result in case_results
    )
    tag_breakdown = Counter(
        tag for case_result in case_results for tag in case_result["tags"]
    )

    return {
        "summary_name": "task_decomposer_eval_summary_v1",
        "dataset_name": dataset.dataset_name,
        "total_cases": len(case_results),
        "passed_cases": passed_cases,
        "failed_cases": len(case_results) - passed_cases,
        "failed_case_ids": failed_case_ids,
        "approval_breakdown": dict(sorted(approval_breakdown.items())),
        "tag_breakdown": dict(sorted(tag_breakdown.items())),
        "case_results": case_results,
    }


def write_task_decomposer_eval_summary(
    path: Path = TASK_DECOMPOSER_EVAL_SUMMARY_PATH,
) -> dict[str, object]:
    summary = run_task_decomposer_eval_suite()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{json.dumps(summary, indent=2)}\n", encoding="utf-8")
    return summary
