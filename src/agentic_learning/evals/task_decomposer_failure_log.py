from pathlib import Path

from agentic_learning.evals.task_decomposer_eval_runner import (
    TASK_DECOMPOSER_EVAL_SUMMARY_PATH,
    write_task_decomposer_eval_summary,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
TASK_DECOMPOSER_FAILURE_LOG_PATH = (
    REPO_ROOT / "artifacts" / "evals" / "task_decomposer_failure_log_v1.md"
)
TASK_DECOMPOSER_EVAL_NOTE_PATH = (
    REPO_ROOT / "artifacts" / "evals" / "task_decomposer_eval_note_v1.md"
)


def collect_case_ids_by_summary_field(
    summary: dict[str, object],
    *,
    field_name: str,
    expected_value: str | None,
) -> list[str]:
    case_results = summary["case_results"]
    return [
        case_result["case_id"]
        for case_result in case_results
        if case_result[field_name] == expected_value
    ]


def collect_case_ids_by_tag(summary: dict[str, object], tag: str) -> list[str]:
    case_results = summary["case_results"]
    return [
        case_result["case_id"]
        for case_result in case_results
        if tag in case_result["tags"]
    ]


def format_case_id_list(case_ids: list[str]) -> str:
    return ", ".join(case_ids) if case_ids else "None"


def build_task_decomposer_failure_log(summary: dict[str, object]) -> str:
    approved_case_ids = collect_case_ids_by_summary_field(
        summary,
        field_name="approval_status",
        expected_value="approved",
    )
    unknown_review_case_ids = collect_case_ids_by_summary_field(
        summary,
        field_name="review_reason",
        expected_value="Unknown items detected.",
    )
    high_risk_review_case_ids = collect_case_ids_by_summary_field(
        summary,
        field_name="review_reason",
        expected_value="At least one risk item is high.",
    )
    auth_case_ids = collect_case_ids_by_tag(summary, "auth")
    validation_case_ids = collect_case_ids_by_tag(summary, "validation")
    dependency_case_ids = collect_case_ids_by_tag(summary, "dependency")
    risk_only_case_ids = collect_case_ids_by_tag(summary, "risk-only")

    return "\n".join(
        [
            "# Task Decomposer Failure Log v1",
            "",
            f"- Source summary: `{TASK_DECOMPOSER_EVAL_SUMMARY_PATH}`",
            f"- Total eval cases: {summary['total_cases']}",
            f"- Passed cases: {summary['passed_cases']}",
            f"- Observed eval mismatches: {summary['failed_cases']}",
            "- Important nuance: `review_required` is an expected guarded workflow outcome here, not an eval regression by itself.",
            "",
            "## Current Outcome Buckets",
            "",
            f"- Approved path ({len(approved_case_ids)}): {format_case_id_list(approved_case_ids)}",
            f"- Review-required because of unknowns ({len(unknown_review_case_ids)}): {format_case_id_list(unknown_review_case_ids)}",
            f"- Review-required because of high risk ({len(high_risk_review_case_ids)}): {format_case_id_list(high_risk_review_case_ids)}",
            "",
            "## Current Failure Taxonomy Inputs",
            "",
            f"- Authorization-rule uncertainty ({len(auth_case_ids)}): {format_case_id_list(auth_case_ids)}",
            f"- Validation or contract uncertainty ({len(validation_case_ids)}): {format_case_id_list(validation_case_ids)}",
            f"- Dependency or persistence uncertainty ({len(dependency_case_ids)}): {format_case_id_list(dependency_case_ids)}",
            f"- High-risk but no unknowns ({len(risk_only_case_ids)}): {format_case_id_list(risk_only_case_ids)}",
            "",
            "## What The Current Deterministic Harness Proves",
            "",
            "- The compiled graph still reaches stable `approved` and `review_required` outcomes against fixed fixtures.",
            "- Approval decisions match the dataset-provided unknown and risk signals.",
            "- Step outcomes remain explicit across draft, unknown analysis, risk analysis, approval decision, and review.",
            "- Basic structured-output quality checks remain stable: task count, test count, unknown count, risk count, and done-criteria uniqueness.",
            "",
            "## What It Does Not Prove Yet",
            "",
            "- Live model draft quality or prompt drift. The draft edge is stubbed.",
            "- Real tool heuristic quality for unknown and risk analysis. Those edges are also fixture-driven inside the eval harness.",
            "- Runtime fallback behavior inside the eval suite. The forced-failure path still lives in separate tests and demo commands.",
            "- Trace quality, latency, cost, or network sensitivity.",
            "",
            "## Next Failure-Hunting Targets",
            "",
            "- Add explicit fallback-oriented eval artifacts instead of leaving fallback proof only in separate workflow tests and demos.",
            "- Compare real unknown/risk tool heuristics against the fixture expectations so the harness stops assuming the analysis edges are correct.",
            "- Add one failure-note artifact when a future eval run produces mismatches instead of only expected review states.",
            "",
        ]
    )


def build_task_decomposer_eval_note(summary: dict[str, object]) -> str:
    unknown_review_case_ids = collect_case_ids_by_summary_field(
        summary,
        field_name="review_reason",
        expected_value="Unknown items detected.",
    )
    high_risk_review_case_ids = collect_case_ids_by_summary_field(
        summary,
        field_name="review_reason",
        expected_value="At least one risk item is high.",
    )

    return "\n".join(
        [
            "# Task Decomposer Eval Note v1",
            "",
            "## Why This Matters",
            "",
            f"- The current local eval surface runs `{summary['total_cases']}` deterministic cases through the compiled task-decomposer graph and currently passes `{summary['passed_cases']}/{summary['total_cases']}`.",
            "- This is not a toy schema check anymore. It verifies graph routing, approval decisions, review outcomes, and a narrow set of output-quality constraints.",
            "",
            "## What We Can Show",
            "",
            f"- Approved path coverage: {summary['approval_breakdown']['approved']} cases.",
            f"- Review path coverage: {summary['approval_breakdown']['review_required']} cases.",
            f"- Unknown-driven review cases: {len(unknown_review_case_ids)}.",
            f"- High-risk review cases: {len(high_risk_review_case_ids)}.",
            "- The repo contains rerunnable eval inputs, a rerunnable eval runner, a machine-readable JSON summary, and now a readable failure log.",
            "",
            "## Current Limits",
            "",
            "- The eval harness freezes draft, unknown, and risk edges with fixtures, so it demonstrates workflow control more than live inference quality.",
            "- Fallback behavior, trace review, latency, and cost still need separate evidence surfaces.",
            "",
            "## Artifacts",
            "",
            f"- Summary: `{TASK_DECOMPOSER_EVAL_SUMMARY_PATH}`",
            f"- Failure log: `{TASK_DECOMPOSER_FAILURE_LOG_PATH}`",
            f"- Note: `{TASK_DECOMPOSER_EVAL_NOTE_PATH}`",
            "",
        ]
    )


def write_task_decomposer_failure_artifacts(
    *,
    failure_log_path: Path = TASK_DECOMPOSER_FAILURE_LOG_PATH,
    eval_note_path: Path = TASK_DECOMPOSER_EVAL_NOTE_PATH,
    summary: dict[str, object] | None = None,
) -> dict[str, object]:
    current_summary = (
        write_task_decomposer_eval_summary()
        if summary is None
        else summary
    )
    failure_log_text = build_task_decomposer_failure_log(current_summary)
    eval_note_text = build_task_decomposer_eval_note(current_summary)

    failure_log_path.parent.mkdir(parents=True, exist_ok=True)
    eval_note_path.parent.mkdir(parents=True, exist_ok=True)
    failure_log_path.write_text(f"{failure_log_text}\n", encoding="utf-8")
    eval_note_path.write_text(f"{eval_note_text}\n", encoding="utf-8")

    return {
        "summary": current_summary,
        "failure_log_path": failure_log_path,
        "eval_note_path": eval_note_path,
    }
