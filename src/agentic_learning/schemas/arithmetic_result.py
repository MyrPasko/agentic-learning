from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator


class ArithmeticResult(BaseModel):
    operation: Literal["multiply"]
    tool_name: Literal["multiply_numbers"]
    operands: tuple[float, float]
    tool_result: float
    final_answer: float
    validation_status: Literal["validated"]
    reasoning_summary: str = Field(min_length=1, max_length=300)

    @model_validator(mode="after")  # This check launches after basic check of types
    def validate_result(self) -> Self:
        expected = self.operands[0] * self.operands[1]

        if abs(self.tool_result - expected) > 1e-9:
            raise ValueError("tool_result does not match operands")

        if abs(self.final_answer - self.tool_result) > 1e-9:
            raise ValueError("final_answer does not match tool_result")

        return self
