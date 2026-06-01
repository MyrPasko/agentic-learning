from agentic_learning.schemas.pr_review_risk_result import PrReviewRiskResult

valid_clear_payload = {
    "reviewer": "risk",
    "focus_area": "Release safety and rollback confidence",
    "risk_signals": [],
    "recommended_mitigations": [],
    "decision": "clear",
}

valid_review_needed_payload = {
    "reviewer": "risk",
    "focus_area": "API rollout and regression exposure",
    "risk_signals": [
        "The endpoint change may alter production behavior without an explicit rollout or rollback check."
    ],
    "recommended_mitigations": [
        "Confirm rollback safety and verify unchanged clients against the updated endpoint behavior."
    ],
    "decision": "review_needed",
}

invalid_missing_risk_signals_payload = {
    "reviewer": "risk",
    "focus_area": "API rollout and regression exposure",
    "risk_signals": [],
    "recommended_mitigations": [
        "Confirm rollback safety and verify unchanged clients against the updated endpoint behavior."
    ],
    "decision": "review_needed",
}

invalid_missing_mitigations_payload = {
    "reviewer": "risk",
    "focus_area": "Deployment safety and rollback confidence",
    "risk_signals": [
        "The deployment path may introduce production risk without a clear mitigation step."
    ],
    "recommended_mitigations": [],
    "decision": "high_risk",
}

invalid_reviewer_payload = {
    "reviewer": "testing",
    "focus_area": "Release safety and rollback confidence",
    "risk_signals": [],
    "recommended_mitigations": [],
    "decision": "clear",
}


def print_invalid_result(title: str, payload: dict) -> None:
    print(f"\n{title}:")
    try:
        PrReviewRiskResult.model_validate(payload)
    except Exception as error:
        print("Validation failed as expected.")
        print(error)


def main() -> None:
    print("Valid clear payload:")
    valid_clear_result = PrReviewRiskResult.model_validate(valid_clear_payload)
    print(valid_clear_result.model_dump_json(indent=2))

    print("\nValid review-needed payload:")
    valid_review_needed_result = PrReviewRiskResult.model_validate(
        valid_review_needed_payload
    )
    print(valid_review_needed_result.model_dump_json(indent=2))

    print_invalid_result(
        "Invalid payload: missing risk_signals",
        invalid_missing_risk_signals_payload,
    )
    print_invalid_result(
        "Invalid payload: missing recommended_mitigations",
        invalid_missing_mitigations_payload,
    )
    print_invalid_result(
        "Invalid payload: wrong reviewer",
        invalid_reviewer_payload,
    )


if __name__ == "__main__":
    main()
