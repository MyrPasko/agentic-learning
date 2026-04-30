from typing import Self

from pydantic import BaseModel, model_validator


class TaskDecomposerResult(BaseModel):
    original_task: str
    plan_summary: str
    implementation_tasks: list[str]
    risks: list[str]
    test_ideas: list[str]
    unknowns: list[str]

    @model_validator(mode="after")
    def validate_result(self) -> Self:

        if not self.implementation_tasks:
            raise ValueError("Implementation_tasks cannot be empty")

        if not self.test_ideas:
            raise ValueError("Test_ideas cannot be empty")

        return self
