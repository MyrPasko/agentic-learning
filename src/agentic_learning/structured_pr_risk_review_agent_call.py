from agentic_learning.schemas.pr_review_risk_result import PrReviewRiskResult
from agentic_learning.structured_pr_review_intake_agent_call import (
    get_validated_structured_pr_review_intake_response,
)
from agentic_learning.structured_pr_risk_review_agent import (
    get_pr_risk_review_agent,
)


def run_structured_pr_risk_review_agent(intake_result: str) -> PrReviewRiskResult:
    result = get_pr_risk_review_agent().invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Review the following structured PR intake result and return only the "
                        "structured risk-review result:\n\n"
                        f"{intake_result}"
                    ),
                }
            ]
        }
    )

    structured_response = result["structured_response"]

    return PrReviewRiskResult.model_validate(structured_response)


def get_validated_structured_pr_risk_review_response(intake_result: str) -> str:
    result = run_structured_pr_risk_review_agent(intake_result)
    return result.model_dump_json(indent=2)


def main() -> None:
    intake_result = get_validated_structured_pr_review_intake_response()
    result = get_validated_structured_pr_risk_review_response(intake_result)
    print(result)


if __name__ == "__main__":
    main()
