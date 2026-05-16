from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ShortText = Annotated[str, Field(min_length=8, max_length=120)]
MediumText = Annotated[str, Field(min_length=20, max_length=300)]
DoneCriterionText = Annotated[str, Field(min_length=12, max_length=160)]


class ImplementationTask(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: ShortText
    description: MediumText
    done_criteria: list[DoneCriterionText] = Field(min_length=1, max_length=5)

    @field_validator("title", "description", mode="before")
    @classmethod
    def normalize_text_fields(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("done_criteria", mode="before")
    @classmethod
    def normalize_done_criteria(cls, value: object) -> object:
        if isinstance(value, list):
            return [item.strip() if isinstance(item, str) else item for item in value]
        return value

    @model_validator(mode="after")
    def validate_done_criteria_uniqueness(self) -> "ImplementationTask":
        normalized_criteria = [
            criterion.strip().lower() for criterion in self.done_criteria
        ]
        if len(normalized_criteria) != len(set(normalized_criteria)):
            raise ValueError("Done criteria must be unique.")
        return self


class RiskItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk: ShortText
    impact: Literal["high", "medium", "low"]
    mitigation: MediumText

    @field_validator("risk", "mitigation", mode="before")
    @classmethod
    def normalize_text_fields(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


class TestIdea(BaseModel):
    model_config = ConfigDict(extra="forbid")

    test_type: Literal["unit", "component", "integration", "e2e"]
    scenario: ShortText
    expected_behavior: MediumText

    @field_validator("scenario", "expected_behavior", mode="before")
    @classmethod
    def normalize_text_fields(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


class UnknownItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: ShortText
    why_it_matters: MediumText

    @field_validator("question", "why_it_matters", mode="before")
    @classmethod
    def normalize_text_fields(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


class TaskDecomposerResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    original_task: MediumText
    plan_summary: MediumText
    implementation_tasks: list[ImplementationTask] = Field(min_length=1, max_length=5)
    risks: list[RiskItem] = Field(min_length=1, max_length=5)
    test_ideas: list[TestIdea] = Field(min_length=1, max_length=5)
    unknowns: list[UnknownItem] = Field(min_length=0, max_length=3)

    @field_validator("original_task", "plan_summary", mode="before")
    @classmethod
    def normalize_text_fields(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value
