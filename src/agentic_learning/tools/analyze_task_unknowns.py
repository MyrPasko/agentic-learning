import json
import os

from langchain_core.tools import StructuredTool

AUTH_SIGNAL_KEYWORDS = (
    "auth",
    "authorization",
    "authentication",
    "permission",
    "permissions",
    "role",
    "roles",
    "ownership",
    "token",
    "session",
)

VALIDATION_CONTRACT_SIGNAL_KEYWORDS = (
    "validation",
    "schema",
    "payload",
    "api",
    "endpoint",
)

DEPENDENCY_SIGNAL_KEYWORDS = (
    "database",
    "cache",
    "queue",
    "webhook",
    "external service",
    "third-party",
    "migration",
    "async",
)

UNKNOWN_SIGNAL_GROUPS = (
    (
        AUTH_SIGNAL_KEYWORDS,
        {
            "question": "What authorization rule applies to this task?",
            "why_it_matters": (
                "Authorization changes the workflow, failure paths, and required "
                "test coverage."
            ),
        },
    ),
    (
        VALIDATION_CONTRACT_SIGNAL_KEYWORDS,
        {
            "question": "What validation rules and payload constraints are required?",
            "why_it_matters": (
                "Missing validation details can break the contract and produce "
                "inconsistent runtime behavior."
            ),
        },
    ),
    (
        DEPENDENCY_SIGNAL_KEYWORDS,
        {
            "question": "What external dependency or persistence constraint exists here?",
            "why_it_matters": (
                "Database, queue, cache, or third-party behavior can change the "
                "implementation plan and risk profile."
            ),
        },
    ),
)


def _analyze_task_unknowns(task: str) -> str:
    """Return up to two unknown candidates for recognized technical task signals."""
    force_failure = os.getenv("FORCE_UNKNOWN_TOOL_FAILURE")
    if force_failure == "1":
        raise RuntimeError("Forced failure for analyze_task_unknowns.")

    task_text = task.lower()
    unknown_candidates = []

    for keywords, candidate in UNKNOWN_SIGNAL_GROUPS:
        if any(keyword in task_text for keyword in keywords):
            unknown_candidates.append(candidate)
        if len(unknown_candidates) == 2:
            break

    return json.dumps(unknown_candidates)


analyze_task_unknowns: StructuredTool = StructuredTool.from_function(
    func=_analyze_task_unknowns,
    name="analyze_task_unknowns",
    description=(
        "Return JSON unknown candidates for a technical task. "
        "Each item includes a question and a reason why it matters."
    ),
)
