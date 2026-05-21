from agentic_learning.task_decomposer_workflow.state import (
    MAX_RETRY_COUNT,
    RouteAfterApprovalDecision,
    RouteAfterDraft,
    RouteAfterRiskAnalysis,
    TaskDecomposerState,
)


def route_after_draft(
    state: TaskDecomposerState,
) -> RouteAfterDraft:
    failure_reason = state.get("failure_reason")
    retry_count = state.get("retry_count", 0)

    if not failure_reason:
        return "run_risk_analysis"

    if retry_count <= MAX_RETRY_COUNT:
        return "retry"

    return "fallback"


def route_after_risk_analysis(
    state: TaskDecomposerState,
) -> RouteAfterRiskAnalysis:
    failure_reason = state.get("failure_reason")
    retry_count = state.get("retry_count", 0)

    if not failure_reason:
        return "approval_decision"

    if retry_count <= MAX_RETRY_COUNT:
        return "retry"

    return "fallback"


def route_after_approval_decision(
    state: TaskDecomposerState,
) -> RouteAfterApprovalDecision:
    retry_count = state.get("retry_count", 0)
    failure_reason = state.get("failure_reason")
    approval_status = state.get("approval_status")

    if approval_status == "approved" and not failure_reason:
        return "done"

    if approval_status == "review_required":
        return "review"

    if retry_count <= MAX_RETRY_COUNT:
        return "retry"

    return "fallback"
