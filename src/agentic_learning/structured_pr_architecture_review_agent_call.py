from agentic_learning.schemas.pr_review_architecture_result import (
    PrReviewArchitectureResult,
)
from agentic_learning.structured_pr_architecture_review_agent import (
    get_pr_architecture_review_agent,
)
from agentic_learning.structured_pr_review_intake_agent_call import (
    get_validated_structured_pr_review_intake_response,
)


def run_structured_pr_architecture_review_agent(
    intake_result: str,
) -> PrReviewArchitectureResult:
    result = get_pr_architecture_review_agent().invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Review the following structured PR intake result and return only the "
                        "structured architecture-review result:\n\n"
                        f"{intake_result}"
                    ),
                }
            ]
        }
    )

    structured_response = result["structured_response"]

    return PrReviewArchitectureResult.model_validate(structured_response)


def get_validated_structured_pr_architecture_review_response(intake_result: str) -> str:
    result = run_structured_pr_architecture_review_agent(intake_result)
    return result.model_dump_json(indent=2)


def main() -> None:
    intake_result = get_validated_structured_pr_review_intake_response()
    result = get_validated_structured_pr_architecture_review_response(intake_result)
    print(result)


if __name__ == "__main__":
    main()
