from agentic_learning.schemas.task_decomposer_result import (
    RiskItem,
    TaskDecomposerResult,
    UnknownItem,
)
from agentic_learning.task_decomposer_workflow.state import ApprovalStatus, ReviewReason


def retrieve_unknowns_and_risks(
    structured_response: TaskDecomposerResult,
) -> tuple[list[UnknownItem], list[RiskItem]]:
    unknown_items = getattr(structured_response, "unknowns", [])
    risk_items = getattr(structured_response, "risks", [])
    return unknown_items, risk_items


def need_for_approval(
    structured_response: TaskDecomposerResult,
) -> tuple[ApprovalStatus, ReviewReason]:
    unknown_items, risk_items = retrieve_unknowns_and_risks(structured_response)
    has_unknowns = len(unknown_items) > 0
    has_high_risk = any(risk.impact == "high" for risk in risk_items)

    if has_unknowns:
        return "review_required", "Unknown items detected."

    if has_high_risk:
        return "review_required", "At least one risk item is high."

    return "approved", None


def build_review_summary(structured_response: TaskDecomposerResult) -> str:
    unknown_items, risk_items = retrieve_unknowns_and_risks(structured_response)
    return f"Unknown items: {len(unknown_items)}, Risks: {len(risk_items)}"
