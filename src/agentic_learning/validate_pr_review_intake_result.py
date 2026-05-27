from agentic_learning.schemas.pr_review_intake_result import PrReviewIntakeResult

valid_payload = {
    "pr_title": "Add backend endpoint for portfolio summary retrieval",
    "pr_summary": "Add a read-only portfolio summary endpoint with query validation, service-layer data access, and stable API success and validation-error contracts.",
    "changed_files": [
        "src/routes/portfolio.ts",
        "src/services/portfolioService.ts",
        "src/validators/portfolioValidator.ts",
        "tests/portfolio.test.ts",
    ],
    "change_type": "api",
    "review_focus": "API contract, validation, and test coverage",
    "needs_human_review": True,
}

invalid_payload = {
    "pr_title": "Portfolio",
    "pr_summary": "Add endpoint.",
    "changed_files": [],
    "change_type": "backend",
    "review_focus": "Check it",
    "needs_human_review": "yes",
}


def main() -> None:
    print("Valid payload:")
    valid_result = PrReviewIntakeResult.model_validate(valid_payload)
    print(valid_result.model_dump_json(indent=2))

    print("\nInvalid payload:")
    try:
        PrReviewIntakeResult.model_validate(invalid_payload)
    except Exception as error:
        print("Validation failed as expected.")
        print(error)


if __name__ == "__main__":
    main()
