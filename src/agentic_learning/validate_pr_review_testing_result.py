from agentic_learning.schemas.pr_review_testing_result import (
    PrReviewTestingResult,
)

valid_clear_payload = {
    "reviewer": "testing",
    "focus_area": "API regression coverage",
    "test_gaps": [],
    "recommended_test_cases": [],
    "decision": "clear",
}

valid_review_needed_payload = {
    "reviewer": "testing",
    "focus_area": "Backend endpoint validation paths",
    "test_gaps": [
        "The endpoint change lacks explicit regression coverage for invalid payload handling."
    ],
    "recommended_test_cases": [
        "Add an integration test covering invalid payload rejection and stable error output."
    ],
    "decision": "review_needed",
}

invalid_missing_gaps_payload = {
    "reviewer": "testing",
    "focus_area": "Backend endpoint validation paths",
    "test_gaps": [],
    "recommended_test_cases": [
        "Add an integration test covering invalid payload rejection and stable error output."
    ],
    "decision": "review_needed",
}

invalid_missing_test_cases_payload = {
    "reviewer": "testing",
    "focus_area": "Regression protection for response shape",
    "test_gaps": [
        "The response contract change may not be protected by a regression test."
    ],
    "recommended_test_cases": [],
    "decision": "high_risk",
}

invalid_reviewer_payload = {
    "reviewer": "architecture",
    "focus_area": "API regression coverage",
    "test_gaps": [],
    "recommended_test_cases": [],
    "decision": "clear",
}


def print_invalid_result(title: str, payload: dict) -> None:
    print(f"\n{title}:")
    try:
        PrReviewTestingResult.model_validate(payload)
    except Exception as error:
        print("Validation failed as expected.")
        print(error)


def main() -> None:
    print("Valid clear payload:")
    valid_clear_result = PrReviewTestingResult.model_validate(valid_clear_payload)
    print(valid_clear_result.model_dump_json(indent=2))

    print("\nValid review-needed payload:")
    valid_review_needed_result = PrReviewTestingResult.model_validate(
        valid_review_needed_payload
    )
    print(valid_review_needed_result.model_dump_json(indent=2))

    print_invalid_result(
        "Invalid payload: missing test_gaps",
        invalid_missing_gaps_payload,
    )
    print_invalid_result(
        "Invalid payload: missing recommended_test_cases",
        invalid_missing_test_cases_payload,
    )
    print_invalid_result(
        "Invalid payload: wrong reviewer",
        invalid_reviewer_payload,
    )


if __name__ == "__main__":
    main()
