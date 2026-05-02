import json

from langchain_core.tools import StructuredTool

TASK_RISK_KEYWORDS = ("endpoint", "validation", "auth", "authorization", "tests")

DEFAULT_RISK_CANDIDATES = [
    {
        "risk": "Insufficient validation",
        "impact": "high",
        "mitigation": (
            "Validate identifier format, required fields, and invalid payloads "
            "before business logic executes."
        ),
    },
    {
        "risk": "Authorization gap",
        "impact": "high",
        "mitigation": (
            "Verify ownership or role permissions before allowing the block "
            "operation and cover unauthorized paths in tests."
        ),
    },
    {
        "risk": "Inconsistent error handling",
        "impact": "medium",
        "mitigation": (
            "Use one error response shape for validation, authorization, "
            "not-found, and server failures."
        ),
    },
    {
        "risk": "Missing integration coverage",
        "impact": "medium",
        "mitigation": (
            "Add integration tests that verify state changes, persistence, and "
            "authorization behavior end to end."
        ),
    },
]


def _analyze_task_risks(task: str) -> str:
    """Return structured risk candidates for tasks that match the narrow Day 11 scope."""
    task_text = task.lower()
    risk_candidates = (
        DEFAULT_RISK_CANDIDATES
        if any(keyword in task_text for keyword in TASK_RISK_KEYWORDS)
        else []
    )
    return json.dumps(risk_candidates)


analyze_task_risks: StructuredTool = StructuredTool.from_function(
    func=_analyze_task_risks,
    name="analyze_task_risks",
    description=(
        "Return JSON risk candidates for a technical task. "
        "Each item includes risk, impact, and mitigation."
    ),
)
