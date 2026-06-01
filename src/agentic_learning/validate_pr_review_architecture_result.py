from agentic_learning.schemas.pr_review_architecture_result import (
    PrReviewArchitectureResult,
)

valid_clear_payload = {
    "reviewer": "architecture",
    "focus_area": "Service boundary clarity",
    "architecture_concerns": [],
    "recommended_checks": [],
    "decision": "clear",
}

valid_review_needed_payload = {
    "reviewer": "architecture",
    "focus_area": "API boundary and validation flow",
    "architecture_concerns": [
        "The endpoint contract and validation path may be coupled too tightly to the route layer."
    ],
    "recommended_checks": [
        "Check whether validation logic can stay isolated from transport concerns."
    ],
    "decision": "review_needed",
}

invalid_missing_concerns_payload = {
    "reviewer": "architecture",
    "focus_area": "API boundary and validation flow",
    "architecture_concerns": [],
    "recommended_checks": [
        "Check whether validation logic can stay isolated from transport concerns."
    ],
    "decision": "review_needed",
}

invalid_missing_checks_payload = {
    "reviewer": "architecture",
    "focus_area": "Deployment and state consistency",
    "architecture_concerns": [
        "The change may affect deployment behavior across service boundaries."
    ],
    "recommended_checks": [],
    "decision": "high_risk",
}

invalid_reviewer_payload = {
    "reviewer": "testing",
    "focus_area": "Service boundary clarity",
    "architecture_concerns": [],
    "recommended_checks": [],
    "decision": "clear",
}


def print_invalid_result(title: str, payload: dict) -> None:
    print(f"\n{title}:")
    try:
        PrReviewArchitectureResult.model_validate(payload)
    except Exception as error:
        print("Validation failed as expected.")
        print(error)


def main() -> None:
    print("Valid clear payload:")
    valid_clear_result = PrReviewArchitectureResult.model_validate(valid_clear_payload)
    print(valid_clear_result.model_dump_json(indent=2))

    print("\nValid review-needed payload:")
    valid_review_needed_result = PrReviewArchitectureResult.model_validate(
        valid_review_needed_payload
    )
    print(valid_review_needed_result.model_dump_json(indent=2))

    print_invalid_result(
        "Invalid payload: missing architecture_concerns",
        invalid_missing_concerns_payload,
    )
    print_invalid_result(
        "Invalid payload: missing recommended_checks",
        invalid_missing_checks_payload,
    )
    print_invalid_result(
        "Invalid payload: wrong reviewer",
        invalid_reviewer_payload,
    )


if __name__ == "__main__":
    main()
