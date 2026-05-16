from agentic_learning.schemas.task_decomposer_result import TaskDecomposerResult

valid_payload = {
    "original_task": "Add /api/portfolio endpoint with validation, error handling, and tests.",
    "plan_summary": "Add a narrow portfolio API slice with explicit input validation, predictable error responses, and basic automated coverage.",
    "implementation_tasks": [
        {
            "title": "Define endpoint contract",
            "description": "Define the request and response contract for the /api/portfolio endpoint before implementation begins.",
            "done_criteria": [
                "The endpoint method and route are documented.",
                "The success response shape is explicitly defined.",
                "Validation failure responses are described.",
            ],
        },
        {
            "title": "Implement request validation",
            "description": "Validate required fields and reject malformed request payloads before business logic executes.",
            "done_criteria": [
                "Missing required fields return a 400 response.",
                "Invalid field types are rejected consistently.",
                "Validation errors use a stable response shape.",
            ],
        },
    ],
    "risks": [
        {
            "risk": "Validation rules may be underspecified.",
            "impact": "high",
            "mitigation": "Define explicit validation rules and cover failure paths with focused tests.",
        },
        {
            "risk": "Error responses may leak internal details.",
            "impact": "medium",
            "mitigation": "Normalize error output and verify failure contracts in integration tests.",
        },
    ],
    "test_ideas": [
        {
            "test_type": "integration",
            "scenario": "Send a valid request to the portfolio endpoint.",
            "expected_behavior": "The endpoint returns the expected response shape with a success status.",
        },
        {
            "test_type": "integration",
            "scenario": "Send an invalid payload with missing required fields.",
            "expected_behavior": "The endpoint returns a 400 response with clear validation errors.",
        },
    ],
    "unknowns": [
        {
            "question": "What authentication rules apply to this endpoint?",
            "why_it_matters": "Authentication requirements change the contract, failure paths, and test coverage.",
        }
    ],
}

invalid_payload = {
    "original_task": "Add /api/portfolio endpoint with validation, error handling, and tests.",
    "plan_summary": "Add the endpoint with validation.",
    "implementation_tasks": [
        {
            "title": "Define route",
            "description": "Add route and document the expected contract for the endpoint.",
            "done_criteria": [
                "Return a 400 response for missing required fields.",
                "return a 400 response for missing required fields.",
            ],
        }
    ],
    "risks": [
        {"risk": "Bad validation.", "impact": "critical", "mitigation": "Fix it."}
    ],
    "test_ideas": [
        {"test_type": "ui", "scenario": "Bad case", "expected_behavior": "Fails"}
    ],
    "unknowns": [{"question": "Auth?", "why_it_matters": "Unknown."}],
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
