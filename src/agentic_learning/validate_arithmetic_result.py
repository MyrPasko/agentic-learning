from pydantic import ValidationError

from agentic_learning.schemas.arithmetic_result import ArithmeticResult

valid_payload = {
    "operation": "multiply",
    "tool_name": "multiply_numbers",
    "operands": (137.42, 58.09),
    "tool_result": 7982.7278,
    "final_answer": 7982.7278,
    "validation_status": "validated",
    "reasoning_summary": "Used the multiply_numbers tool to compute the product.",
}

invalid_payload = {
    "operation": "multiply",
    "tool_name": "multiply_numbers",
    "operands": (137.42, 58.09),
    "tool_result": 7000.0,
    "final_answer": 7000.0,
    "validation_status": "validated",
    "reasoning_summary": "Used the multiply_numbers tool to compute the product.",
}


def main() -> None:
    print("Valid payload:")
    valid_result = ArithmeticResult.model_validate(valid_payload)
    print(valid_result.model_dump_json(indent=2))

    print("\nInvalid payload:")
    try:
        ArithmeticResult.model_validate(invalid_payload)
    except ValidationError as error:
        print("Validation failed as expected.")
        print(error)


if __name__ == "__main__":
    main()
