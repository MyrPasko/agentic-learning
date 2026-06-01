from agentic_learning.schemas.pr_review_architecture_result import (
    PrReviewArchitectureResult,
)
from agentic_learning.structured_pr_architecture_review_agent import (
    get_pr_architecture_review_agent,
)
from agentic_learning.structured_pr_review_intake_agent_call import (
    run_structured_pr_review_intake_agent,
)


def run_structured_pr_architecture_review_agent() -> PrReviewArchitectureResult:
    pr_intake_result_raw = run_structured_pr_review_intake_agent()
    pr_intake_result = pr_intake_result_raw.model_dump_json(indent=2)

    result = get_pr_architecture_review_agent().invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Review the following structured PR intake result and return only the "
                        "structured architecture-review result:\n\n"
                        f"{pr_intake_result}"
                    ),
                }
            ]
        }
    )

    structured_response = result["structured_response"]

    return PrReviewArchitectureResult.model_validate(structured_response)


def main() -> None:
    result = run_structured_pr_architecture_review_agent()
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
