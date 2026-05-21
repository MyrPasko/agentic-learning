from typing import Any

from ..state import TaskDecomposerState


def build_task_decomposer_graph_state(
    state: TaskDecomposerState | None = None, **updates: Any
) -> TaskDecomposerState:
    next_state: TaskDecomposerState = {
        "prompt": None,
        "draft_response": None,
        "structured_response": None,
        "tool_name": None,
        "failure_reason": None,
        "retry_count": 0,
        "used_fallback": False,
        "approval_status": None,
        "review_reason": None,
        "review_summary": None,
        "step_outcomes": {
            "draft": "skipped",
            "risk_analysis": "skipped",
            "approval_decision": "skipped",
            "review": "skipped",
        },
    }
    if state:
        next_state.update(state)
    next_state.update(updates)
    return next_state
