from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from agentic_learning.helpers.pr_review_helpers import (
    MediumText,
    ReviewerRisk,
    ShortText,
)

ReviewDecision = Literal["clear", "review_needed", "high_risk"]


class PrReviewRiskResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reviewer: ReviewerRisk
    focus_area: ShortText
    risk_signals: list[MediumText] = Field(default_factory=list)
    recommended_mitigations: list[MediumText] = Field(default_factory=list)
    decision: ReviewDecision

    @field_validator("risk_signals", "recommended_mitigations", mode="before")
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
    def validate_non_empty_lists(self) -> "PrReviewRiskResult":
        if self.decision != "clear" and (
            not self.risk_signals or not self.recommended_mitigations
        ):
            raise ValueError(
                "risk_signals and recommended_mitigations must be non-empty for review_needed or high_risk decisions"
            )
        return self
