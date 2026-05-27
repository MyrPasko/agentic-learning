from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

FileName = Annotated[str, Field(min_length=1, max_length=255)]
ShortText = Annotated[str, Field(min_length=8, max_length=120)]
MediumText = Annotated[str, Field(min_length=20, max_length=300)]
ChangeType = Literal["api", "frontend", "data", "infra", "mixed", "unclear"]


class PrReviewIntakeResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pr_title: ShortText
    pr_summary: MediumText
    changed_files: list[FileName] = Field(default_factory=list, min_length=1)
    change_type: ChangeType
    review_focus: ShortText
    needs_human_review: bool

    @field_validator("pr_title", "pr_summary", "review_focus", mode="before")
    @classmethod
    def normalize_text_fields(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("changed_files", mode="before")
    @classmethod
    def normalize_changed_files(cls, value: object) -> object:
        if isinstance(value, list):
            return [str(item).strip() for item in value]
        return value
