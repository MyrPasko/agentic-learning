from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from agentic_learning.helpers.pr_review_helpers import (
    MediumText,
    ReviewerArchitecture,
    ShortText,
)

ReviewDecision = Literal["clear", "review_needed", "high_risk"]


class PrReviewArchitectureResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reviewer: ReviewerArchitecture
    focus_area: ShortText
    architecture_concerns: list[MediumText] = Field(default_factory=list)
    recommended_checks: list[MediumText] = Field(default_factory=list)
    decision: ReviewDecision

    @field_validator("architecture_concerns", "recommended_checks", mode="before")
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
    def validate_non_empty_lists(self) -> "PrReviewArchitectureResult":
        if self.decision != "clear" and (
            not self.architecture_concerns or not self.recommended_checks
        ):
            raise ValueError(
                "architecture_concerns and recommended_checks must be non-empty for review_needed or high_risk decisions"
            )
        return self
