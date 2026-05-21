from pathlib import Path
from typing import Literal, TypedDict

from agentic_learning.schemas.task_decomposer_result import (
    TaskDecomposerDraft,
    TaskDecomposerResult,
)

INPUT_FILE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "examples"
    / "input_backend_endpoint.md"
)

MAX_RETRY_COUNT = 1

ApprovalStatus = Literal["approved", "review_required"] | None
ReviewReason = str | None
RouteAfterDraft = Literal["run_risk_analysis", "retry", "fallback"]
RouteAfterRiskAnalysis = Literal["retry", "fallback", "approval_decision"]
RouteAfterApprovalDecision = Literal["done", "review", "retry", "fallback"]


class TaskDecomposerState(TypedDict, total=False):
    prompt: str | None
    draft_response: TaskDecomposerDraft | None
    structured_response: TaskDecomposerResult | None
    tool_name: str | None
    failure_reason: str | None
    retry_count: int
    used_fallback: bool
    approval_status: ApprovalStatus
    review_reason: ReviewReason
    review_summary: str | None
