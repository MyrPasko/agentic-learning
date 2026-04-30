from agentic_learning.schemas.task_decomposer_result import TaskDecomposerResult

valid_payload = {
    "original_task": "Add /api/portfolio endpoint with validation, error handling, and tests.",
    "plan_summary": "Add a narrow portfolio API slice with explicit input validation, predictable error responses, and basic automated coverage.",
    "implementation_tasks": [
        "Define the /api/portfolio route and expected request/response contract.",
        "Implement request validation for required fields and invalid input types.",
        "Add endpoint logic plus explicit error handling for validation and server failures.",
        "Write integration and unit tests for success and failure paths.",
    ],
    "risks": [
        "Validation rules may be underspecified and allow malformed requests.",
        "Error responses may leak internal implementation details if not normalized.",
    ],
    "test_ideas": [
        "Verify a valid request returns the expected response shape.",
        "Verify invalid payloads return a 400 response with clear validation errors.",
        "Verify unexpected internal failures return a stable error contract.",
    ],
    "unknowns": [
        "Which HTTP method and request shape should the endpoint support?",
        "What authentication and authorization rules apply to this endpoint?",
    ],
}

invalid_payload = {
    "original_task": "Add /api/portfolio endpoint with validation, error handling, and tests.",
    "plan_summary": "Add the endpoint.",
    "implementation_tasks": ["Define the route."],
    "risks": [],
    "test_ideas": [],
    "unknowns": [],
}


def main() -> None:
    print("Valid payload:")
    valid_result = TaskDecomposerResult.model_validate(valid_payload)
    print(valid_result.model_dump_json(indent=2))

    print("\nInvalid payload:")
    try:
        TaskDecomposerResult.model_validate(invalid_payload)
    except Exception as e:
        print("Validation failed as expected.")
        print(e)


if __name__ == "__main__":
    main()
