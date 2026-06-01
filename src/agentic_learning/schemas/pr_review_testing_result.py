from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from agentic_learning.helpers.pr_review_helpers import (
    MediumText,
    ReviewerTesting,
    ShortText,
)

ReviewDecision = Literal["clear", "review_needed", "high_risk"]


class PrReviewTestingResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reviewer: ReviewerTesting
    focus_area: ShortText
    test_gaps: list[MediumText] = Field(default_factory=list)
    recommended_test_cases: list[MediumText] = Field(default_factory=list)
    decision: ReviewDecision

    @field_validator("test_gaps", "recommended_test_cases", mode="before")
    @classmethod
    def normalize_lists(cls, value: object) -> object:
        if isinstance(value, list):
            return [str(item).strip() for item in value]
        return value

    @field_validator("reviewer", "focus_area", "decision", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        if isinstance(value, str):
            return str(value).strip()
        return value

    @model_validator(mode="after")
    def validate_non_empty_lists(self) -> "PrReviewTestingResult":
        if self.decision != "clear" and (
            not self.test_gaps or not self.recommended_test_cases
        ):
            raise ValueError(
                "test_gaps and recommended_test_cases must be non-empty for review_needed or high_risk decisions"
            )
        return self
