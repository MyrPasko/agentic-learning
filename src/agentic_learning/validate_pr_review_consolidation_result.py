from agentic_learning.pr_review_consolidation_policy import (
    compute_expected_consolidation_decision,
    validate_consolidation_policy,
)
from agentic_learning.schemas.pr_review_architecture_result import (
    PrReviewArchitectureResult,
)
from agentic_learning.schemas.pr_review_consolidation_result import (
    PrConsolidationResult,
)
from agentic_learning.schemas.pr_review_risk_result import PrReviewRiskResult
from agentic_learning.schemas.pr_review_testing_result import PrReviewTestingResult

valid_clear_payload = {
    "summary": "All specialized reviewers found no meaningful follow-up issues.",
    "priority_concerns": [],
    "recommended_next_action": "Confirm the checks and proceed with merge.",
    "decision": "clear",
}

valid_review_needed_payload = {
    "summary": "Reviewer outputs indicate the change needs follow-up before merge.",
    "priority_concerns": [
        "Validation and error-path coverage remain incomplete across the reviewer outputs."
    ],
    "recommended_next_action": "Close the documented review gaps before merge.",
    "decision": "review_needed",
}

invalid_clear_with_concerns_payload = {
    "summary": "All specialized reviewers found no meaningful follow-up issues.",
    "priority_concerns": [
        "This concern should not exist when the overall decision is clear."
    ],
    "recommended_next_action": "Confirm the checks and proceed with merge.",
    "decision": "clear",
}

invalid_review_needed_without_concerns_payload = {
    "summary": "Reviewer outputs indicate the change needs follow-up before merge.",
    "priority_concerns": [],
    "recommended_next_action": "Close the documented review gaps before merge.",
    "decision": "review_needed",
}


def build_architecture_result(
    decision: str = "clear",
) -> PrReviewArchitectureResult:
    payload = {
        "reviewer": "architecture",
        "focus_area": "Service boundary clarity",
        "architecture_concerns": [],
        "recommended_checks": [],
        "decision": decision,
    }
    if decision != "clear":
        payload["architecture_concerns"] = [
            "The API boundary needs follow-up review for contract safety."
        ]
        payload["recommended_checks"] = [
            "Inspect the contract boundary and error-handling flow."
        ]
    return PrReviewArchitectureResult.model_validate(payload)


def build_testing_result(
    decision: str = "clear",
) -> PrReviewTestingResult:
    payload = {
        "reviewer": "testing",
        "focus_area": "Regression coverage depth",
        "test_gaps": [],
        "recommended_test_cases": [],
        "decision": decision,
    }
    if decision != "clear":
        payload["test_gaps"] = [
            "Regression coverage for invalid inputs and error paths is incomplete."
        ]
        payload["recommended_test_cases"] = [
            "Add tests for invalid input handling and stable error responses."
        ]
    return PrReviewTestingResult.model_validate(payload)


def build_risk_result(
    decision: str = "clear",
) -> PrReviewRiskResult:
    payload = {
        "reviewer": "risk",
        "focus_area": "Release safety and rollback confidence",
        "risk_signals": [],
        "recommended_mitigations": [],
        "decision": decision,
    }
    if decision != "clear":
        payload["risk_signals"] = [
            "The change has unresolved release-safety signals that need follow-up."
        ]
        payload["recommended_mitigations"] = [
            "Verify rollback safety and confirm release checks before merge."
        ]
    return PrReviewRiskResult.model_validate(payload)


def print_invalid_result(title: str, payload: dict) -> None:
    print(f"\n{title}:")
    try:
        PrConsolidationResult.model_validate(payload)
    except Exception as error:
        print("Validation failed as expected.")
        print(error)


def main() -> None:
    print("Valid clear payload:")
    valid_clear_result = PrConsolidationResult.model_validate(valid_clear_payload)
    print(valid_clear_result.model_dump_json(indent=2))

    print("\nValid review-needed payload:")
    valid_review_needed_result = PrConsolidationResult.model_validate(
        valid_review_needed_payload
    )
    print(valid_review_needed_result.model_dump_json(indent=2))

    print_invalid_result(
        "Invalid payload: clear decision with priority_concerns",
        invalid_clear_with_concerns_payload,
    )
    print_invalid_result(
        "Invalid payload: review_needed decision without priority_concerns",
        invalid_review_needed_without_concerns_payload,
    )

    clear_decision = compute_expected_consolidation_decision(
        build_architecture_result("clear"),
        build_testing_result("clear"),
        build_risk_result("clear"),
    )
    print("\nExpected policy for all-clear upstream results:")
    print(clear_decision)

    review_needed_decision = compute_expected_consolidation_decision(
        build_architecture_result("clear"),
        build_testing_result("review_needed"),
        build_risk_result("clear"),
    )
    print("\nExpected policy when one reviewer needs follow-up:")
    print(review_needed_decision)

    high_risk_decision = compute_expected_consolidation_decision(
        build_architecture_result("clear"),
        build_testing_result("review_needed"),
        build_risk_result("high_risk"),
    )
    print("\nExpected policy when one reviewer is high-risk:")
    print(high_risk_decision)

    valid_policy_result = PrConsolidationResult.model_validate(
        {
            "summary": "Reviewer outputs indicate merge should wait for follow-up work.",
            "priority_concerns": [
                "One or more reviewer outputs flagged unresolved issues before merge."
            ],
            "recommended_next_action": "Address the reviewer follow-up items before merge.",
            "decision": "review_needed",
        }
    )
    validate_consolidation_policy(
        valid_policy_result,
        build_architecture_result("clear"),
        build_testing_result("review_needed"),
        build_risk_result("clear"),
    )
    print("\nPolicy validation passed for a review-needed consolidation result.")


if __name__ == "__main__":
    main()
