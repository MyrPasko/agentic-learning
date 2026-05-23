import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from agentic_learning.schemas.task_decomposer_result import TaskDecomposerDraft

TASK_DECOMPOSER_EVAL_DATASET_PATH = (
    Path(__file__).resolve().parent / "data" / "task_decomposer_eval_dataset_v1.json"
)

ApprovalStatus = Literal["approved", "review_required"]
ReviewReason = Literal[
    "Unknown items detected.",
    "At least one risk item is high.",
]
RiskImpact = Literal["high", "medium", "low"]


class TaskDecomposerEvalQualityChecks(BaseModel):
    model_config = ConfigDict(extra="forbid")

    implementation_task_count: int = Field(ge=1, le=5)
    test_idea_count: int = Field(ge=1, le=5)
    unknown_count: int = Field(ge=0, le=2)
    risk_count: int = Field(ge=0, le=5)
    done_criteria_are_unique: bool


class TaskDecomposerEvalCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(pattern=r"^[a-z0-9-]+$")
    tags: list[str] = Field(min_length=1, max_length=4)
    input_task: str = Field(min_length=20, max_length=240)
    draft_response: TaskDecomposerDraft
    expected_unknown_questions: list[str] = Field(max_length=2)
    expected_risk_impacts: list[RiskImpact] = Field(max_length=5)
    expected_approval_status: ApprovalStatus
    expected_review_reason: ReviewReason | None
    expected_quality: TaskDecomposerEvalQualityChecks

    @model_validator(mode="after")
    def validate_internal_consistency(self) -> "TaskDecomposerEvalCase":
        if len(set(self.tags)) != len(self.tags):
            raise ValueError("tags must be unique per case.")

        if self.expected_quality.implementation_task_count != len(
            self.draft_response.implementation_tasks
        ):
            raise ValueError(
                "expected_quality.implementation_task_count must match draft_response."
            )

        if self.expected_quality.test_idea_count != len(self.draft_response.test_ideas):
            raise ValueError(
                "expected_quality.test_idea_count must match draft_response."
            )

        if self.expected_quality.unknown_count != len(self.expected_unknown_questions):
            raise ValueError(
                "expected_quality.unknown_count must match expected_unknown_questions."
            )

        if self.expected_quality.risk_count != len(self.expected_risk_impacts):
            raise ValueError(
                "expected_quality.risk_count must match expected_risk_impacts."
            )

        all_done_criteria = [
            criterion.strip().lower()
            for implementation_task in self.draft_response.implementation_tasks
            for criterion in implementation_task.done_criteria
        ]
        are_unique = len(all_done_criteria) == len(set(all_done_criteria))

        if self.expected_quality.done_criteria_are_unique != are_unique:
            raise ValueError(
                "expected_quality.done_criteria_are_unique must match the draft."
            )

        if (
            self.expected_approval_status == "approved"
            and self.expected_review_reason is not None
        ):
            raise ValueError("Approved cases must not declare a review reason.")

        if (
            self.expected_approval_status == "review_required"
            and self.expected_review_reason is None
        ):
            raise ValueError("Review-required cases must declare a review reason.")

        return self


class TaskDecomposerEvalDataset(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_name: Literal["task_decomposer_eval_dataset_v1"]
    cases: list[TaskDecomposerEvalCase] = Field(min_length=20)

    @model_validator(mode="after")
    def validate_dataset(self) -> "TaskDecomposerEvalDataset":
        case_ids = [case.case_id for case in self.cases]
        if len(case_ids) != len(set(case_ids)):
            raise ValueError("Dataset case_id values must be unique.")

        approval_statuses = {case.expected_approval_status for case in self.cases}
        if approval_statuses != {"approved", "review_required"}:
            raise ValueError("Dataset must cover both approved and review-required cases.")

        return self


def load_task_decomposer_eval_dataset(
    path: Path = TASK_DECOMPOSER_EVAL_DATASET_PATH,
) -> TaskDecomposerEvalDataset:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return TaskDecomposerEvalDataset.model_validate(payload)
