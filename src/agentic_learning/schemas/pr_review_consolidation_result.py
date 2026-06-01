from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from agentic_learning.helpers.pr_review_helpers import (
    MediumText,
    ShortText,
)

ReviewDecision = Literal["clear", "review_needed", "high_risk"]


class PrConsolidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: ShortText | MediumText
    priority_concerns: list[MediumText] = Field(default_factory=list)
    recommended_next_action: ShortText
    decision: ReviewDecision

    @field_validator("priority_concerns", mode="before")
    @classmethod
    def normalize_lists(cls, value: object) -> object:
        if isinstance(value, list):
            return [str(item).strip() for item in value]
        return value

    @field_validator("summary", "recommended_next_action", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        if isinstance(value, str):
            return str(value).strip()
        return value

    @model_validator(mode="after")
    def validate_non_empty_lists(self) -> "PrConsolidationResult":
        if self.decision == "clear" and self.priority_concerns:
            raise ValueError("priority_concerns must be empty for clear decisions")
        if self.decision != "clear" and (not self.priority_concerns):
            raise ValueError(
                "priority_concerns must be non-empty for review_needed or high_risk decisions"
            )
        return self
