from agentic_learning.schemas.pr_review_testing_result import (
    PrReviewTestingResult,
)
from agentic_learning.structured_pr_review_intake_agent_call import (
    get_validated_structured_pr_review_intake_response,
)
from agentic_learning.structured_pr_testing_review_agent import (
    get_pr_testing_review_agent,
)


def run_structured_pr_testing_review_agent(intake_prompt: str) -> PrReviewTestingResult:
    result = get_pr_testing_review_agent().invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Review the following structured PR intake result and return only the "
                        "structured testing-review result:\n\n"
                        f"{intake_prompt}"
                    ),
                }
            ]
        }
    )

    structured_response = result["structured_response"]

    return PrReviewTestingResult.model_validate(structured_response)


def get_validated_structured_pr_testing_review_response(intake_prompt: str) -> str:
    result = run_structured_pr_testing_review_agent(intake_prompt)
    return result.model_dump_json(indent=2)


def main() -> None:
    intake_result = get_validated_structured_pr_review_intake_response()
    result = get_validated_structured_pr_testing_review_response(intake_result)
    print(result)


if __name__ == "__main__":
    main()
